import re
from .accentuation import stress

jot_dict={
    "ё":"й'о", "`ё":"`о", 
    "е":"й'э", "`е":"`э", 
    "я":"й'а", "`я":"й'`а", 
    "ю":"й'у", "`ю":"`у", 

    "'ё":"'й'о", "'`ё":"'`о",
    "'е":"'й'э", "'`е":"'`э", 
    "'я":"'й'а", "'`я":"'й'`а",
    "'ю":"'й'у", "'`ю":"'`у",
    }
def jot_function_1(m):
    s=jot_dict[m.group(1)]
    return s

def jot_function_2(m):
    s=jot_dict[m.group(2)]
    return s

def jot(s):
    replace_map={
        "ё":"й'о", "`ё":"`о", 
        "е":"й'э", "`е":"`э", 
        "я":"й'а", "`я":"й'`а", 
        "ю":"й'у", "`ю":"`у", 

        "'ё":"'й'о", "'`ё":"'`о",
        "'е":"'й'э", "'`е":"'`э", 
        "'я":"'й'а", "'`я":"'й'`а",
        "'ю":"'й'у", "'`ю":"'`у",
        }
    # в начале слова
    # for letter in replace_map:
    #     s = re.sub(r"( |\n|^)`?()", jot_function_2, s)
    # s = re.sub(r"\n([еёюя])", jot_function, s)
    # s = re.sub(r"^([еёюя])", jot_function, s)
    # после гласной буквы 
    s = re.sub(r"[аяиыуюеёо]([еёюя])", jot_function_1, s)
    # или твердого и мягкого знака
    s = re.sub(r"('[еёюя])|ъ([еёюя])", jot_function_1, s)
    return s


def deafen_and_sharpen(s):
    sharpening_map={"к":"г", "т":"д", "п":"б", "с":"з", "ш":"ж", "ф":"в"}
    deafening_map={"г":"к", "д":"т", "б":"п", "з":"с", "ж":"ш", "в":"ф"}

    sharp_sounds="бгвдзжмнл"
    deaf_sounds="пкфтсшщхцч"

    s = re.sub("гк", "хк", s)

    for k in "бгвдзж":
        s=re.sub(k + rf"([{deaf_sounds}])", deafening_map[k] + r'\1', s)

    for sharp_sound in deafening_map:
        # оглушение в конце слов
        s=re.sub(rf"([а-я]+){sharp_sound}([^а-яё`'])", r'\1' + deafening_map[sharp_sound] + r'\2',s)
        # оглушение в конце текста
        s=re.sub(rf"{sharp_sound}$", deafening_map[sharp_sound],s)
    
    # for k in "пкфтсш":
    #     s=re.sub(k + rf"ь([{sharp_sounds}])", sharpening_map[k] + "'" + r'\1',s)
    #     s=re.sub(k + rf"([{sharp_sounds}])", sharpening_map[k] + r'\1',s)

    s = re.sub(rf"в ([{deaf_sounds}])", "ф " + r'\1', s)
    s = re.sub(r"с ([бгдзжмнл])", "з " + r'\1', s)

    return s

def soften_vowels(s):
    always_softening_vowels="яёюеиь"
    vowels_map={
        "я":"'а", "`я":"'`а", 
        "ё":"'о", "`ё":"'`о",
        "ю":"'у", "`ю":"'`у", 
        "е":"'э", "`е":"'`э",
        "и":"'и", "`и":"'`и", 
        "ь":"'"
    }
    def soften_function(m):
        item=vowels_map[m.group(1)]
        return m.group()[0] + item

    not_always_hard_consonants="бвгдзклмнпрстфхчщ"

    for consonant in not_always_hard_consonants:
        s=re.sub(consonant+r"(`*[" + always_softening_vowels + r'])', soften_function, s)
    return s

def soften_consonants(s):
    # Твердый [н] может меняться на мягкий [н’] в сочетаниях [н’ч’], [н’щ’].
    s = re.sub(rf"н([чщ])", "н'" + r"\1", s)

    #Твердые  [д], [т], [з], [с], [н] могут смягчаться перед мягкими [д’], [т’], [з’], [с’], [н’].
    s = re.sub(rf"([дтзсн])(д'|т'|з'|с'|н')", r"\1" + "'" + r"\2", s)

    always_soft_consonants="чщ"
    for consonant in always_soft_consonants:
        s = re.sub(rf"{consonant}([^'])", consonant+ "'" + r'\1', s)
    return s

def soften(s):
    s = soften_vowels(s)
    s = soften_consonants(s)
    return s

def accentuate(s):
    s = stress.accentuate(s).lower()
    #s = re.sub(r"(^[^ауоиэыеёюя`]*)[о]([^ауоиэыеёюя]*)", r'\1' + "а" + r'\2', s)
    return s

def remove_hard_sign(s):
    # функция удаляет Ъ из транскрипций
    return re.sub("ъ", "", s)

def simplify_transcription(s):
    result = re.findall(r"`[аеёиоуыэюя]|[бвгджзклмнпрстфхцчшщ' \n]", s)
    s = "".join(result)
    s = re.sub("`", "", s)
    s = re.sub("(')+", "'", s)
    return s

def tsya(s):
    result = re.sub(r"ться|тся", "ца", s)
    return result

def ego(s):
    #По правилам звуко буквенного анализа в окончаниях «-ого», «-его» имён прилагательных, причастий и местоимений согласный «Г» транскрибируется как звук [в]: красного [кра´снава], синего [с’и´н’ива], белого [б’э´лава], острого, полного, прежнего, того, этого, кого.
    s = re.sub(r"([^`])его\b", r"\1" + "ива", s)
    s = re.sub(r"([^`])ого\b", r"\1" + "ава", s)
    return s
    
def transcribe(s, simplify=False, verbose=False):
    s = accentuate(s)
    if verbose:
        print("accentuate:")
        print(s)
        print("\n")
    s = tsya(s)
    if verbose:
        print("tsya:")
        print(s)
        print("\n")

    s = ego(s)
    if verbose:
        print("ego:")
        print(s)
        print("\n")

    s = soften(s)
    if verbose:
        print("soften:")
        print(s)
        print("\n")

    s = jot(s)
    if verbose:
        print("jot:")
        print(s)
        print("\n")

    s = deafen_and_sharpen(s)
    if verbose:
        print("deafen&sharpen:")
        print(s)
        print("\n")

    s = remove_hard_sign(s)
    if verbose:
        print("hard sign:")
        print(s)
        print("\n")
    if simplify:
        s = simplify_transcription(s)
        if verbose:
            print("simplify:")
            print(s)
            print("\n")
    s = re.sub("^ ","",s)
    s = re.sub("\n ","\n",s)
    s = re.sub("[^\S\r\n]+"," ",s)

    return s

# if __name__=='__main__':
#     s = "У лукоморья дуб зелёный;\nЗлатая цепь на дубе том:\nИ днём и ночью кот учёный\nВсё ходит по цепи кругом"
#     #s = "Объемлет ужас печенегов;\nПитомцы бурные набегов\nЗовут рассеянных коней,\nПротивиться не смеют боле"
#     print(transcribe(s, True))