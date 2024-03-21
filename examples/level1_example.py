#provide the input words (constants and temporary words) and add consecutive numbers(with limit10) at the end in level 1:
python drowtsil.py -f "./input.txt" -ft "./tmp.txt" -l 1 -n 10
python drowtsil.py -i "constant_word_1" "constant_word_2" -ti "temporary_word_1" "temporary_word_2" -l 1 --numbers

#provide the input words (constants words) and add consecutive charcters(a-z) and temporary words at the end in level 1:
python drowtsil.py -f "./input.txt" -ft "./tmp.txt" -l 1 -ch
python drowtsil.py -i "constant_word_1" "constant_word_2" -ti "temporary_word_1" "temporary_word_2" -l 1 --chars