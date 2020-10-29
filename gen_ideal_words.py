#! /usr/bin/env python3

# Cleanroom POC for physical swiping on a keyboard
# Steven Moreland

from collections import defaultdict
from itertools import combinations
from itertools import permutations

import sys

# readme:
# - all measurements are in micrometers
# - row - on a qwerty keyboard, q is on the 0 row, a is on the 1 row, z is on the 2 row
# - index - location of key counting from the left. in row one tab is 0, q is 1.

# the horizontal and vertical key gap distance on the keyboard
# unfortunately, I couldn't find actual measurements
KEY_GAP_VERTICAL   =  3500
KEY_GAP_HORIZONTAL =  3500
KEY_HEIGHT         = 15210
KEY_WIDTH          = 15667

NUM_ROWS           = 3

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
ALPHABET_SET = set(ALPHABET)

# the format is, from the left, the letters in order.
#'?' where there is a non-alphabetic key.
# so, '?' shows up as tabs
QWERTY = [ "?qwertyuiop???", "?asdfghjkl???", "?zxcvbnm????" ]
DVORAK = [ "????pyfgcrl???", "?aoeuidhtns??", "??qjkxbmwvz?" ]

if len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "qwerty|dvorak <dict>")
    exit(1)

# WORD_FILE = "/usr/share/dict/words"

layout_pref = sys.argv[1] if len(sys.argv) == 2 else "qwerty"
LAYOUT = { "qwerty": QWERTY, "dvorak": DVORAK }[sys.argv[1]]
WORD_FILE = sys.argv[2]

def layout_to_lookup(layout):
    """ for key, get (row, index) """
    LU = {} # Look Up
    for row in range(len(layout)):
        for index in range(len(layout[row])):
            c = layout[row][index]
            if c == "?": continue
            assert c not in LU
            LU[c] = (row, index)

    for c in ALPHABET:
        assert c in LU, c

    return LU

LAYOUT_LU = layout_to_lookup(LAYOUT)

# the following measurements are taken with calipers on a 2016 macbook pro laptop
# for row, index
KEY_WIDTH_RI = [
    # tab, then other keys
    [25200] + [KEY_WIDTH] * 13,
    # caps lock, other keys, return
    [29820] + [KEY_WIDTH] * 11 + [30000],
    # shift, other keys, shift
    [39350] + [KEY_WIDTH] * 10 + [39350],
]

for layout in [ QWERTY, DVORAK ]:
    assert len(layout) == len(KEY_WIDTH_RI)
    for row in range(len(layout)):
        assert len(KEY_WIDTH_RI[row]) == len(layout[row])

def key_start_x(row, index):
    return sum(KEY_WIDTH_RI[row][:index]) + index * KEY_GAP_HORIZONTAL
def key_end_x(row, index):
    return key_start_x(row, index) + KEY_WIDTH_RI[row][index]
def key_start_y(row, index):
    return row * (KEY_HEIGHT + KEY_GAP_VERTICAL)
def key_end_y(row, index):
    return key_start_y(row, index) + KEY_HEIGHT

def row_length(row):
    return key_end_x(row, len(KEY_WIDTH_RI[row]) - 1)

# row lengths within 1mm of each other, since on this keyboard they
# start and end at the same location.
for r1, r2 in combinations(range(NUM_ROWS), 2):
    assert abs(row_length(r1) - row_length(r2)) < 1000

def print_key_info(letter):
    loc = LAYOUT_LU[letter]
    print("Information for", letter)
    print("row, column", loc)
    print("key_start_x", key_start_x(*loc))
    print("key_end_x", key_end_x(*loc))
    print("key_start_y", key_start_y(*loc))
    print("key_end_y", key_end_y(*loc))

# a bounding box (bb)
# is the (top left point, bottom right point)

def bounding_boxes():
    """ computes top left, bottom right for each letter """
    BB = {}
    for c in ALPHABET:
        loc = LAYOUT_LU[c]
        BB[c] = (
            (key_start_x(*loc), key_start_y(*loc)),
            (key_end_x(*loc), key_end_y(*loc))
        )
    return BB
BB_FOR_LETTER = bounding_boxes()

KEYBOARD_BB = ( (0,0),  (row_length(0), key_end_y(2,1)) )

def bb_center(bb):
    (x1, y1), (x2, y2) = bb
    return (x1+x2)/2, (y1+y2)/2

def bb_point_intersect(bb, p):
    (x1, y1), (x2, y2) = bb
    px, py = p
    return x1 <= px <= x2 and y1 <= py <= y2

# https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
def line_intersect(l1, l2):
    xdiff = (l1[0][0] - l1[1][0], l2[0][0] - l2[1][0])
    ydiff = (l1[0][1] - l1[1][1], l2[0][1] - l2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return None

    d = (det(*l1), det(*l2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    return x, y

assert line_intersect( ((0,0),(0,2)), ((-1, 1),(1, 1)) ) == (0, 1)

def bb_corners(bb):
    (x1, y1), (x2, y2) = bb
    return (x1, y1), (x1, y2), (x2, y1), (x2, y2)

def bb_expand(bb, amount):
    (x1, y1), (x2, y2) = bb
    return (x1 - amount, y1 - amount), (x2 + amount, y2 + amount)

# only care about one point since keys don't overlap...
def bb_line_intersect(bb, l):
    """ returns a points where a line intersects a bounding box """
    (x1, y1), (x2, y2) = bb
    for point in [
        line_intersect( ((x1,y1),(x1,y2)), l ),
        line_intersect( ((x1,y1),(x2,y1)), l ),
        line_intersect( ((x1,y2),(x2,y2)), l ),
        line_intersect( ((x2,y1),(x2,y2)), l )
    ]:
        if point is None: continue
        # FIXME: might be just over the edge?
        if not bb_point_intersect(bb_expand(bb, 100), point): continue

        yield point

def line_loc(l, p):
    """
    l is a line, p is a point along that line. if l[0] is the start of that line,
    return the percentage p is along that line. So l[1] would retur 1
    """
    px, py = p
    (x1, y1), (x2, y2) = l

    xper = None if x1 == x2 else (px - x1) / (x2 - x1)
    yper = None if y1 == y2 else (py - y1) / (y2 - y1)

    if xper is not None and yper is not None:
        assert abs(xper-yper) < 0.001, "%s %s %s %s" % (xper, yper, l, p)

    if xper is not None:
        return xper
    return yper

assert line_loc(  ((0, 0),(2,4)),  (1, 2)  ) == 0.5

def line_scored_path(l):
    """
    computes the letters a finger would hit if it went straight from start to end
    """

    PATH = []

    for c,bb in BB_FOR_LETTER.items():
        # getting the percentage along the path that the key is found
        scores = (line_loc(l, p) for p in bb_line_intersect(bb, l))
        scores = (score for score in scores if 0 <= score <= 1)
        scores = list(scores)

        if len(scores) == 0: continue

        for s in scores:
            PATH.append( (s, c) )

    return PATH

def first_unique(l):
    u = []
    for i in l:
        if i not in u:
            u.append(i)
    return u

def avg(l):
    return sum(l) / len(l)

def bb_to_bb_letters(bba, bbb):
    PATH = []
    for a, b in zip(bb_corners(bba), bb_corners(bbb)):
        PATH += line_scored_path((a, b))

    scores = defaultdict(list)
    for i, c in PATH:
        scores[c] += [i]

    PATH = [(avg(a), c) for (c, a) in scores.items() if len(a) > 2]

    return "".join(first_unique(p[1] for p in sorted(PATH)))

#print(bb_to_bb_letters(BB_FOR_LETTER["c"], BB_FOR_LETTER["u"]))
#print(bb_to_bb_letters(BB_FOR_LETTER["q"], BB_FOR_LETTER["l"]))

def ideal_word_swipe(word):
    swipe = ""
    for a, b in zip(word, word[1:]):
        swipe += bb_to_bb_letters(BB_FOR_LETTER[a], BB_FOR_LETTER[b])
    return swipe

def read_dict():
    with open(WORD_FILE, "r") as dict:
        for i in dict.read().splitlines():
            if any(c not in ALPHABET_SET for c in i.lower()):
                continue
            yield i
    
for w in read_dict():
    s = ideal_word_swipe(w.lower())
    if not s: s = w.lower()
    print(w, s)

