# Drowtsil
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

Drowtsil (reverse of wordlist) is a targeted-attack wordlist generator. It's a simple script that can help in penetration testing (brute-force attack, dictionary attack, and fuzzing). So you can use it to create a wordlist of login credentials or URLs, etc. 

## Features
- Apply different types of transform functions like upper and lowercase, toggle-case, leet-case, reverse-case, sentence-case, alternate-case and swap-case
- Perform permutation with multiprocessing and without it.
- Ease of use in four different levels of operations. 

## How it works
Drowtsil runs in four different levels. These levels are designed for ease of use. In **level 0**, you can leverage different functions to transform your input wordlist. these functions include upper and lowercase, capital case, leet case, toggle case, swap case, alternating form, and reverse form. In **level 1**, you can Add consecutive numbers or characters or words you provide in temporary list, at the end of each word from the input wordlist. This function can detect web URLs and their suffixes. In **level 2**, you can get a permutation of your input list. this operation can be performed with multiprocessing or without it. In **level 3**, you can get a permutation of your input list and in addition, perform all transform functions on these permutations.

This tool accepts two kinds of input lists as the name of constant and temporary. the first one is a list of words you want to apply functions or permutations on them and the second one is the list that can use for items you want to occur once for each of the first list members. the second list can contain specific items in the wordlist like year date or symbols. temporary list can be leveraged in level 1 to add at the end of each word from the constant list or in levels 2 and 3 to add to each word of the constant list in permutation operation.

## Requirements
Just python 3

## Usage
python drowtsil.py -h

## options:
```
(Input and output):
  -i, --input           List of constant input words
  -ti, --tmpinp         List of temporary input words, every time each one is selected and added to constant words list
  -f, --filename        Path to constant Wordlist file
  -ft, --tmpfile        Path to temporary Wordlist file, every time each one selected and added to constant words list
  -o, --output          Path of generated wordlist (default is "./output.txt")
(Runtime properties):
  -l, --level           Level of operation (0,1,2,3) (default is 1)
  -p, --pattern         Pattern of words, Enter like "pattern" "index". Example: 0 for the first of the word and 1000 for the end of the word or other indexes
  -r, --regex           Regex to match words
  -pn, --pernumber      Minimum number of words to generate permutations like start with 2-word permutation (default is 2)
  -ps, --process        Number of processes in the pool (default is number of logical cores - 1)
  -max                  Maximum length of the preshared key (default is 63)
  -min                  Minimum length of the preshared key (default is 8)
(Transform functions):
  -u, --upper           Enable upper case function
  -lo, --lower          Enable lower case function
  -c, --capital         Enable capitalize function
  -lt, --leet_case      Enable leet case function, replace 'a' with '@', 's' with '$' and etc
  -t, --toggle          Enable toggle case function with index (default is 0)
  -s, --swap            Enable swap case function
  -st, --sentence       Enable sentence case function
  -rv, --reverse        Reverse every word in level 0
  -a, --alternating     transform text into the form that alternates between lowercase and uppercase
  -all                  Apply all text transform functions in levels 0 and 3
  -n, --numbers         Add consecutive numbers at the end of strings in level 1
  -ch, --chars          Add consecutive characters at the end of strings in level 1
  ```
## Examples
provide the input words in the command line and apply all functions of level 0:
```
-i "constant_word_1" "constant_word_2" -l 0 -all
```
```
-i "constant_word_1" "constant_word_2" -l 0 -u -lo -c -lt -t 1 -s -st -rv -a
```
provide the input words in the from of text files and apply all functions of level 0:
```
-f "./input.txt" -l 0 -all
```
```
-f "./input.txt" -l 0 -u -lo -c -lt -t 1 -s -st -rv -a
```
provide the input words (constants and temporary words) and add consecutive numbers(with limit10) at the end in level 1:
```
-f "./input.txt" -ft "./tmp.txt" -l 1 -n 10
```
```
-i "constant_word_1" "constant_word_2" -ti "temporary_word_1" "temporary_word_2" -l 1 --numbers
```
provide the input words (constants words) and add consecutive characters(a-z) and temporary words at the end in level 1:
```
-f "./input.txt" -ft "./tmp.txt" -l 1 -ch
```
```
-i "constant_word_1" "constant_word_2" -ti "temporary_word_1" "temporary_word_2" -l 1 --chars
```
provide the input words and get permutations of them in level 2:
```
-f "./input.txt" -ft "./tmp.txt" -l 2
```
provide the input words and define output file directory in level 2:
```
-f "./input.txt" -ft "./tmp.txt" -o "./output.txt" -l 2
```
level 3 applies permutation and all functions on input words:
```
-f "./input.txt" -ft "./tmp.txt" -l 3 -all
```
```
-f "./input.txt" -ft "./tmp.txt" -l 3 -u -c -lt -t 0 -st -a
```
Get permutations of reverse words:
```
-f "./input.txt" -o "./reversed_output.txt" -l 0 -rv
```
```
-f "./reversed_output.txt" -l 3 -all
```

## Limitations
You must be aware that permutation operation may require heavy computing, memory, and disk resources in a matter of long wordlists.

## Disclaimer
The software and scripts provided by this repository should only be used for legal activations like penetration testing
or education purposes.

## Todo
- [ ] random-case transformation
- [ ] create wordlist using web scraping
- [ ] create wordlist based on subject
