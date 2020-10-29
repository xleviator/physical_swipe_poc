#! /usr/bin/env python3

from functools import lru_cache
import sys

if len(sys.argv) != 2:
    print("Usage:",sys.argv[0],"<ideal file>")
    exit(1)

IDEAL_FILE = sys.argv[1]

with open(IDEAL_FILE, "r") as f:
    WORDS = [a.split() for a in f.read().splitlines()]

@lru_cache(maxsize=None)
def levenshtein(s, t):
    MISMATCH_COST = 3
    ADD_TO_S_COST = 1
    ADD_TO_T_COST = 1

    if s == "":
        return len(t) * ADD_TO_T_COST
    if t == "":
        return len(s) * ADD_TO_S_COST

    mismatch = 0
    if s[-1] != t[-1]:
        mismatch = MISMATCH_COST

    res = min([levenshtein(s[:-1], t)+ADD_TO_S_COST,
               levenshtein(s, t[:-1])+ADD_TO_T_COST,
               levenshtein(s[:-1], t[:-1])+ mismatch])

    return res

def predict_word(a):
    if len(a) == 0: return ""

    best = 100000
    best_w = ""
    for w, i in WORDS:
        if w[0] != a[0] or w[-1] != a[-1]: continue

        l = levenshtein(a, i)
        if l < best:
            best = l
            best_w = w
    return best_w

while True:
    print(predict_word(input()))
