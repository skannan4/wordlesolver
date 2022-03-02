# Wordle Solver

### Introduction
The ostensible purpose of this project was to develop some simpler Wordle solvers in Python. The secondary goal was for me to refresh my Python skills a bit, since I really haven't play with it much since college and only intermittently used it in my grad school projects (R was just too convenient for seq). However, the *real* purpose of all of this was to procastinate on studying for my medicine shelf (which I eventually passed!). In that sense, it should be noted that this code is not optimized for speed, it is not optimized for pythonic quality - it is simply optimized for my amusement and entertainment.

A related point is that I'm sure word-searching is fairly well-studied, and that aside there are probably many people who have already come up with similar/better solvers (that's how `soare` became everyone's hipster opening, after all). There's also this [competition](https://github.com/Kinkelin/WordleCompetition) to improve Wordle solvers. My whole point was to look at none of that - I didn't want to put any more effort into this than I do playing Wordle anyway.

With that, here's what I've got.

### Different Solving Approaches
For clarity, the way I am displaying results here is in the form `[(0-2), (0-2), (0-2), (0-2), (0-2)]`, where `0` indicates no match (grey in Wordle), `1` indicates match in the wrong spot (yellow in Wordle), and `2` indicates complete match (green in Wordle). My default dictionary is a Scrabble dictionary taken from [Will McGugan](https://twitter.com/willmcgugan/status/1478045889423941636), which has 8,672 5-letter words.

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
### Benchmarking the Different Approaches
Ok - moment of truth. I tested each of the methods on 500 randomly selected words from the dictionary. Results are here:

![image](https://user-images.githubusercontent.com/28656813/156413034-6d2955f6-0d96-4904-bcbe-ab6fb0db5523.png)
![image](https://user-images.githubusercontent.com/28656813/156413045-b8c378cd-5385-40a4-bca9-a1c5aab83bf1.png)
![image](https://user-images.githubusercontent.com/28656813/156413063-d51a59df-938d-4a2e-9e91-1d2bec0a7a7e.png)

I think there were a couple of interesting and useful takeaways:
- Thankfully, both the max and half frequency solvers beat the random solver by a decent bit. Switching to the max solver saves an average of 1 letter every 3.25 words played. In this run, the max frequency solver marginally beat out the half frequency solver in both guesses (4.522/91.0% for max vs 4.576/89.6% for half), but I suspect this is within some margin of error.
- Sacrifice guessing at threshold 1 and 2 really didn't improve the guessing all that much compared to the max frequency solver - switching to sacrifice with threshold 2 saves 1 letter every 18.5 games with ~2% improvement in success rate. This was a somewhat unexpected result for me, given that I would think having more information would always be a good thing (in fact, I usually go `saint` -> `horde` nearly every game, unless I guess 4 letters right off the bat). I wonder if this is because with the max solver, the computer is already incredibly efficient at narrowing down remaining words in the dictionary. Of course, I don't use positional information, but I suspect that this wouldn't actually change things much. What *might* make the sacrifice guesser more efficient is making the decision to guess based on the number of words left in the dictionary instead.
- Obviously, sacrifice guessing at higher thresholds is bad - once the computer has enough letters, it should just start hunting for the win. (I plan on trying this approach myself, and not sacrifice guessing when I've already got three letters off of my first word).
- At threshold of 1, the sacrifice solver does one sacrifice guess every 2.85 games, while at threshold of 2 is does a sacrifice guess more or less every game. I wonder if there is more of a balancing act to the cost-benefit of sacrifice guessing than I imagined, which is why as above I wonder if the rationale to sacrifice guess should be based on number of remaining words in the dictionary rather than number of letters obtained.

##### Different Libraries
But wait - the results above also showed something else that was weird to me. Take the sacrifice solvers, at either threshold 1 or 2. They are both at about 4.45 guesses/word, with ~92-93% success rate. However, let's say I benchmark against myself (as noted, I only play on easy mode) - on 55 games, I'm at 3.8/100%. In short, I'm whooping all of my computers by quite a bit! That's not usually supposed to happen.

A quick look at the Scrabble dictionary gave me a potential explanation. Just looking at the top, there are words like `aahed`, `abhmo`, `adzes` etc. (I remember people throwing a fit over `cynic`!) In short, the solver not only might encounter more words than I am likely to see, but also has to eliminate more possibilities (certainly possibilities I wouldn't even need to consider) to get to simple answers. To test this possibility out, I explored several input dictionaries:

- Scrabble dictionary (as above) - 8,672 5-letter words
- Full Wordle [accepted list](https://github.com/Kinkelin/WordleCompetition/blob/main/data/official/combined_wordlist.txt) - 12,972 5-letter words (showcasing some wonderful words like `ohias`, `rewth`, and `jembe`)
- Top [10,000](https://github.com/first20hours/google-10000-english/blob/master/google-10000-english-usa.txt) and [20,000](https://github.com/first20hours/google-10000-english/blob/master/20k.txt) most common English words - 1,385 and 2,570 5-letter words respectively (the former list being a subset of the latter). This was generated by n-gram frequency analysis of the Google Trillion Word Corpus
- Top [100,000](https://github.com/Kinkelin/WordleCompetition/blob/main/data/other/common_words.txt) words, according to Wiktionary - 7,592 5-letter words (the full list is [here](https://gist.github.com/h3xx/1976236)

Just for record-keeping, here is the overlap in the lists (yes, done in R, which sort of defeats the spirit of Pythoning this, but good gosh the venn diagram options are so much easier in R...)

![test](https://user-images.githubusercontent.com/28656813/156440323-b6b909e1-db85-4559-938a-533ee1e097d9.png)

As you can see, the Scrabble list is largely encompassed by the Wordle list. The Wordle and top 100,000 lists each have their own pool of unique words (I have no idea what some of these Wordle words are, but many of the unique top 100,000 words appear of foreign origin). The Google project word lists have their own unique words, though many of them appear to be proper names.

So given these dictionaries, here were the benchmarking results:

![image](https://user-images.githubusercontent.com/28656813/156441391-5355d026-2f6a-4cb8-b778-0fe4a6035bf3.png)
![image](https://user-images.githubusercontent.com/28656813/156441463-ffa00770-cd7b-4a41-8dea-4016a918d516.png)
![image](https://user-images.githubusercontent.com/28656813/156441484-15ac1f73-3625-482b-ae86-1c693db4bca1.png)

Takeaways from this set of data would be:
- As expected, the average number of guesses was correlated with the dictionary size. Using the Sacrifice T1 as a guesser, the average guesses per game was ~3.6 for the top 10,000 dictionary, and ~3.75 for the 20,000, with close to 100% rates for both (not shown here). The latter isn't too far off from my own personal record, so I wonder if that suggests that I account for ~2500 words in my head when I play Wordle (which comes out to about 20% of Wordle's accepted dictionary, by the way).
- As above, the sacrifice approach really doesn't improve on max frequency guess; in fact, Sacrifice T2 seems to routinely perform a bit *worse* for the smaller dictionaries.

##### Word Length
When I was a kid, I used to play [Cows and Bulls](https://en.wikipedia.org/wiki/Bulls_and_Cows) with my family. This game is largely similar, except we would typically use four-letter words. Wordle, of course, uses 5. Right after the Wordle bubble started, I saw people start posting variations with much larger words, with the implication that these offered more of a challenge. I was a bit puzzled, since I figured there are fewer long words that fit any given pattern, and longer guesswords offer more information per guess. So I did a quick simulation to see how this actually plays out.

![image](https://user-images.githubusercontent.com/28656813/156452102-449c2f34-1e8e-4f66-840a-064d10368621.png)
![image](https://user-images.githubusercontent.com/28656813/156452114-ecfd14e9-65c6-4852-97ef-de4bd8e2b27d.png)

As I expected, longer words are actually *easier* to figure out than shorter ones.

### Ideas to Play With Later

- Changing the thresholding approach for sacrifice guessing to be based on what percentage of the dictionary is left. Might enable more efficient sacrifice guessing?
- I realised about halfway through this that there is a better approach to weighting guesswords - rather than counting how many letters from a desired list are in a potential guessword, one could weight by frequency. This could improve sacrifice guessing. As pointed out above, a common situation is `arose` -> `blind` -> `caput`, but `caput` isn't the optimal guess here since it reuses `a`. This is a consequence of how I do my weighting. However, I also wonder the degree to which it would matter, since it seems like going past one sacrifice guess is suboptimal anyway. This type of weighting could also make max frequency guessing just a bit better.
