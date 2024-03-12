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


def add_pattern(word, pattern_dict):
    for i in pattern_dict.keys():
        if i == 0:
            word = pattern_dict.get(i) + word
        elif i == 1000:
            word = word + pattern_dict.get(i)
        else:
            word = word[:i] + pattern_dict.get(i) + word[i:]
    return word


def capitalize(input_list):
    return [item.capitalize() for item in input_list]


def _check_input(input_item):
    try:
        if type(int(input_item)) == int:
            return False
    except:
        return True


def lower_case(input_list):
    return [item.lower() for item in input_list]


def read_from_file(file_path):
    with open(file_path, "r") as f:
        inputs = f.read().splitlines()
    return inputs


def reverse(input_list):
    return [item[::-1] for item in input_list]


def swap_case(input_list):
    return [item.swapcase() for item in input_list]


def substitution(input_list):
    new_list = []
    for word in input_list:
        if _check_input(word):
            word_copy = word
            for char in substitutions:
                # find returns -1 if not found
                index = word.find(char)
                if index != -1:
                    word = word.replace(char, substitutions.get(char))
                    new_word = word_copy.replace(char, substitutions.get(char))
                    new_list.append(new_word)
            new_list.append(word)
    return set(new_list)


def toggle_case(input_list, index):
    output_list = []
    for item in input_list:
        if _check_input(item):
            tmpstr = ""
            try:
                tmpstr += item[:index].upper()
                tmpstr += item[index].lower()
                tmpstr += item[index + 1 :].upper()

                output_list.append(tmpstr)
            except:
                pass
    return output_list


def upper_case(input_list):
    return [item.upper() for item in input_list]


def write_to_file(wordlist, semaphore, file_path):
    with semaphore:
        with open(file_path, "a") as file:
            for line in wordlist:
                file.write(f"{line}\n")


# Source: https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
def printProgressBar(
    iteration,
    total,
    prefix="Progress:",
    suffix="Completed",
    decimals=1,
    length=100,
    fill="█",
    printEnd="\r",
):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} | {bar} | {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
