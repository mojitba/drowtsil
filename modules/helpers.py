# helperss Module


substitutions = {
    "a": "@",
    "s": "$",
    "i": "1",
    "o": "0",
    "t": "7",
    "g": "9",
    "e": "3",
    "z": "2",
}


def _check_input(input_item):
    """return true if input is a string"""
    try:
        if type(int(input_item)) == int:
            return False
    except:
        return True


def upper_case(input_list):
    return [item.upper() for item in input_list]


def substitution(input_list):
    new_list = []
    for word in input_list:
        if _check_input(word):
            word_copy = word
            for char in substitutions:
                index = word.find(char)
                if index != -1:
                    word = word.replace(char, substitutions.get(char))
                    new_word = word_copy.replace(char, substitutions.get(char))
                    new_list.append(new_word)
            new_list.append(word)
    return set(new_list)


def lower_case(input_list):
    return [item.lower() for item in input_list]


def capitalize(input_list):
    return [item.capitalize() for item in input_list]


def swap_case(input_list):
    return [item.swapcase() for item in input_list]


def toggle_case(input_list, position):
    output_list = []
    for item in input_list:
        if _check_input(item):
            tempstr = ""
            try:
                tempstr += item[:position].upper()
                tempstr += item[position].lower()
                tempstr += item[position + 1 :].upper()

                output_list.append(tempstr)
            except:
                pass
    return output_list
