"""Unit tests for helper functions (modules/helpers.py)

Program:
    Drowtsil(reverse of word list)-v1.0 - Another wordlist for education or security audit purposes

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

from src.modules import helpers


class DrowtsilHelpersTestCase(unittest.TestCase):
    """Test case for modules.helpers"""

    def setUp(self):
        self.input_words = ["riCk", "moRty", "42"]
        self.semaphore = Semaphore(1)
        self.fake_file_path = "file/path/mock"

    def test__check_input(self):
        int_input = 42
        str_input = "rick"
        expect_true = helpers._check_input(str_input)
        expect_false = helpers._check_input(int_input)
        self.assertTrue(expect_true)
        self.assertFalse(expect_false)

    def test_write_to_file(self):
        with patch("builtins.open", mock_open()) as mock_write_to_file:
            helpers.write_to_file(self.input_words, self.semaphore, self.fake_file_path)
            mock_write_to_file.assert_called_once_with(self.fake_file_path, "a")

    def test_read_from_file(self):
        mock_file_content = """riCK
        moRty
        42"""
        with patch(
            target="builtins.open",
            new=mock_open(read_data=mock_file_content),
            create=True,
        ) as mock_read_from_file:
            actual = helpers.read_from_file(self.fake_file_path)
            mock_read_from_file.assert_called_once_with(self.fake_file_path, "r")
            expected = mock_file_content.split("\n")
            self.assertEqual(expected, actual)

    def test_upper_case(self):
        expected_list_upper_case = helpers.upper_case(self.input_words)
        self.assertEqual(expected_list_upper_case, ["RICK", "MORTY", "42"])

    def test_lower_case(self):
        expected_list_lower_case = helpers.lower_case(self.input_words)
        self.assertEqual(expected_list_lower_case, ["rick", "morty", "42"])

    def test_leet_case(self):
        expected_list_leet_case = helpers.leet_case(self.input_words)
        expected_list = ["r1Ck", "m0Rty", "moR7y", "m0R7y"]
        self.assertCountEqual(expected_list_leet_case, expected_list)
        self.assertIn("r1Ck", expected_list_leet_case)
        self.assertIn("m0Rty", expected_list_leet_case)
        self.assertIn("moR7y", expected_list_leet_case)
        self.assertIn("m0R7y", expected_list_leet_case)

    def test_capitalize(self):
        expected_list_capitalize = helpers.capitalize(self.input_words)
        self.assertCountEqual(expected_list_capitalize, ["Rick", "Morty", "42"])

    def test_swap_case(self):
        expected_list_swap_case = helpers.swap_case(self.input_words)
        self.assertCountEqual(expected_list_swap_case, ["RIcK", "MOrTY", "42"])

    def test_toggle_case(self):
        expected_list_toggle_case = helpers.toggle_case(self.input_words, index=0)
        self.assertCountEqual(expected_list_toggle_case, ["rICK", "mORTY"])

    def test_reverse(self):
        expected_list_reverse = helpers.reverse(self.input_words)
        self.assertCountEqual(expected_list_reverse, ["kCir", "ytRom", "24"])

    def test_alternating_case(self):
        self.assertCountEqual(
            helpers.alternating_case(self.input_words), ["rIcK", "mOrTy", "42"]
        )

    def test_sentence_case(self):
        text_list = ["thisistext", "tHisIsALSOateXt"]
        self.assertEqual(helpers.sentence_case(text_list), ['Thisistext', 'Thisisalsoatext'])
        

    def tear_down(self):
        pass


if __name__ == "__main__":
    unittest.main()
