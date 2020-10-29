This was written on the afternoon of Aug 25, 2019, and you can see it
filmed here:

https://www.youtube.com/watch?v=NQbtv97-L0g

This is not quality software - be warned.

The point is cellphone screens have very high resolution, and I was
curious if just pressing buttons on a keyboard had enough information
to implement swipe. There are a lot of things you could do here to
improve this (such as calculating how far off keys are from a finger
path or using different techniques altogether).

How it works: gen_ideal_words.py can be used to calculate ideal
paths a finger would take when swiping a word on a keyboard. For
usage, see gen.sh.

To actually use this, if you use a qwerty keyboard, for instance,
try "gen_ideal_words.py IDEAL_10000_qwerty". Swipe a word and hit
enter (unfortunately this isn't built into an event-based system
with timing, so you have to hit 'enter' to compute).
