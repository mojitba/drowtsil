"""Unit tests for main file (drowtsil.py)

Program:
    Drowtsil(reverse of word list)-v1.0 - Another wordlist generator for penetration testing and education purposes

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
import unittest
from unittest.mock import patch, mock_open
from multiprocessing import Semaphore
import argparse
from pathlib import Path

import drowtsil

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class DrowtsilTestCase(unittest.TestCase):
    """Test case"""

    def setUp(self):
        self.const_words = ["riCk", "moRty"]
        self.tmp_words = ["42"]
        self.fake_input_const_files = "file/path/mock/const"
        self.fake_input_tmp_files = "file/path/mock/tmp"
        self.current_word = self.const_words + self.tmp_words
        self.semaphore = Semaphore(1)
        self.word_counter = 0
        self.parser = argparse.ArgumentParser()
        self.fake_output_path = "output/path/mock"
        self.expected_words = [
            "riCkmoRty",
            "moRtyriCk",
            "42riCkmoRty",
            "42moRtyriCk",
            "riCk42moRty",
            "riCkmoRty42",
            "moRty42riCk",
            "moRtyriCk42",
        ]

    def test_create_wordlist_with_pattern(self):
        iter = [
            ("riCk", "moRty"),
            ("moRty", "riCk"),
            ("42", "riCk", "moRty"),
            ("42", "moRty", "riCk"),
            ("riCk", "42", "moRty"),
            ("riCk", "moRty", "42"),
            ("moRty", "42", "riCk"),
            ("moRty", "riCk", "42"),
        ]

        excpected_list_with_pattern = [
            "FIRSTriCkmoRtyEND",
            "FIRSTmoRtyriCkEND",
            "FIRST42riCkmoRtyEND",
            "FIRST42moRtyriCkEND",
            "FIRSTriCk42moRtyEND",
            "FIRSTriCkmoRty42END",
            "FIRSTmoRty42riCkEND",
            "FIRSTmoRtyriCk42END",
        ]

        pattern_dict = {0: "FIRST", 1000: "END"}

        args = Namespace(
            max=63,
            min=8,
            upper=False,
            lower=False,
            capital=True,
            leet_case=False,
            toggle=0,
            swap=False,
            regex=None,
            level=1,
            all=False,
        )

        wordlist_with_pattern, word_counter_with_pattern = drowtsil.create_wordlist(
            iter,
            args.min,
            args.max,
            args.level,
            args.capital,
            args.regex,
            pattern_dict,
            self.word_counter,
        )

        self.assertCountEqual(wordlist_with_pattern, excpected_list_with_pattern)
        self.assertEqual(word_counter_with_pattern, 8)

    def test_create_wordlist_without_pattern(self):
        iter = [
            ("riCk", "moRty"),
            ("moRty", "riCk"),
            ("42", "riCk", "moRty"),
            ("42", "moRty", "riCk"),
            ("riCk", "42", "moRty"),
            ("riCk", "moRty", "42"),
            ("moRty", "42", "riCk"),
            ("moRty", "riCk", "42"),
        ]

        args = Namespace(
            max=63,
            min=8,
            upper=False,
            lower=False,
            capital=True,
            leet_case=False,
            toggle=0,
            swap=False,
            regex=None,
            level=1,
            all=False,
        )

        (
            wordlist_without_pattern,
            word_counter_without_pattern,
        ) = drowtsil.create_wordlist(
            iter,
            args.min,
            args.max,
            args.level,
            args.capital,
            args.regex,
            None,
            self.word_counter,
        )

        self.assertCountEqual(wordlist_without_pattern, self.expected_words)
        self.assertEqual(word_counter_without_pattern, 8)

    def test_level_zero(self):
        args = Namespace(
            upper=True,
            lower=True,
            capital=True,
            leet_case=True,
            reverse=True,
            alternating=True,
            toggle=1,
            swap=True,
            level=0,
            all=False,
        )
        words, output_print = drowtsil.level_zero(args, self.current_word)
        self.assertCountEqual(
            words,
            [
                "42",
                "RICK",
                "MORTY",
                "rick",
                "morty",
                "RiCK",
                "MoRTY",
                "RIcK",
                "MOrTY",
                "Rick",
                "Morty",
                "m0R7y",
                "r1Ck",
                "m0Rty",
                "moR7y",
                "kCir",
                "ytRom",
                "24",
                "rIcK",
                "mOrTy",
            ],
        )
        self.assertEqual(
            output_print,
            [
                "upper case",
                "lower case",
                "toggle case",
                "swap case",
                "capitalize",
                "leet_case",
                "reverse",
                "alternating",
            ],
        )

    def test_level_one_with_urls(self):
        numbers = 3
        chars = False
        constant_words = ['www.website.com/index.php','http://website.org/index.html','https://website.org/home.html','https://website.org/item=']
        temporary_words = ""
        _ , word_counter = drowtsil.level_one(constant_words, temporary_words, numbers, chars)
        self.assertEqual(word_counter, 12)
    
    def test_level_one_with_urls(self):
        numbers = 0
        chars = True
        constant_words = ['www.website.com/index','http://website.org/index','https://website.org/home','https://website.org/item=']
        temporary_words = ["list", "#"]
        _, word_counter = drowtsil.level_one(constant_words, temporary_words, numbers, chars)
        self.assertEqual(word_counter, 112)
    
    def test_is_url_valid(self):
        input_list = ['www.website.com/index.php']
        self.assertEqual(drowtsil._is_url(input_list), [['www.website.com/index', '.php', '']])
    
    def test_is_url_invalid(self):
        input_list = ['Not_a_url']
        self.assertEqual(drowtsil._is_url(input_list), [])

    def test_level_three_args_all_disabled(self):
        args_all_disabled = Namespace(
            input=self.const_words,
            tmpinp=self.tmp_words,
            filename=None,
            tmpfile=None,
            output=None,
            pernumber=2,
            process=8,
            max=63,
            min=8,
            upper=False,
            lower=False,
            capital=False,
            leet_case=False,
            toggle=None,
            swap=False,
            sentence=False,
            alternating=False,
            level=2,
            all=False,
        )
                
        with patch("builtins.open", mock_open()) as mock_write_to_file:
            word_counter = drowtsil.level_three(
                self.expected_words,
                args_all_disabled,
                self.fake_output_path,
                self.word_counter,
                self.semaphore,
                mock_write_to_file,
            )
            self.assertEqual(word_counter, 0)

    def test_level_three_args_all_enabled(self):
        args_all_enabled = Namespace(
            input=self.const_words,
            tmpinp=self.tmp_words,
            filename=None,
            tmpfile=None,
            output=None,
            pernumber=2,
            process=8,
            max=63,
            min=8,
            upper=False,
            lower=False,
            capital=False,
            leet_case=False,
            toggle=None,
            swap=False,
            sentence=False,
            alternating=False,
            level=2,
            all=True,
        )

        with patch("builtins.open", mock_open()) as mock_write_to_file:
            word_counter = drowtsil.level_three(
                self.expected_words,
                args_all_enabled,
                self.fake_output_path,
                self.word_counter,
                self.semaphore,
                mock_write_to_file,
            )
            self.assertEqual(word_counter, 64)

    def test_add_to_wordlist_args_without_regex(self):
        test_wordlist = []
        word_counter = 0
        args_without_regex = Namespace(max=63, min=8, regex=None)

        for word in self.expected_words:
            word_counter = drowtsil._add_to_wordlist(
                test_wordlist,
                word,
                args_without_regex.min,
                args_without_regex.max,
                args_without_regex.regex,
                word_counter,
            )

        self.assertEqual(word_counter, 8)

    def test_add_to_wordlist_args_with_regex(self):
        test_wordlist = []
        word_counter = 0
        args_with_regex = Namespace(max=63, min=8, regex="^[r]")

        for word in self.expected_words:
            word_counter = drowtsil._add_to_wordlist(
                test_wordlist,
                word,
                args_with_regex.min,
                args_with_regex.max,
                args_with_regex.regex,
                word_counter,
            )

        self.assertEqual(word_counter, 3)

    def test_create_parser(self):
        test_args = {
            "input": None,
            "tmpinp": None,
            "filename": None,
            "tmpfile": None,
            "output": "./output.txt",
            "pattern": None,
            "regex": None,
            "level": 2,
            "pernumber": 2,
            "process": 0,
            "max": 63,
            "min": 8,
            "upper": False,
            "lower": False,
            "capital": False,
            "sentence": False,
            "leet_case": False,
            "toggle": 0,
            "swap": False,
            "reverse": False,
            "alternating": False,
            "all" : False,
            "numbers": False,
            "chars": False,
        }

        test_process_number_default = 0
        parser = drowtsil._create_parser(test_process_number_default)
        args = parser.parse_args()
        self.assertCountEqual(test_args, args.__dict__)

    def test_add_pattern(self):
        word = "riCkmoRty42"
        first_pattern_dict = {0: "FIRST", 1000: "END"}
        second_pattern_dict = {0: "FIRST", -1: "ONEBEFOREEND"}
        third_pattern_dict = {2: "SECOND", -2: "SECONDBEFOREEND"}

        self.assertEqual(
            drowtsil._add_pattern(word, first_pattern_dict), "FIRSTriCkmoRty42END"
        )
        self.assertEqual(
            drowtsil._add_pattern(word, second_pattern_dict),
            "FIRSTriCkmoRty4ONEBEFOREEND2",
        )
        self.assertEqual(
            drowtsil._add_pattern(word, third_pattern_dict),
            "riSECONDCkmoRtySECONDBEFOREEND42",
        )

    def test_calculate_total(self):
        len_input = len(self.const_words)
        pernumber = 2
        self.assertEqual(
            drowtsil._calculate_total(self.tmp_words, len_input, pernumber), 2
        )

    def test_extract_pattern(self):
        args = Namespace(pattern=["FIRST", "0", "END", "1000"])
        result = drowtsil._extract_pattern(args)
        self.assertEqual(result, {1000: "END", 0: "FIRST"})

    def test_extract_user_input_single_arg_exist(self):
        single_arg_exist = Namespace(
            input=None,
            tmpinp=None,
            filename=self.fake_input_const_files,
            tmpfile=None,
            level = None,
        )
      
        with patch("builtins.open", mock_open()) as mock_read_from_filename_tmpfile:
            mock_read_from_filename_tmpfile.return_value = ["mock value"]
            
            with self.assertRaises(SystemExit) as e:
                drowtsil._extract_user_input(
                    single_arg_exist,
                    self.parser,
                    mock_read_from_filename_tmpfile,
                )
                er = e.exception
                self.assertEqual(er.error_code, 1)
                self.assertEqual(
                    er.message,
                    "[!] ERROR: Input constant words or temporary words doesn't provide.\n",
                )

    def test_extract_user_input_args_filename_tmpfile_exist(self):
        args_filename_tmpfile_exist = Namespace(
            input=None,
            tmpinp=None,
            filename=self.fake_input_const_files,
            tmpfile=self.fake_input_tmp_files,
            level = None,
        )

        with patch("builtins.open", mock_open()) as mock_read_from_filename_tmpfile:
            mock_read_from_filename_tmpfile.return_value = ["mock value"]

            self.assertEqual(
                drowtsil._extract_user_input(
                    args_filename_tmpfile_exist,
                    self.parser,
                    mock_read_from_filename_tmpfile,
                ),
                (["mock value"], ["mock value"]),
            )

    def test_extract_user_input_args_filename_tmpin_exist(self):
        args_filename_tmpin_exist = Namespace(
            input=None,
            tmpinp=self.tmp_words,
            filename=self.fake_input_const_files,
            tmpfile=None,
            level = None,
        )

        with patch("builtins.open", mock_open()) as mock_read_from_filename_tmpfile:
            mock_read_from_filename_tmpfile.return_value = ["mock value"]

            self.assertEqual(
                drowtsil._extract_user_input(
                    args_filename_tmpin_exist,
                    self.parser,
                    mock_read_from_filename_tmpfile,
                ),
                (["mock value"], ["42"]),
            )

    def test_extract_user_input_args_input_tmpfile_exist(self):
        args_input_tmpfile_exist = Namespace(
            input=self.const_words,
            tmpinp=None,
            filename=None,
            tmpfile=self.fake_input_tmp_files,
            level = None,
        )

        with patch("builtins.open", mock_open()) as mock_read_from_filename_tmpfile:
            mock_read_from_filename_tmpfile.return_value = ["mock value"]

            self.assertEqual(
                drowtsil._extract_user_input(
                    args_input_tmpfile_exist,
                    self.parser,
                    mock_read_from_filename_tmpfile,
                ),
                (["riCk", "moRty"], ["mock value"]),
            )

    def test_extract_user_input_args_input_tmpinp_exist(self):
        args_input_tmpinp_exist = Namespace(
            input=self.const_words,
            tmpinp=self.tmp_words,
            filename=None,
            tmpfile=None,
            level = None,
        )

        with patch("builtins.open", mock_open()) as mock_read_from_filename_tmpfile:
            mock_read_from_filename_tmpfile.return_value = ["mock value"]

            self.assertEqual(
                drowtsil._extract_user_input(
                    args_input_tmpinp_exist,
                    self.parser,
                    mock_read_from_filename_tmpfile,
                ),
                (["riCk", "moRty"], ["42"]),
            )

    def test_extract_user_input_args_input_just_exist_in_level_zero(self):
        args_input_just_exist_in_level_zero = Namespace(
            input=self.const_words,
            tmpinp=None,
            filename=None,
            tmpfile=None,
            level = 0,
        )

        with patch("builtins.open", mock_open()) as mock_read_from_filename_tmpfile:
            mock_read_from_filename_tmpfile.return_value = ["mock value"]

            self.assertEqual(
                drowtsil._extract_user_input(
                    args_input_just_exist_in_level_zero,
                    self.parser,
                    mock_read_from_filename_tmpfile,
                ),
                (['riCk', 'moRty'], ''),
            )
    
    def test_extract_user_input_args_filename_just_exist_in_level_zero(self):
        args_filename_just_exist_in_level_zero = Namespace(
            input=None,
            tmpinp=None,
            filename=self.fake_input_const_files,
            tmpfile=None,
            level = 0,
        )

        with patch("builtins.open", mock_open()) as mock_read_from_filename_tmpfile:
            mock_read_from_filename_tmpfile.return_value = ["mock value"]

            self.assertEqual(
                drowtsil._extract_user_input(
                    args_filename_just_exist_in_level_zero,
                    self.parser,
                    mock_read_from_filename_tmpfile,
                ),
                (['mock value'], ''),
            )

    def test_extract_user_input_args_does_not_exist(self):
        args_does_not_exist = Namespace(
            input=None,
            tmpinp=None,
            filename=None,
            tmpfile=None,
            level = None,
        )

        with patch("builtins.open", mock_open()) as mock_read_from_filename_tmpfile:
            mock_read_from_filename_tmpfile.return_value = ["mock value"]

            with self.assertRaises(SystemExit) as e:
                drowtsil._extract_user_input(
                    args_does_not_exist,
                    self.parser,
                    mock_read_from_filename_tmpfile,
                )
                er = e.exception
                self.assertEqual(er.error_code, 1)
                self.assertEqual(
                    er.message,
                    "[!] ERROR: Input constant words or temporary words doesn't provide.\n",
                )

    def test_checking_permutation_number_answer_no(self):
        len_input = 13
        with patch("builtins.input", lambda _ : '-n') as mock_input_no:

            with self.assertRaises(SystemExit) as e:
                drowtsil._checking_permutation_number(
                    len_input,
                    self.parser,
                    )
                er = e.exception
                
                self.assertEqual(er.error_code, 1)
                self.assertEqual(
                     er.message,
                     "[!] Try again with fewer words!",
                 )

    def test_checking_permutation_number_answer_yes(self):
        len_input = 13
        with patch("builtins.input", lambda _ : '-y') as mock_input_yes:
            result = drowtsil._checking_permutation_number(
                    len_input,
                    self.parser,
                    )
            self.assertEqual(result, None)




if __name__ == "__main__":
    unittest.main()
