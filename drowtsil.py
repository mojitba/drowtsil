import argparse


def main(argv=None):
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
        default=8,
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
