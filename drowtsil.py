#!/usr/bin/python3
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

from modules import helpers



def main(argv=None):
    start_method = get_all_start_methods()
    set_start_method(start_method[0])
    start_time = default_timer()
    process_number_default = cpu_count()

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
        "--pernumber",
        type=int,
        default=2,
        help="Minimum number of words to generate permutations",
    )
    parser.add_argument(
        "-ps",
        "--process",
        type=int,
        default=process_number_default,
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
        "-c", "--capital", action="store_true", help="Enable capital case function"
    )
    parser.add_argument(
        "-sb",
        "--substitution",
        action="store_true",
        help="Enable substitution function, replce 'a' with '@', 's' with '$' and etc",
    )
    parser.add_argument(
        "-t",
        "--toggle",
        type=int,
        default=0,
        const=1,
        nargs="?",
        help="Enable toggle case function with position [default=0]",
    )
    parser.add_argument(
        "-s", "--swap", action="store_true", help="Enable upper case function"
    )
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        default=2,
        choices=[0, 1, 2],
        help="Level of operation (0,1,2)",
    )

    args = parser.parse_args()
    # exfiltrate arguments
    min = args.min
    max = args.max
    per_number = args.pernumber
    output_dir = Path(args.output)
    process_number = args.process

    try:
        if args.filename and args.tmpfile:
            target_cons_dir = Path(args.filename)
            target_tmp_dir = Path(args.tmpfile)
            cons_words = helpers.read_from_file(target_cons_dir)
            tmp_words = helpers.read_from_file(target_tmp_dir)

        elif args.filename and args.tmpinp:
            target_cons_dir = Path(args.filename)
            cons_words = helpers.read_from_file(target_cons_dir)
            tmp_words = args.tmpinp

        elif args.input and args.tmpfile:
            target_tmp_dir = Path(args.tmpfile)
            cons_words = args.input
            tmp_words = helpers.read_from_file(target_tmp_dir)

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

    len_input = len(cons_words)
    semaphore = Semaphore(1)
    if tmp_words:
        total = ((len_input + 2) - per_number) * len(tmp_words)
    else:
        total = len_input

    iteration_number = 0
    word_counter = 0

    # emptying previous output file
    with open(output_dir, "w") as f:
        pass

    try:
        if args.level != 0:
            helpers.printProgressBar(0, total, length=50)
        for item in tmp_words:
            current_words = [item]
            current_words += cons_words
            # checking for levels
            if args.level == 0:
                words = []
                output_print = []
                if args.upper:
                    words += helpers.upper_case(current_words)
                    output_print.append("uppercase")
                if args.lower:
                    words += helpers.lower_case(current_words)
                    output_print.append("lowercase")
                if args.toggle:
                    words += helpers.toggle_case(current_words, args.toggle)
                    output_print.append("togglecase")
                if args.swap:
                    words += helpers.swap_case(current_words)
                    output_print.append("swapcase")
                if args.capital:
                    words += helpers.capitalize(current_words)
                    output_print.append("capitalize")
                if args.substitution:
                    words += helpers.substitution(current_words)
                    output_print.append("substitution")

                helpers.write_to_file(words, semaphore, output_dir)

            if args.level == 1 or args.level == 2:
                starmap_iterable = [
                    (current_words, i) for i in range(per_number, len_input + 2)
                ]

                with Pool(processes=process_number) as pool:
                    for iter in pool.starmap(permutations, starmap_iterable):
                        wordlist = []
                        for item in iter:
                            letter = "".join(item)
                            if len(letter) >= min and len(letter) <= max:
                                wordlist.append(letter)
                                word_counter += 1
                            if args.level == 2 and not args.capital:
                                cap_letter = "".join(helpers.capitalize(item))
                                if len(cap_letter) >= min and len(cap_letter) <= max:
                                    wordlist.append(cap_letter)
                                    word_counter += 1

                        if args.level == 1:
                            helpers.write_to_file(wordlist, semaphore, output_dir)
                            iteration_number += 1
                            helpers.printProgressBar(iteration_number, total, length=50)
                        if args.level == 2:
                            helpers.write_to_file(wordlist, semaphore, output_dir)
                            temp_wordlist = []
                            if not args.substitution:
                                temp_wordlist += helpers.substitution(wordlist)
                                helpers.write_to_file(
                                    temp_wordlist, semaphore, output_dir
                                )
                                word_counter += len(temp_wordlist)
                                temp_wordlist.clear()
                            if not args.upper:
                                temp_wordlist += set(helpers.upper_case(wordlist))
                                helpers.write_to_file(
                                    temp_wordlist, semaphore, output_dir
                                )
                                word_counter += len(temp_wordlist)
                                temp_wordlist.clear()
                            if not args.capital:
                                temp_wordlist += set(helpers.capitalize(wordlist))
                                helpers.write_to_file(
                                    temp_wordlist, semaphore, output_dir
                                )
                                word_counter += len(temp_wordlist)
                                temp_wordlist.clear()
                            if not args.toggle:
                                temp_wordlist += set(
                                    helpers.toggle_case(wordlist, position=args.toggle)
                                )
                                helpers.write_to_file(
                                    temp_wordlist, semaphore, output_dir
                                )
                                word_counter += len(temp_wordlist)
                                temp_wordlist.clear()
                            wordlist.clear()

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
    if args.level == 0:
        print(f"These opertations done on input wordlist:\n")
        for item in output_print:
            print(f"-{item}\n")


if __name__ == "__main__":
    main()
