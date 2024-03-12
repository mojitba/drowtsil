""""Docstring about this script

"""
from timeit import default_timer
import argparse
from pathlib import Path
from itertools import permutations
from errno import ENOSPC
from multiprocessing import (
    cpu_count,
    Pool,
    get_all_start_methods,
    set_start_method,
    Semaphore,
)
import re

from modules import helpers


logo = """
    ____                     __       _ __
   / __ \_________ _      __/ /______(_) /
  / / / / ___/ __ \ | /| / / __/ ___/ / / 
 / /_/ / /  / /_/ / |/ |/ / /_(__  ) / /  
/_____/_/   \____/|__/|__/\__/____/_/_/   
                                                                                                                                             
 Wordlist Generator for Security Audit
                 V.1
"""


def _add_pattern(word, pattern_dict):
    for i in pattern_dict.keys():
        if i == 0:
            word = pattern_dict.get(i) + word
        elif i == 1000:
            word = word + pattern_dict.get(i)
        else:
            word = word[:i] + pattern_dict.get(i) + word[i:]
    return word


def _create_parser(process_number_default):
    parser = argparse.ArgumentParser(
        description="Another Wordlist Generator for Security Audit Purposes",
        prog="Drowtsil WordList Generator",
        epilog="Thanks for using %(prog)s!",
    )
    parser.add_argument(
        "-i", "--input", type=str, nargs="+", help="List of constant input words"
    )
    parser.add_argument(
        "-ti",
        "--tmpinp",
        type=str,
        nargs="+",
        help="List of temporary input words, every time each one\n\t selected and add to constant words list",
    )
    parser.add_argument(
        "-f", "--filename", type=str, help="Path to constant Wordlist file"
    )
    parser.add_argument(
        "-ft",
        "--tmpfile",
        type=str,
        help="Path to temporary Wordlist file, every time each one selected\n\t and add to constant words list",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./output.txt",
        help="Path of generated wordlist",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        type=str,
        nargs="+",
        default=None,
        help='Pattern of words, Enter like "pattern" "index". Example: 0 for first and 1000 for end of word or other indexes',
    )

    parser.add_argument(
        "-r", "--regex", type=str, default=None, help="Regex to match words"
    )

    parser.add_argument(
        "-l",
        "--level",
        type=int,
        default=2,
        choices=[0, 1, 2],
        help="Level of operation (0,1,2)",
    )

    parser.add_argument(
        "-pn",
        "--pernumber",
        type=int,
        default=2,
        help="Minimum number of words to generate permutations",
    )
    parser.add_argument(
        "-ps",
        "--process",
        type=int,
        nargs="?",
        const=process_number_default,
        default=0,
        help="Number of processes in pool(default is number of logical cores - 1)",
    )
    parser.add_argument(
        "-max", type=int, default=63, help="Maximum lenght of preshared key"
    )
    parser.add_argument(
        "-min", type=int, default=8, help="Minimum lenght of preshared key"
    )
    parser.add_argument(
        "-u", "--upper", action="store_true", help="Enable upper case function"
    )
    parser.add_argument(
        "-lo", "--lower", action="store_true", help="Enable upper case function"
    )
    parser.add_argument(
        "-c", "--capital", action="store_true", help="Enable capitalize function"
    )
    parser.add_argument(
        "-sb",
        "--substitution",
        action="store_true",
        help="Enable substitution function, replce 'a' with '@', 's' with '$' and etc",
    )
    # ?
    parser.add_argument(
        "-t",
        "--toggle",
        type=int,
        default=0,
        const=1,
        nargs="?",
        help="Enable toggle case function with index [default=0]",
    )
    parser.add_argument(
        "-s", "--swap", action="store_true", help="Enable upper case function"
    )
    parser.add_argument(
        "-rv", "--reverse", action="store_true", help="Reverse every item from input"
    )

    return parser


def create_wordlist(iter, min, max, level, capital, regexp, pattern_dict, word_counter):
    wordlist = []
    for item in iter:
        word = "".join(item)
        if pattern_dict:
            word = _add_pattern(word, pattern_dict)

        word_counter = _add_to_wordlist(wordlist, word, min, max, regexp, word_counter)

        if level == 2 and not capital:
            cap_word = "".join(helpers.capitalize(item))
            if pattern_dict:
                cap_word = _add_pattern(cap_word, pattern_dict)

            word_counter = _add_to_wordlist(
                wordlist, cap_word, min, max, regexp, word_counter
            )

    return wordlist, word_counter


def _add_to_wordlist(wordlist, word, min, max, regexp, word_counter):
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
    words = []
    output_print = []
    if args.upper:
        words += helpers.upper_case(current_words)
        output_print.append("upper case")
    if args.lower:
        words += helpers.lower_case(current_words)
        output_print.append("lower case")
    if args.toggle:
        words += helpers.toggle_case(current_words, args.toggle)
        output_print.append("toggle case")
    if args.swap:
        words += helpers.swap_case(current_words)
        output_print.append("swap case")
    if args.capital:
        words += helpers.capitalize(current_words)
        output_print.append("capitalize")
    if args.substitution:
        words += helpers.substitution(current_words)
        output_print.append("substitution")
    if args.reverse:
        words += helpers.reverse(current_words)
        output_print.append("reverse")
    return set(words), output_print


def level_two(
    wordlist,
    args,
    output_dir,
    word_counter,
    semaphore,
    write_function,
):
    write_function(wordlist, semaphore, output_dir)
    temp_wordlist = []
    if not args.substitution:
        temp_wordlist += helpers.substitution(wordlist)
        write_function(temp_wordlist, semaphore, output_dir)
        word_counter += len(temp_wordlist)
        temp_wordlist.clear()
    if not args.upper:
        temp_wordlist += set(helpers.upper_case(wordlist))
        write_function(temp_wordlist, semaphore, output_dir)
        word_counter += len(temp_wordlist)
        temp_wordlist.clear()
    if not args.capital:
        temp_wordlist += set(helpers.capitalize(wordlist))
        write_function(temp_wordlist, semaphore, output_dir)
        word_counter += len(temp_wordlist)
        temp_wordlist.clear()
    if not args.toggle:
        temp_wordlist += set(helpers.toggle_case(wordlist, index=args.toggle))
        write_function(temp_wordlist, semaphore, output_dir)
        word_counter += len(temp_wordlist)
        temp_wordlist.clear()

    wordlist.clear()

    return word_counter


# private function for unittesting purposes
def _extract_user_input(args, parser, read_function):
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
        else:
            parser.exit(
                1,
                message="[!] ERROR: Input words doesn't provide or the specified directory doesn't exist.\n",
            )
    except FileNotFoundError:
        parser.exit(
            1,
            message="[!] ERROR: Uncorrect specidfied path for input files. Try again!\n",
        )
    return cons_words, tmp_words


# private function for unittesting purposes
def _extract_pattern(args):
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
def _compute_total(tmp_words, len_input, pernumber):
    if tmp_words:
        total = ((len_input + 2) - pernumber) * len(tmp_words)
    else:
        total = len_input
    return total


def main(argv=None):
    start_method = get_all_start_methods()
    set_start_method(start_method[0])
    start_time = default_timer()
    process_number_default = cpu_count()
    write_function = helpers.write_to_file
    read_function = helpers.read_from_file
    parser = _create_parser(process_number_default)
    args = parser.parse_args()
    cons_words, tmp_words = _extract_user_input(args, parser, read_function)
    len_input = len(cons_words)
    total = _compute_total(tmp_words, len_input, args.pernumber)
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
        if args.level != 0:
            print_bar(iteration_number, total, length=50)

        for item in tmp_words:
            current_words = [item]
            current_words += cons_words

            # checking for levels
            if args.level == 0:
                words, output_print = level_zero(args, current_words)
                write_function(words, semaphore, output_dir)
                print(f"These opertations have been done:\n")
                for item in output_print:
                    print(f"-{item}\n")

            else:
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

                        if args.level == 1:
                            write_function(wordlist, semaphore, output_dir)

                            iteration_number += 1
                            helpers.printProgressBar(iteration_number, total, length=50)
                        if args.level == 2:
                            word_counter = level_two(
                                wordlist,
                                args,
                                output_dir,
                                word_counter,
                                semaphore,
                                write_function,
                            )
                            iteration_number += 1
                            helpers.printProgressBar(iteration_number, total, length=50)
                else:
                    starmap_iterable = [
                        (current_words, i) for i in range(args.pernumber, len_input + 2)
                    ]

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
                                word_counter = level_two(
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
                "[!] ERROR: (End Of Disk Space) There isn't enough disk space in output directory, please provide another directory for output file."
            )
    except KeyboardInterrupt:
        print("Keyboard Interrupt occurred!")

    if args.level != 0:
        print(
            f"Wordlist with {word_counter} words created in: {default_timer() - start_time :.2f} seconds with Drowtsil"
        )


if __name__ == "__main__":
    main()
