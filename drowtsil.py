"""This script allows the user to create wordlist for targeted subject. Use only for security audit, penetration testing and education purposes.

This tool accepts two list in form of text file (.txt) or from command line and returns a wordlist in (.txt) format.

Program:
    Drowtsil(reverse of word list)-v1.0 - Another wordlist generator for penetration testing and education purposes

Usage:
    python drowtsil.py -h

Author:
    Mojtaba Hemmati
    github.com/moji1tba 3/21/2024

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
from timeit import default_timer
import argparse
from pathlib import Path
from itertools import permutations
import re
from errno import ENOSPC
from multiprocessing import (
    cpu_count,
    Pool,
    get_all_start_methods,
    set_start_method,
    Semaphore,
)

from src.modules import helpers

logo = """
    ____                     __       _ __
   / __ \_________ _      __/ /______(_) /
  / / / / ___/ __ \ | /| / / __/ ___/ / / 
 / /_/ / /  / /_/ / |/ |/ / /_(__  ) / /  
/_____/_/   \____/|__/|__/\__/____/_/_/   
                                                                                                                                             
 Wordlist Generator for Security Audit
                 V.1
"""


def _create_parser(process_number_default):
    """Create and return a parser (argparse.ArgumentParser instance) for main() function.

    :param process_number_default: default value for the number of processes (compute with multiprocessing.cpu_count())
    :type input_list: int
    :returns: an instance from argparse.ArgumentParser class contains switches with their values.
    :rtype: <class 'argparse.ArgumentParser'>
    """

    parser = argparse.ArgumentParser(
        description="Another Wordlist Generator for Security Audit Purposes",
        prog="Drowtsil WordList Generator",
        epilog="Thanks for using %(prog)s!",
    )
    #user's provided paths or words
    parser.add_argument(
        "-i", "--input", type=str, nargs="+", help="List of constant input words"
    )
    parser.add_argument(
        "-ti",
        "--tmpinp",
        type=str,
        nargs="+",
        default=None,
        help="List of temporary input words, every time each one is\n\t selected and added to constant words list",
    )
    parser.add_argument(
        "-f", "--filename", type=str, help="Path to constant Wordlist file"
    )
    parser.add_argument(
        "-ft",
        "--tmpfile",
        type=str,
        default=None,
        help="Path to temporary Wordlist file, every time each one selected\n\t and added to constant words list",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./output.txt",
        help="Path of generated wordlist (default is \"./output.txt\")",
    )
    #user's prefer options
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        default=1,
        choices=[0, 1, 2, 3],
        help="Level of operation (0,1,2,3) (default is 1)",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        type=str,
        nargs="+",
        default=None,
        help='Pattern of words, Enter like "pattern" "index". Example: 0 for first and 1000 for the end of word or other indexes',
    )
    parser.add_argument(
        "-r", "--regex", type=str, default=None, help="Regex to match words"
    )
    parser.add_argument(
        "-pn",
        "--pernumber",
        type=int,
        default=2,
        help="Minimum number of words to generate permutations like start with 2-word permutation (default is 2)",
    )
    parser.add_argument(
        "-ps",
        "--process",
        type=int,
        nargs="?",
        const=process_number_default,
        default=None,
        help="Number of processes in the pool (default is number of logical cores - 1)",
    )
    parser.add_argument(
        "-max", type=int, default=63, help="Maximum length of the preshared key (default is 63)"
    )
    parser.add_argument(
        "-min", type=int, default=8, help="Minimum length of the preshared key (default is 8)"
    )
    #operations options
    parser.add_argument(
        "-u", "--upper", action="store_true", help="Enable upper case function"
    )
    parser.add_argument(
        "-lo", "--lower", action="store_true", help="Enable lower case function"
    )
    parser.add_argument(
        "-c", "--capital", action="store_true", help="Enable capitalize function"
    )
    parser.add_argument(
        "-lt",
        "--leet_case",
        action="store_true",
        help="Enable leet case function, replace 'a' with '@', 's' with '$' and etc",
    )
    parser.add_argument(
        "-t",
        "--toggle",
        type=int,
        default=None,
        const=0,
        nargs="?",
        help="Enable toggle case function with index (default is 0)",
    )
    parser.add_argument(
        "-s", "--swap", action="store_true", help="Enable swap case function"
    )
    parser.add_argument(
        "-st", "--sentence", action="store_true", help="Enable sentence case function"
    )
    parser.add_argument(
        "-rv", "--reverse", action="store_true", help="Reverse every word in level 0"
    )
    parser.add_argument(
        "-a",
        "--alternating",
        action="store_true",
        help="transform text into the form that alternates between lowercase and uppercase",
    )
    parser.add_argument(
        "-all", action="store_true", help="Apply all text transform functions in levels 0 and 3"
    )
    parser.add_argument(
        "-n","--numbers", type=int, default=0, help="Add consecutive numbers at the end of strings in level 1"
    )
    parser.add_argument(
        "-ch","--chars", action="store_true", help="Add consecutive characters at the end of strings in level 1"
    )
    return parser


def create_wordlist(iter, min, max, level, capital, regexp, pattern_dict, word_counter):
    """Get an iterable object and create a wordlist with selected options 
    
    Create a wordlist by joining items from iterators in one string. every iterator contains a list of all permutations
    tuples. if a specific pattern is provided, it will be added and then passed to the private function (_add_to_wordlist). if
    the level selected by the user is 2 and the capital switch doesn't disable, capitalized words also are added to the wordlist.

    :param iter: iterable returns from itertools.permutations
    :type iter: itertools.permutations
    :param min: minimum size of word by char
    :type min: int
    :param max: maximum size of word by char
    :type max: int
    :param level: user's selected level
    :type level: int
    :param capital: enable capitalize case transformation
    :type capital: bool
    :param regexp: regex pattern to match
    :type regexp: str
    :param pattern_dict: pattern provided by the user
    :type pattern_dict: dict
    :param word_counter: tracking generated word number
    :type word_counter: int
    :returns: returns a list of generated words and their number
    :rtype: tuple
    """
    wordlist = []
    for item in iter:
        word = "".join(item)
        if pattern_dict:
            word = _add_pattern(word, pattern_dict)

        word_counter = _add_to_wordlist(wordlist, word, min, max, regexp, word_counter)
        #apply capitalize operation in level 2
        if level == 2 and capital:
            cap_word = "".join(helpers.capitalize(item))
            if pattern_dict:
                cap_word = _add_pattern(cap_word, pattern_dict)

            word_counter = _add_to_wordlist(
                wordlist, cap_word, min, max, regexp, word_counter
            )

    return wordlist, word_counter

def _add_pattern(word, pattern_dict):
    """Add the pattern provided by the user to the specified index of the word

    :param word: a word from the wordlist
    :type word: str
    :param pattern_dict: a dictionary of pattern  in shape {index:"pattern"} (index 0 for first of word, 1000 for end of word)
    :type pattern_dict: dict
    :returns: a word with an appended pattern
    :rtype: str
    """
    for i in pattern_dict.keys():
        if i == 0:
            word = pattern_dict.get(i) + word
        elif i == 1000:
            word = word + pattern_dict.get(i)
        else:
            word = word[:i] + pattern_dict.get(i) + word[i:]
    return word


def _add_to_wordlist(wordlist, word, min, max, regexp, word_counter):
    """A private function that adds a word to the wordlist.

    :param wordlist: an empty list for adding words 
    :type wordlist: list
    :param word: generated word that is going to be added to the wordlist
    :type word: str
    :param min: minimum size of word by char
    :type min: int
    :param max: maximum size of word by char
    :type max: int
    :param regexp: regex pattern to match
    :type regexp: str
    :param word_counter: tracking generated word number
    :type word_counter: int
    :returns: returns number of generated words
    :rtype: int
    """
    if len(word) >= min and len(word) <= max:
        if regexp != None:
            if re.match(regexp, word):
                wordlist.append(word)
                word_counter += 1

        else:
            wordlist.append(word)
            word_counter += 1

    return word_counter


def level_zero(args, current_words):
    """It performs when the user's selected level is 0. Get a list of words and arguments provided by the user and apply selected functions on
      all items.

    list of functions: 
      -upper case
      -lower case,
      -toggle case
      -swap case
      -capitalize case
      -leet case
      -reverse case
      -alternating case 

    :param args: arguments provide by the user
    :type args: <class '__main__.Namespace'>
    :param current_words: a merged list of constant words and temporary words
    :type current_words: list
    :returns: a tuple contains a list of transformed words and a list of operations that have been done 
    :rtype: tuple
    """
    words = []
    output_print = []
    if args.all or args.upper:
        words += helpers.upper_case(current_words)
        output_print.append("upper case")
    if args.all or args.lower:
        words += helpers.lower_case(current_words)
        output_print.append("lower case")
    if args.all or args.toggle is not None:
        if args.all and args.toggle is None:
            args.toggle = 0
        words += helpers.toggle_case(current_words, args.toggle)
        output_print.append("toggle case")
    if args.all or args.swap:
        words += helpers.swap_case(current_words)
        output_print.append("swap case")
    if args.all or args.capital:
        words += helpers.capitalize(current_words)
        output_print.append("capitalize")
    if args.all or args.leet_case:
        words += helpers.leet_case(current_words)
        output_print.append("leet_case")
    if args.all or args.reverse:
        words += helpers.reverse(current_words)
        output_print.append("reverse")
    if args.all or args.alternating:
        words += helpers.alternating_case(current_words)
        output_print.append("alternating")
    return set(words), output_print

def level_one(constant_words, temporary_words, numbers, chars):
    """It performs when the user's selected level is 1. Get a list of URLs or other texts and add consecutive numbers or letters or
    items of temporary_words at the end.
    
    :param constant_words: a list of constant words
    :type constant_words: list
    :param temporary_words: a list of temporary words
    :type temporary_words: list
    :param numbers: limit for consecutive numbers - also enable this feature
    :type numbers: int
    :param chars: enable adding consecutive characters
    :type chars: bool
    :returns: a tuple contains a list of transformed words and the length of the wordlist 
    :rtype: tuple
    """
    wordlist = []
    urls = _is_url(constant_words)
    # if input list contains urls
    if urls:
        for url in urls:
            if numbers:
                for i in range(numbers):
                    try:
                        new_url = "".join(url[0]+str(i)+url[1])
                    except IndexError:
                        new_url = "".join(url[0]+str(i))
                    wordlist.append(new_url)
            if temporary_words != "":
                for tmp_item in temporary_words:
                    try:
                        new_url = "".join(url[0]+str(tmp_item)+url[1])
                    except IndexError:
                        new_url = "".join(url[0]+str(tmp_item))
                    wordlist.append(new_url)
            if chars:
                for char_item in helpers.characters:
                    try:
                        new_url = "".join(url[0]+str(char_item)+url[1])
                    except IndexError:
                        new_url = "".join(url[0]+str(char_item))
                    wordlist.append(new_url)
    # if input list does not contain urls.
    else:
        if numbers:
            for i in range(numbers):
                for item in constant_words:
                    wordlist.append(item + str(i))
        if temporary_words != "":
            for tmp_item in temporary_words:
                for item in constant_words:
                    wordlist.append(item + tmp_item)
        if chars:
            for char_item in helpers.characters:
                for item in constant_words:
                    wordlist.append(item + char_item)
                    
    return wordlist, len(wordlist)


def _is_url(input_list):
    """It's a private function for checking if the list contains URLs or not.
    
    :param input_list: list of strings
    :type input_list: list
    :returns: a list of lists containing URLs and their suffixes.
    :rtype: list
    """
    urls = [re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', item) for item in input_list]
    try:
        result =[re.split(r"([.]{1}[a-zA-Z]+$)", item[0]) for item in urls ]
    except IndexError:
        result = []

    return result

def level_three(
    wordlist,
    args,
    output_dir,
    word_counter,
    semaphore,
    write_function,
):
    """It performs when the user's selected level is 2. Get a list of words and arguments provided by the user and apply selected functions on
      every item of the wordlist.

      list of functions: 
      -upper case
      -sentence case
      -toggle case
      -capitalize case
      -leet case
      -alternating case 

    :param wordlist: a list contains all permutations of input words
    :type wordlist: list
    :param args: arguments provided by the user
    :type args: <class '__main__.Namespace'>
    :param output_dir: path to the output directory
    :type output_dir: str
    :param word_counter: tracking generated word number
    :type word_counter: int
    :param semaphore: semaphore for prevent of mutual exclusion (default is 1)
    :type semaphore: multiprocessing.synchronize.Semaphore
    :param write_function: an instance of helpers.write_to_file function
    :type write_function: function
    :returns: returns number of generated words
    :rtype: int
    """
    write_function(wordlist, semaphore, output_dir)
    temp_wordlist = []
    if args.all or args.leet_case:
        temp_wordlist += helpers.leet_case(wordlist)
        write_function(temp_wordlist, semaphore, output_dir)
        word_counter += len(temp_wordlist)
        #clear temp wordlist to save memory
        temp_wordlist.clear()
    if args.all or args.upper:
        temp_wordlist += set(helpers.upper_case(wordlist))
        write_function(temp_wordlist, semaphore, output_dir)
        word_counter += len(temp_wordlist)
        temp_wordlist.clear()
    if args.all or args.sentence:
        temp_wordlist += set(helpers.sentence_case(wordlist))
        write_function(temp_wordlist, semaphore, output_dir)
        word_counter += len(temp_wordlist)
        temp_wordlist.clear() 
    if args.all or args.toggle is not None:
        if args.all and args.toggle is None:
            args.toggle = 0
        temp_wordlist += set(helpers.toggle_case(wordlist, index=args.toggle))
        write_function(temp_wordlist, semaphore, output_dir)
        word_counter += len(temp_wordlist)
        temp_wordlist.clear()
    if args.all or args.alternating:
        temp_wordlist += set(helpers.alternating_case(wordlist))
        write_function(temp_wordlist, semaphore, output_dir)
        word_counter += len(temp_wordlist)
        temp_wordlist.clear()
    #clear wordlist to save memory
    wordlist.clear()

    return word_counter


# private function for testing purposes
def _extract_user_input(args, parser, read_function):
    """A private function that reads input words from files and returns an appropriate message if files are not found.

    :param args: arguments provided by the user
    :type args: <class '__main__.Namespace'>
    :param parser: an instance of argparse.ArgumentParser
    :type parser: <class 'argparse.ArgumentParser'>
    :param read_function: an instance of helpers.read_from_file function
    :type read_function: function
    :returns: a tuple containing a list of constant words and a list of temporary words
    :rtype: tuple
    """
    try:
        if args.filename and args.tmpfile:
            target_cons_dir = Path(args.filename)
            target_tmp_dir = Path(args.tmpfile)
            cons_words = read_function(target_cons_dir)
            tmp_words = read_function(target_tmp_dir)

        elif args.filename and args.tmpinp:
            target_cons_dir = Path(args.filename)
            cons_words = read_function(target_cons_dir)
            tmp_words = args.tmpinp

        elif args.input and args.tmpfile:
            target_tmp_dir = Path(args.tmpfile)
            cons_words = args.input
            tmp_words = read_function(target_tmp_dir)

        elif args.input and args.tmpinp:
            cons_words = args.input
            tmp_words = args.tmpinp
        
        elif args.input and (args.level == 0 or args.level == 1):
            cons_words = args.input
            tmp_words = ""

        elif args.filename and (args.level == 0 or args.level == 1):
            target_cons_dir = Path(args.filename)
            cons_words = read_function(target_cons_dir)
            tmp_words = ""

        else:
            parser.exit(
                1,
                message="[!] ERROR: Input constant words or temporary words doesn't provide.\n",
            )
    except FileNotFoundError:
        parser.exit(
            1,
            message="[!] ERROR: Incorrectly specified path of input files. Try again!\n",
        )
    except PermissionError:
        parser.exit(
            1,
            message="[!] ERROR: Permission denied to the specified path of input files. Try again!\n",
        )
    return cons_words, tmp_words


# private function for unittesting purposes
def _extract_pattern(args):
    """A private function that creates a dictionary of patterns provided by the user.

    :param args: arguments provided by the user - example: ['pattern1', 'index1']
    :type args: <class '__main__.Namespace'>
    :returns: a dictionary of patterns {index: "pattern",}
    :rtype: dict
    """
    if args.pattern:
        pattern_dict = dict()
        for p in range(int(len(args.pattern) / 2)):
            pindex = int(args.pattern.pop())
            pstr = args.pattern.pop()
            pattern_dict[pindex] = pstr
    else:
        pattern_dict = None
    return pattern_dict


# private function for unittesting purposes
def _calculate_total(tmp_words, len_input, pernumber):
    """A private function that calculates the total number of iterations to use in helpers.printProgressBar function.

    :param tmp_words: a list of temporary words which each will be added to constant words to create a current word list
    :type tmp_words: list
    :param len_input: length of constant word list
    :type len_input: int
    :param pernumber: minimum length permutations of elements in the iterable
    :type pernumber: int
    :returns: an integer that will be passed to helpers.printProgressBar function
    :rtype: int
    """
    if tmp_words:
        total = ((len_input + 2) - pernumber) * len(tmp_words)
    else:
        total = len_input
    return total

# private function for unittesting purposes
def _checking_permutation_number(len_input, parser):
    """A private function that calculates the number of permutations for input words, to notify the user of the high volume of computation

    :param len_input: length of constant word list
    :type len_input: int
    :param parser: an instance of argparse.ArgumentParser
    :type parser: <class 'argparse.ArgumentParser'>
    :returns: None
    :rtype: None
    """
    import math
    possible_permutation = math.factorial(len_input)
    answer = input(f"Your input file contains {len_input} words with {possible_permutation} permutations. this number of permutation may require heavy computation and memory and disk resources.\n recommended try again with fewer words. Are you sure to continue? (-y for YES -n for NO - default is NO) ")
    if answer == "-n" or answer == "":
        parser.exit(
        1,
        message="[!] Try again with fewer words!\n",
    )

def main(args=None):
    """Main function to generate a wordlist

    :param args: arguments provided by the user - optional
    :type args: <class '__main__.Namespace'>
    :returns: None
    :rtype: None
    """
    #specifies start method for multiprocessing mode
    start_method = get_all_start_methods()
    set_start_method(start_method[0])
    #calculate logical cpu cores
    process_number_default = cpu_count()
    #record progress time
    start_time = default_timer()
    #assign functions for testing purpose
    write_function = helpers.write_to_file
    read_function = helpers.read_from_file
    #create argument parser
    parser = _create_parser(process_number_default)
    args = parser.parse_args()
    #extract constant and temporary lists
    cons_words, tmp_words = _extract_user_input(args, parser, read_function)
    len_input = len(cons_words)
    total = _calculate_total(tmp_words, len_input, args.pernumber)
    output_dir = Path(args.output)
    semaphore = Semaphore(1)
    iteration_number = 0
    word_counter = 0
    print_bar = helpers.printProgressBar
    pattern_dict = _extract_pattern(args)
    print(logo)

    # emptying previous output file
    mode = "w"
    with open(output_dir, mode):
        pass
    
    try:
        if args.level == 0:
                wordlist, output_print = level_zero(args, cons_words)
                write_function(wordlist, semaphore, output_dir)
                word_counter = len(wordlist)

        elif args.level == 1:
                wordlist, word_counter = level_one(cons_words, tmp_words, args.numbers, args.chars)
                write_function(wordlist, semaphore, output_dir)
        
        else:
            print_bar(iteration_number, total, length=50)

            for item in tmp_words:
                #each time initialize a list of words from the constant list and one item from the temporary list
                current_words = [item]
                current_words += cons_words
                # checking for high number of permutations
                if len_input+1 >= 12:
                    _checking_permutation_number(len_input, parser)
                #calculate permutation without multiprocessing
                if not args.process:
                    for i in range(args.pernumber, len_input + 2):
                        iter = permutations(current_words, i)
                        wordlist, word_counter = create_wordlist(
                            iter,
                            args.min,
                            args.max,
                            args.level,
                            args.capital,
                            args.regex,
                            pattern_dict,
                            word_counter,
                        )

                        if args.level == 2:
                            write_function(wordlist, semaphore, output_dir)

                            iteration_number += 1
                            helpers.printProgressBar(iteration_number, total, length=50)
                            
                        if args.level == 3:
                            word_counter = level_three(
                                wordlist,
                                args,
                                output_dir,
                                word_counter,
                                semaphore,
                                write_function,
                            )
                            iteration_number += 1
                            helpers.printProgressBar(iteration_number, total, length=50)
                if args.process:
                    starmap_iterable = [
                        (current_words, i) for i in range(args.pernumber, len_input + 2)
                    ]
                    #calculate permutation with multiprocessing
                    with Pool(processes=args.process) as pool:
                        for iter in pool.starmap(permutations, starmap_iterable):
                            wordlist, word_counter = create_wordlist(
                                iter,
                                args.min,
                                args.max,
                                args.level,
                                args.capital,
                                args.regex,
                                pattern_dict,
                                word_counter,
                            )
                            if args.level == 1:
                                write_function(wordlist, semaphore, output_dir)

                                iteration_number += 1
                                helpers.printProgressBar(
                                    iteration_number, total, length=50
                                )
                            if args.level == 2:
                                word_counter = level_three(
                                    wordlist,
                                    args,
                                    output_dir,
                                    word_counter,
                                    semaphore,
                                    write_function,
                                )
                            iteration_number += 1
                            helpers.printProgressBar(iteration_number, total, length=50)

    except MemoryError:
        print(
            "[!] ERROR:(Memory error) There isn't enough memory to calculate permutations of words, Try with fewer words"
        )
    except OSError as e:
        if e.errno == ENOSPC:
            print(
                "[!] ERROR: (End Of Disk Space) There isn't enough disk space in the output directory, please provide another directory for the output file."
            )
    except KeyboardInterrupt:
        print("Keyboard Interrupt occurred!")

    if args.level == 0:
        print(f"These operations have been done:\n")
        for item in output_print:
            print(f"-{item}\n")

    
    print(
        f"Wordlist with {word_counter} words created in: {default_timer() - start_time :.2f} seconds with Drowtsil"
    )


if __name__ == "__main__":
    main()
