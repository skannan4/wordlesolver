# Wordle Solver

### Introduction
The ostensible purpose of this project was to develop some simpler Wordle solvers in Python. The secondary goal was for me to refresh my Python skills a bit, since I really haven't play with it much since college and only intermittently used it in my grad school projects (R was just too convenient for seq). However, the *real* purpose of all of this was to procastinate on studying for my medicine shelf (which I eventually passed!). In that sense, it should be noted that this code is not optimized for speed, it is not optimized for pythonic quality - it is simply optimized for my amusement and entertainment.

A related point is that I'm sure word-searching is fairly well-studied, and that aside there are probably many people who have already come up with similar/better solvers (that's how `SOARE` became everyone's hipster opening, after all). There's also this [competition](https://github.com/Kinkelin/WordleCompetition) to improve Wordle solvers. My whole point was to look at none of that - I didn't want to put any more effort into this than I do playing Wordle anyway.

With that, here's what I've got.

### Different Solving Approaches

For clarity, the way I am displaying results here is in the form `[(0-2), (0-2), (0-2), (0-2), (0-2)]`, where `0` indicates no match (grey in Wordle), `1` indicates match in the wrong spot (yellow in Wordle), and `2` indicates complete match (green in Wordle). My default dictionary is a Scrabble dictionary taken from [Will McGugan] (https://twitter.com/willmcgugan/status/1478045889423941636), which has 8,672 5-letter words.

##### Random Solver

An easy starting point is a solver that just guesses the next word randomly. Here's an example of the solver trying to guess `aroma`, which was a previous solution.

```
Playing computer vs computer game, random mode!
Using input word!
aroma
There are 8672 possible guesswords remaining
Guessword is slank
[0, 0, 1, 0, 0]
There are 715 possible guesswords remaining
Guessword is circa
[0, 0, 1, 0, 2]
There are 17 possible guesswords remaining
Guessword is opera
[1, 0, 0, 1, 2]
There are 1 possible guesswords remaining
Guessword is aroma
[2, 2, 2, 2, 2]
It took the computer 4 guesses to correctly guess the word in random mode.
```
