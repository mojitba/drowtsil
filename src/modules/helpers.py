#!/usr/bin/env python3
"""Helpers module contains functions that used to transform words and write generated wordlist to file

Program:
    Drowtsil(reverse of word list)-v1.0 - Another wordlist generator for ethical penetration testing and educational purposes.

Usage:
    python drowtsil.py -h

Author:
    Mojtaba Hemmati
    github.com/mojitba 3/13/2024

License:
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

See 'LICENSE' for more information.

"""
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


def alternating_case(input_list):
    """Transform every item from input list to alternating case. In this form text alternates between lowercase and upper case.

    :param input_list: wordlist provided by the user
    :type input_list: list
    :returns: a list of alternating version of input items
    :rtype: list
    """
    alternating_list = []
    for item in input_list:
        word = ""
        for i, _ in enumerate(item):
            if i % 2 == 0:
                word += item[i].lower()
            else:
                word += item[i].upper()

        alternating_list.append(word)

    return alternating_list


def capitalize(input_list):
    """Capitalize case of every item from input list.

    :param input_list: wordlist provided by the user
    :type input_list: list
    :returns: a list of capitalized version of input items
    :rtype: list
    """
    return [item.capitalize() for item in input_list]


def _check_input(input_item):
    """cheks if input is a string litteraly or an integer as a string.

    :param input_item: input item
    :type input_item: str
    :returns: True if input is a string and False if not.
    :rtype: bool
    """
    try:
        if type(int(input_item)) == int:
            return False
    except:
        return True


def lower_case(input_list):
    """Transforms every item from input list to lower case.

    :param input_list: wordlist provided by the user
    :type input_list: list
    :returns: a list of lower case version of input items
    :rtype: list
    """
    return [item.lower() for item in input_list]


def read_from_file(file_path):
    """Reading wordlist provided by the user from file line by line.

    :param file_path: location of input file
    :type file_path: list
    :returns: None
    :rtype: None
    """
    with open(file_path, "r") as f:
        inputs = f.read().splitlines()
    return inputs


def reverse(input_list):
    """Reverse every item from input.

    :param input_word: list provided by the user
    :type input_word: str
    :returns: reverse version of input word
    :rtype: str
    """
    return [item[::-1] for item in input_list]


def swap_case(input_list):
    """Transforms every item from input list to swap case (upper to lower and vice versa).

    :param input_list: wordlist provided by the user
    :type input_list: list
    :returns: a list of swap case version of input items
    :rtype: list
    """
    return [item.swapcase() for item in input_list]


def sentence_case(input_list):
    """Transform every item from input list to sentence case.
    
    It works by capitalizing the very first letter in each sentence and then transform the rest of text in lowercase.
    example: ["thisistext", "tHisIsALSOateXt"] Transforms to ['Thisistext', 'Thisisalsoatext']

    :param input_list: wordlist provided by the user
    :type input_list: list
    :returns: a list of input items in sentence case version
    :rtype: list
    """
    sentence_list = []
    for item in input_list:
        sentence_word = item[:1].capitalize()
        sentence_word += item[1:].lower()
        sentence_list.append(sentence_word)

    return sentence_list


def leet_case(input_list):
    """Transforms every item from input list to leet case(1337). 
    
    It uses substitutions dictionary to subtitute a to @, s to $ and etc.
    example: ["riCk", "moRty", "42"] Transforms to ["r1Ck", "m0Rty", "moR7y", "m0R7y"]

    :param input_list: wordlist provided by the user
    :type input_list: list
    :returns: a set of leet version of input items
    :rtype: set
    """
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
    """Transforms every item from input to toggle case with specified index. 
    
    in toggle case each word begins in lower case and the rest in upper case. 
    example: toggle_case(input_list = ["rick"], index=0) returns ["rICK"]

    :param input_list: wordlist provided by the user
    :type input_list: list
    :param index: index of string which Transforms to lower case
    :type index: int
    :returns: a list of toggle case version of input items
    :rtype: list
    """
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
    """Transforms every item from input to upper case.

    :param input_list: wordlist provided by the user
    :type input_list: list
    :returns: a list of upper case version of input items
    :rtype: list
    """
    return [item.upper() for item in input_list]


def write_to_file(wordlist, semaphore, file_path):
    """Write generated wordlist to file.

    :param wordlist: wordlist to write on disk
    :type wordlist: list
    :param semaphore: semaphore for prevent of mutual exclusion (default is 1)
    :type semaphore: multiprocessing.synchronize.Semaphore
    :param file_path: location of output file
    :type file_path: str
    :returns: None
    :rtype: None
    """
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
    """Call in a loop to create terminal progress bar.
    :param iteration: current iteration (Required)
    :type iteration: int
    :param total: total iterations (Required)
    :type total: int
    :param prefix: prefix string (Optional)
    :type prefix: str
    :param suffix: suffix string (Optional)
    :type suffix: str
    :param decimals: positive number of decimals in percent complete (Optional)
    :type decimals: int
    :param length: character length of bar (Optional)
    :type length: int
    :param fill: bar fill character (Optional)
    :type fill: str
    :param printEnd: end character (e.g. '\r', '\r\n') (Optional)
    :type printEnd: str
    :returns: None
    :rtype: str
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} | {bar} | {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
