#! /bin/sh

./gen_ideal_words.py qwerty google-10000-english.txt > IDEAL_10000_qwerty
./gen_ideal_words.py dvorak google-10000-english.txt > IDEAL_10000_dvorak

