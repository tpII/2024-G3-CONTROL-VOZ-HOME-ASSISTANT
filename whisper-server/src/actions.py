
import unidecode

commands = {'meca': 'C_command', 'None': 'None'}
keywords = ['meca', 'dross']

def __find_any_keywords(text):
    text = unidecode.unidecode(text.lower()) # Todo en minusculas
    words = text.split()

    keyword = [words[index] for index, word in enumerate(words) if word in keywords][-1]
    print(keyword)

    if keyword:
        return keyword
    else:
        return 'None'




def set_command(text):
    keyword = __find_any_keywords(text)
    return commands[keyword]

