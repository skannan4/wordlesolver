# Wordle Solver

### Introduction
The ostensible purpose of this project was to develop some simpler Wordle solvers in Python. The secondary goal was for me to refresh my Python skills a bit, since I really haven't play with it much since college and only intermittently used it in my grad school projects (R was just too convenient for seq). However, the *real* purpose of all of this was to procastinate on studying for my medicine shelf (which I eventually passed!). In that sense, it should be noted that this code is not optimized for speed, it is not optimized for pythonic quality - it is simply optimized for my amusement and entertainment.

A related point is that I'm sure word-searching is fairly well-studied, and that aside there are probably many people who have already come up with similar/better solvers (that's how `soare` became everyone's hipster opening, after all). There's also this [competition](https://github.com/Kinkelin/WordleCompetition) to improve Wordle solvers. My whole point was to look at none of that - I didn't want to put any more effort into this than I do playing Wordle anyway.

With that, here's what I've got.

### Different Solving Approaches

For clarity, the way I am displaying results here is in the form `[(0-2), (0-2), (0-2), (0-2), (0-2)]`, where `0` indicates no match (grey in Wordle), `1` indicates match in the wrong spot (yellow in Wordle), and `2` indicates complete match (green in Wordle). My default dictionary is a Scrabble dictionary taken from [Will McGugan] (https://twitter.com/willmcgugan/status/1478045889423941636), which has 8,672 5-letter words.

##### Random Solver

An easy starting point is a solver that just guesses the next word randomly. Here's an example of the solver trying to guess `aroma`, which was a previous solution.

```
Playing computer vs computer game, random mode!
Using input word!
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

##### Max Frequency Solver

The next iteration would be one that looks for what letters most frequently occur in the remaining possible guesswords, and then tries to make a guessword that contains as many of those letters as possible. Note that there are usually multiple possible guesswords that could fulfill this criteria. Rather than selecting randomly, I just picked the one at the top of the list, both because I found that it didn't make a difference on average, and because I liked the determinism - it meant I could pick out a consistent guessing strategy. By the way, using this dictionary, the top letters in order are: s, e, a, o, r, i, l, n, t, d; this explains the popularity of openings like `soare` or, as my solver does here, `arose`. Here's the solver working on `caulk`.

```
Playing computer vs computer game, max mode!
Using input word!
There are 8672 possible guesswords remaining
Guessword is arose
[1, 0, 0, 0, 0]
There are 468 possible guesswords remaining
Guessword is inlay
[0, 0, 1, 1, 0]
There are 26 possible guesswords remaining
Guessword is caulk
[2, 2, 2, 2, 2]
It took the computer 3 guesses to correctly guess the word in max mode.
```

##### Half Frequency Solver

As mentioned above, I didn't think *too* carefully about my solving strategies, so another idea that I thought would be interesting is to use what I call a "Guess Who"-style half frequency solver. Basically, rather that using the *most frequently* appearing letters in the guessword, I wanted to use letters whose frequency was closest to 50%, so that the list would be more efficiently split. For the first guess or so, `arose` is still the most popular choice; however, with later guesses, I expected this would change. However, in reality, they actually guessed fairly similarly throughout, and benchmarking them also validated that.

![image](https://user-images.githubusercontent.com/28656813/156404797-430317c0-42d9-4685-aa42-e6bc2cae7387.png)
![image](https://user-images.githubusercontent.com/28656813/156404819-f0d6436f-2725-4516-b0cc-5956c4ee579f.png)

Mean guess here was 4.66 vs 4.62 respectively.

##### Sacrifice Guessing

The above strategies are intuitive and work for hard mode of Wordle. However, I don't play Wordle on hard mode (truthfully, I think it gets rid of the fun part of Wordle), and a key part of my tactic is "sacrifice guessing." This is where you guess a word that you know will be wrong to maximize testing new letters. However, a good question would be when to sacrifice guess and when to try and just get the word. To figure this out, I set in a threshold number of letters. If you know at or below the threshold number of letters in the keyword (regardless of position), you sacrifice guess; if not, you max frequency guess. (As an example, say the threshold is 2 - if you only know 0-2 letters of the keyword, you sacrifice guess). Note that your sacrifice guess can reuse earlier letters, you just try to avoid that! Because I always select the top word in the list if there are multiple options, I could come up with a favoured sacrifice guess approach. Based on the letter frequencies above, my preferred opening of `saint` -> `horde` is probably not the *most* optimal; the computer goes `arose` -> `blind` -> `caput`.

An example is below, using the randomly selected keyword `cured`.

```
Playing computer vs computer game, sacrifice mode!
Threshold is 2
A random word has been selected!
There are 8672 possible guesswords remaining
Guessword is arose
[0, 1, 0, 0, 1]
There are 283 possible guesswords remaining
Guessword is blind
[0, 0, 0, 0, 2]
There are 10 possible guesswords remaining
Guessword is cured
[2, 2, 2, 2, 2]
It took the computer 3 guesses to correctly guess the word in sacrifice mode.
The computer also used 1 sacrifice guesses.
```


