#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 19:54:49 2022

@author: skannan4
Purpose: To experiment with different Wordle solvers in python. The secondary goals are to refresh some basic python coding (albeit without really embracing a clean, pythonic style) and to procrastinate from otherwise unpleasant work.
"""

#imports
import random
import numpy as np
from matplotlib import pyplot as plt
from statistics import mean
import pandas as pd
import seaborn as sns

#####Basic functions that are used in every part of this project#####

#load_words: Takes a newline-delineated file and imports it into python as a list to serve as a dictionary (whether for selecting a keyword or for aiding a solver)
    #parameters: filename, word_length; doprint - whether to print updates
    #returns: the loaded dictionary
def load_words(filename, word_length, doprint = True):
    dictionary = list()
    if doprint: print("Loading words from dictionary...")
    with open(filename) as f:
        for line in f:
            if len(line) == (word_length + 1):  #needed to length + 1 because of the newline character, I'm guessing?
                dictionary.append(line.rstrip("\n"))
    if doprint: print(len(dictionary), "words loaded.")
    return dictionary

#compare_words: My approach for word matching as done in wordle. The output of this is of form [0-2, 0-2, 0-2, 0-2, 0-2], where 0 means no match (grey in wordle), 1 means letter in the wrong spot (yellow in wordle), and 2 means exact match (green in wordle). The tricky part is how to handle all those multi-letter words. I used a goofy system to mark when a letter was a match in the keyword, so that a repeat letter in the guessword wouldn't trigger a match.
    #parameters: keyword - this is the correct answer; guessword - this is the guess; word_length
    #returns: the comparison between keyword and guessword in the form [0-2, 0-2, 0-2, 0-2, 0-2]
def compare_words(keyword, guessword, word_length):
    compare = [0] * word_length
    keyword = list(keyword)
    guessword = list(guessword)
    for i in range(0, word_length):
        if guessword[i] == keyword[i]:
            compare[i] = 2
            keyword[i] = 0
    for i in range(0, word_length):
        if (guessword[i] in keyword) and (keyword[i] != 0):
            compare[i] = 1
    return compare

#trim_dict: So I admit in advance that I used the word "dictionary" to refer to multiple entities, which is probably quite annoying (made worse by the fact that these dictionaries aren't python's dictionary structure). Here, in this function, the dictionary refers to the source of guesswords for the computer. After a given guess, the only words that should remain in the dictionary are words that would produce the same output as the keyword when compared against the guessword. This function trims the dictionary to only those words and returns the trimmed list.
    #parameters: dictionary - this is the current source of guesswords; guessword - this is the most recent guess that produced some comparison output; compare - this is the actual comparison output (the output of compare_words), word_length
    #returns: the dictionary after it has been trimmed based on the current guess
def trim_dict(dictionary, guessword, compare, word_length):
    for word in list(dictionary):
        if compare_words(word, guessword, word_length) != compare:
            dictionary.remove(word)
    return dictionary

#count_chars: This function is used in the half and max guessers. It calculates the frequency of each letter within words of a dictionary (normalized to the number of words) - thus, in a sense, it tells you what percentage of words remaining in the dictionary have a given letter (albeit not exactly because of repeat letters; I didn't really care to adjust for this for these simple purposes).
    #parameters: dictionary (which here likely refers to the source of guesswords)
    #returns: a dict (e.g. the python data structure, lol) with frequencies of occurrence for each letter
def count_chars(dictionary):
    count = dict.fromkeys(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'], 0)
    for char in "".join(dictionary):
        count[char] += 1/len(dictionary)
    return count

#####Functions used to form a new guessword#####
#Note - this doesn't include the random guesser because that's just a one-liner

#guess_max: This guesser uses the principle that the guessword should contain as many of the most frequently appearing letters left in the dictionary (again, here to mean the source of guesswords). Note that the guessword needn't necessarily contain all n of the top occurring letters - it just tries to get as many as possible. When there are multiple equally valid options, it just selects the first one rather than randomly choosing (see below on guess_half for explanation).
    #parameters: dictionary of source guesswords (this will be progressively trimmed by trim_dict); word_length
    #returns: a guessword as above
def guess_max(dictionary, word_length):
    topn = list(dict(sorted(count_chars(dictionary).items(), key = lambda t: t[1], reverse = True)[0:word_length]).keys()) #ake the output of count_chars, sort it from highest to lowest by frequency, take the top n keys (n being the word length), and get a list out of it
    dictionary_count = dict.fromkeys(dictionary, 0) #Run through the dictionary and count how many times each word has one of those top letters
    for word in dictionary:
        for letter in topn:
            if letter in word: 
                dictionary_count[word] += 1
    return max(dictionary_count.items(), key = lambda t: t[1])[0] #Just send the word with the max score

#guess_half: This guesser uses what I think of as the "Guess Who" principle - try to use letters that are as close to 50% frequency in the dictionary so you can split your list in half (kinda). So this takes the top n letters whose frequency is closest to 50%. At first, this will invariably also be the most common letters, but as your dictionary shrinks this won't be the case. As with guess_max above, it also just takes the guessword that has the most of your n selected letters, rather than randomly selecting between all equally valid options. I actually initially implemented a random selector (the code is below, commented out), but found that it didn't perform better, and I liked the determinism of this approach (it meant that I could pick out some common strategies).
    #parameters: dictionary of source guesswords (this will be progressively trimmed by trim_dict); word_length
    #returns: a guessword as above
def guess_half(dictionary, word_length):
    count_half = {k: abs(v-0.5) for k,v in count_chars(dictionary).items()} #subtract off 0.5 and take the absolute value to find the letters closest to 50% frequency
    topn = list(dict(sorted(count_half.items(), key = lambda t: t[1])[0:word_length]).keys()) #same as in guess_max but here taking the min n
    dictionary_count = dict.fromkeys(dictionary, 0)
    for word in dictionary:
        for letter in topn:
            if letter in word: 
                dictionary_count[word] += 1
    return max(dictionary_count.items(), key = lambda t: t[1])[0]

#In this version of guess_half, you find all words with the max number possible of your five letters of interest, and then randomly choose one of them, as opposed to just choosing the one at the top of the list. Performs similarly/sometimes worse. Note that this one is written only for five letter words; would need to be adjusted
#def guess_half(dictionary):
#    count_half = {k: abs(v-0.5) for k,v in count_chars(dictionary).items()}
#    top5 = list(dict(sorted(count_half.items(), key = lambda t: t[1])[0:5]).keys())
#    dictionary_count = dict.fromkeys(dictionary, 0)
#    for word in dictionary:
#        for letter in top5:
#            if letter in word: 
#                dictionary_count[word] += 1
#    max_value = max(dictionary_count.items(), key = lambda t: t[1])[1]
#    max_keys = list()
#    for key, value in dictionary_count.items(): 
#        if value == max_value:
#            max_keys.append(key)
#    print(max_keys)
#    return random.choice(max_keys)

#guess_sacrifice: This actually functions very similar to guess_max, because in the absence of sacrifice guessing, guess_max does better than random guessing (but about the same as guess_half, tbh). The logic is to first sort the list of letters by descending frequency, as in guess_max. But then you remove all of the letters from an input list, which will end up being the list of letters that have already been previously guessed. Then you take the top n letters, and try to form a guessword. Note that because you won't always use every one of these n letters in the guessword, you may end up repeating an old letter in the guessword - which is fine! The idea is to maximize new letters.
    #parameters: dictionary of source guesswords, letters_used - a list of all of the letters that should be removed from consideration (because they have already been guessed); word_length
    #returns: a guessword as above
def guess_sacrifice(dictionary, letters_used, word_length):
    topn = sorted(count_chars(dictionary).items(), key = lambda t: t[1], reverse = True)
    for letter in list(topn):
        if letter[0] in letters_used:
            topn.remove(letter)
    topn = list(dict(topn[0:word_length]).keys())
    dictionary_count = dict.fromkeys(dictionary, 0)
    for word in dictionary:
        for letter in topn:
            if letter in word: 
                dictionary_count[word] += 1
    return max(dictionary_count.items(), key = lambda t: t[1])[0]

#####Functions used to play a single game in a given mode#####

#play_game_human: Lol did we really need a human vs computer option in my crappy python text interface when there's already a very pretty GUI? Probably not, but this was a good practice of taking user input, plus useful in some very basic testing.
    #parameters: word_length; word - if not given, this selects a random word from the dictionary, but can also be input by the user; dictionary - this is the source of keywords and also the eventual source of guesswords. Defaults to the scrabble list that I downloaded from mathspp.
def play_game_human(word_length, word = "RANDOM", dictionary = "DEFAULT"):
    print("Playing human vs computer game!")
    if dictionary == "DEFAULT":
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length)
    dictionary = list(dictionary) #GAH python's assignment approach means I have to keep doing this
    if word == "RANDOM":
        keyword = random.choice(dictionary)
        print("A random word has been selected!")
    else:
        keyword = word
        print("Using input word!")
    print(keyword)
    current_compare = [0]*word_length
    guess = 0
    while(current_compare != [2]*word_length):
        guessword = input("Take a guess! ")
        guess += 1
        current_compare = compare_words(keyword, guessword, word_length)
        print(current_compare)
    print("It took you", guess, "guesses to correctly guess the word.")

#play_game_computer_rand: This is computer vs human/computer, using random selection to pick the next guessword. This effectively serves as the control group for all further testing.
    #parameters: word_length, word - if not given, this selects randomly from the dictionary, but can also be input by the user; dictionary - this is the source of keywords and also the eventual source of guesswords. Defaults to the scrabble list that I downloaded from mathspp; doprint - determines whether to print stuff (can be turned off for large n testing)
    #returns: the number of guesses it took to solve the puzzle
def play_game_computer_rand(word_length, word = "RANDOM", dictionary = "DEFAULT", doprint = True):
    if doprint: print("Playing computer vs computer game, random mode!")
    if dictionary == "DEFAULT":
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length, doprint)
    dictionary = list(dictionary) #GAH
    if word == "RANDOM":
        keyword = random.choice(dictionary)
        if doprint: print("A random word has been selected!")
    else:
        keyword = word
        if doprint: print("Using input word!")
    current_compare = [0]*word_length #This is the score for your most recent guess; starts at all 0s
    guess = 0 #number of guesses
    while(current_compare != [2]*word_length):
        if doprint: print("There are", len(dictionary), "possible guesswords remaining")
        guessword = random.choice(dictionary) #777 let's goooooooooooooo
        guess += 1
        if doprint: print("Guessword is", guessword)
        current_compare = compare_words(keyword, guessword, word_length) #update the current_compare
        if doprint: print(current_compare)
        dictionary= trim_dict(dictionary, guessword, current_compare, word_length) #trims the guessing dictionary based on your most recent guess
    if doprint: print("It took the computer", guess, "guesses to correctly guess the word in random mode.")
    return guess

#play_game_computer_max: This is computer vs human/computer, using the guess_max selection to pick the next guessword (e.g. based on most frequently appearing remaining letters). This, of course, functions in hard mode.
    #parameters: word_length, word - if not given, this selects randomly from the dictionary, but can also be input by the user; dictionary - this is the source of keywords and also the eventual source of guesswords. Defaults to the scrabble list that I downloaded from mathspp; doprint - determines whether to print stuff (can be turned off for large n testing)
    #returns: the number of guesses it took to solve the puzzle
def play_game_computer_max(word_length, word = "RANDOM", dictionary = "DEFAULT", doprint = True):
    if doprint: print("Playing computer vs computer game, max mode!")
    if dictionary == "DEFAULT":
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length, doprint = doprint)
    dictionary = list(dictionary) #GAAAH
    if word == "RANDOM":
        keyword = random.choice(dictionary)
        if doprint: print("A random word has been selected!")
    else:
        keyword = word
        if doprint: print("Using input word!")
    ifdoprint: print(keyword)
    current_compare = [0]*word_length #This is the score for your most recent guess; starts at all 0s
    guess = 0 #number of guesses
    while(current_compare != [2]*word_length):
        if doprint: print("There are", len(dictionary), "possible guesswords remaining")
        guessword = guess_max(dictionary, word_length) #Now using the max frequency letter approach
        guess += 1
        if doprint: print("Guessword is", guessword)
        current_compare = compare_words(keyword, guessword, word_length) #update the current_compare
        if doprint: print(current_compare)
        dictionary= trim_dict(dictionary, guessword, current_compare, word_length) #trims the guessing dictionary based on your most recent guess
    if doprint: print("It took the computer", guess, "guesses to correctly guess the word in max mode.")
    return guess

#play_game_computer_half: This is computer vs human/computer, using the guess_half selection to pick the next guessword (e.g. based on letters whose frequently is closest to 50% in the remaining list - e.g. to try and split the list effectively). This, of course, functions in hard mode.
    #parameters: word_length, word - if not given, this selects randomly from the dictionary, but can also be input by the user; dictionary - this is the source of keywords and also the eventual source of guesswords. Defaults to the scrabble list that I downloaded from mathspp; doprint - determines whether to print stuff (can be turned off for large n testing)
    #returns: the number of guesses it took to solve the puzzle
def play_game_computer_half(word_length, word = "RANDOM", dictionary = "DEFAULT", doprint = True):
    if doprint: print("Playing computer vs computer game, halving mode!")
    if dictionary == "DEFAULT":
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length, doprint = doprint)
    dictionary = list(dictionary) #GAAAH
    if word == "RANDOM":
        keyword = random.choice(dictionary)
        if doprint: print("A random word has been selected!")
    else:
        keyword = word
        if doprint: print("Using input word!")
    if doprint: print(keyword)
    current_compare = [0]*word_length #This is the score for your most recent guess; starts at all 0s
    guess = 0 #number of guesses
    while(current_compare != [2]*word_length):
        if doprint: print("There are", len(dictionary), "possible guesswords remaining")
        guessword = guess_half(dictionary, word_length) #Now using the half frequency letter approach
        guess += 1
        if doprint: print("Guessword is", guessword)
        current_compare = compare_words(keyword, guessword, word_length) #update the current_compare
        if doprint: print(current_compare)
        dictionary= trim_dict(dictionary, guessword, current_compare, word_length) #trims the guessing dictionary based on your most recent guess
    if doprint: print("It took the computer", guess, "guesses to correctly guess the word in halving mode.")
    return guess

#play_game_computer_sacrifice: This is computer vs human/computer, using sacrifice guessing. The notion of sacrifice guessing is to use a guessword containing previously unused letters (even if some of those letters are in the keyword) to try and maximize your chance of finding remaining letters. The question, however, becomes when to use sacrifice guessing -clearly once you have an idea of the word, you can go straight to try to figure it out using the info you have. In this function, I allow this to be parameterized by a threshold - at or below this threshold, you will sacrifice guess, but above it, you will use the max guessing strategy. The threshold is based on total number of letters that you have guessed so far (regardless of position). Of course, this method won't work in hard mode.
    #parameters: word_length; threshold - this is the maximum number of letters in the keyword that you can know such that you will still allow sacrifice guesses. Above this threshold, you switch to max guessing. (Why did I make this a less than or equals rather than just less than? Because I'm a dummy); word - if not given, this selects randomly from the dictionary, but can also be input by the user; dictionary - this is the source of keywords and also the eventual source of guesswords. Defaults to the scrabble list that I downloaded from mathspp; doprint - determines whether to print stuff (can be turned off for large n testing)
    #returns: a list where the first item is the number of guesses it took and the second item is the number of sacrifice guesses made
def play_game_computer_sacrifice(word_length, threshold, word = "RANDOM", dictionary = "DEFAULT", doprint = True):
    if doprint: print("Playing computer vs computer game, sacrifice mode!")
    if doprint: print("Threshold is", threshold)
    if dictionary == "DEFAULT":
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length, doprint = doprint)
    dictionary = list(dictionary) #GAAAAH
    full_dictionary = list(dictionary) #So this will be a list that DOES NOT CHANGE - that way, you sacrifice guesses can be pulled from the full dictionary and allow you to guess words that you know are wrong but can give more info
    letters_used = list() #Need this to be able to keep track of what letters you've used and try to avoid them in your sacrifice guesses
    if word == "RANDOM":
        keyword = random.choice(dictionary)
        if doprint: print("A random word has been selected!")
    else:
        keyword = word
        if doprint: print("Using input word!")
    current_compare = [0]*word_length #This is the score for your most recent guess; starts at all 0s
    max_compare = sum(1 for n in current_compare if n != 0) #you need to tabulate how many letters you have guessed in the word so far; when this exceeds your threshold, you switch to max guessing
    guess = 0 #number of guesses
    sacrifice_guess = -1 #number of sacrifice guesses - starts at -1 since by this definition your first guess is technically a sacrifice guess, but we don't want to count that
    prev_guessword = "" #use this to keep track of what letters you need to avoid in your sacrifice
    while(current_compare != [2]*word_length):
        if doprint: print("There are", len(dictionary), "possible guesswords remaining")
        if(max_compare <= threshold):
            guessword = guess_sacrifice(full_dictionary, letters_used, word_length) #here's where you sacrifice guess
            if guessword != prev_guessword: #This if statement is to avoid a weird situation that sometimes happened where it would keep guessing the wrong word over and over and over. I didn't quite work out why that happened, this just solved it without much fuss
                letters_used = letters_used + list(guessword) #add on all the letters from your recent guess to the avoid list
                sacrifice_guess += 1
                current_compare = compare_words(keyword, guessword, word_length)
                max_compare += sum(1 for n in current_compare if n != 0) #This updates how many total letters you now know
                prev_guessword = guessword
            else:
                guessword = guess_max(dictionary, word_length)
                current_compare = compare_words(keyword, guessword, word_length)
        else:
            guessword = guess_max(dictionary, word_length) #If you cross your threshold, time to go for the jugular with max guessing
            current_compare = compare_words(keyword, guessword, word_length)
        guess += 1
        if doprint: print("Guessword is", guessword)
        if doprint: print(current_compare)
        dictionary= trim_dict(dictionary, guessword, current_compare, word_length) #trim the dictionary whether you sacrifice guessed or not
    if doprint: print("It took the computer", guess, "guesses to correctly guess the word in sacrifice mode.")
    if doprint: print("The computer also used", sacrifice_guess, "sacrifice guesses.")
    return [guess, sacrifice_guess]

#####Functions that allow you to run a single mode multiple times (for simulations)#####

#computer_rand_sim: This simulates games of the random mode guesser.
    #parameters: n - number of simulations to be run. If a custom word list is provided, n is calculated as the length of that wordlist and the user input is ignored; word_length; word - If default, then it randomly selects n words from the dictionary, but it can also be a list provided by the user; doprint - whether you want results printed out from each of the individual games
    #returns: none
def computer_rand_sim(n, word_length, word = "RANDOM", dictionary = "DEFAULT", doprint = True):
    if dictionary == "DEFAULT":
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length, doprint = doprint)
    if word == "RANDOM":
        word = random.sample(dictionary, n)
    else: 
        n = len(word)
    guess_sim = [0]*n #number of guesses for each word in the list
    for i in range(0, n):
        print(i+1, end = " ")
        guess_sim[i] = play_game_computer_rand(word_length, word[i], dictionary, doprint)
    plt.hist(guess_sim, bins = np.arange(0, max(guess_sim) + 2, 1))
    plt.title("Random Guesser, n = %d" % n)
    plt.xlabel("# of Guesses")
    plt.ylabel("Frequency")
    plt.show()
    print("Average:", mean(guess_sim))
    print("Success %:", (sum(1 for n in guess_sim if n <= 6)/n) * 100)

#computer_max_sim: This simulates games of the max mode guesser.
    #parameters: n - number of simulations to be run. If a custom word list is provided, n is calculated as the length of that wordlist and the user input is ignored; word_length; word - If default, then it randomly selects n words from the dictionary, but it can also be a list provided by the user; doprint - whether you want results printed out from each of the individual games
    #returns: none
def computer_max_sim(n, word_length, word = "RANDOM", dictionary = "DEFAULT", doprint = True):
    if dictionary == "DEFAULT":
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length, doprint = doprint)
    if word == "RANDOM":
        word = random.sample(dictionary, n)
    else: 
        n = len(word)
    guess_sim = [0]*n #number of guesses for each word in the list
    for i in range(0, n):
        print(i+1, end = " ")
        guess_sim[i] = play_game_computer_max(word_length, word[i], dictionary, doprint)
    plt.hist(guess_sim, bins = np.arange(0, max(guess_sim) + 2, 1))
    plt.title("Maximum Guesser, n = %d" % n)
    plt.xlabel("# of Guesses")
    plt.ylabel("Frequency")
    plt.show()
    print("Average:", mean(guess_sim))
    print("Success %:", (sum(1 for n in guess_sim if n <= 6)/n) * 100)

#computer_half_sim: This simulates games of the half mode guesser.
    #parameters: n - number of simulations to be run. If a custom word list is provided, n is calculated as the length of that wordlist and the user input is ignored; word_length; word - If default, then it randomly selects n words from the dictionary, but it can also be a list provided by the user; doprint - whether you want results printed out from each of the individual games
    #returns: none
def computer_half_sim(n, word_length, word = "RANDOM", dictionary = "DEFAULT", doprint = True):
    if dictionary == "DEFAULT":
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length, doprint = doprint)
    if word == "RANDOM":
        word = random.sample(dictionary, n)
    else: 
        n = len(word)
    guess_sim = [0]*n #number of guesses for each word in the list
    for i in range(0, n):
        print(i+1, end = " ")
        guess_sim[i] = play_game_computer_half(word_length, word[i], dictionary, doprint)
    plt.hist(guess_sim, bins = np.arange(0, max(guess_sim) + 2, 1))
    plt.title("Half Guesser Guesser, n = %d" % n)
    plt.xlabel("# of Guesses")
    plt.ylabel("Frequency")
    plt.show()
    print("Average:", mean(guess_sim))
    print("Success %:", (sum(1 for n in guess_sim if n <= 6)/n) * 100)

#computer_sacrifice_sim: This simulates games of the sacrifice mode guesser for a particular, given threshold.
    #parameters: n - number of simulations to be run. If a custom word list is provided, n is calculated as the length of that wordlist and the user input is ignored; word_length; threshold (only uses one single threshold); word - If default, then it randomly selects n words from the dictionary, but it can also be a list provided by the user; doprint - whether you want results printed out from each of the individual games
    #returns: none
def computer_sacrifice_sim(n, word_length, threshold, word = "RANDOM", dictionary = "DEFAULT", doprint = True):
    if dictionary == "DEFAULT":
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length, doprint = doprint)
    if word == "RANDOM":
        word = random.sample(dictionary, n)
    else: 
        n = len(word)
    guess_sim = [0]*n #number of guesses for each word in the list
    sacrifice_sim = [0]*n #number of sacrifice guesses for each word in the list
    for i in range(0, n):
        print(i+1, end = " ")
        game = play_game_computer_sacrifice(word_length, threshold, word[i], dictionary, doprint)
        guess_sim[i] = game[0] #gets guesses
        sacrifice_sim[i] = game[1] #gets sacrifices
    plt.hist(guess_sim, bins = np.arange(0, max(guess_sim) + 2, 1))
    plt.title("Sacrifice Guesser, n = {n}, t = {t}".format(n = n, t = threshold))
    plt.xlabel("# of Guesses")
    plt.ylabel("Frequency")
    plt.show()
    plt.hist(sacrifice_sim, bins = np.arange(0, max(sacrifice_sim) + 2, 1))
    plt.title("Sacrifice Guesser, n = {n}, t = {t}".format(n = n, t = threshold))
    plt.xlabel("# of Sacrifice Guesses")
    plt.ylabel("Frequency")
    plt.show()
    print("Average:", mean(guess_sim))
    print("Sacrifices:", mean(sacrifice_sim))
    print("Success %:", (sum(1 for n in guess_sim if n <= 6)/n) * 100)
    
#####Functions that allow you to compare multiple modes for benchmarking#####

#computer_benchmark: Benchmarks all methods (random, max, half, sacrifice with thresholds up to and including the word length) for a single word length and a single dictionary. Includes some basic text and plotting for visualization. Note that the same keyword list is always used for each method.
    #parameters: n - number of simulations to be run. If a custom word list is provided, n is calculated as the length of that wordlist and the user input is ignored; wod_length; word - If default, then it randomly selects n words from the dictionary, but it can also be a list provided by the user; dictionary - uses the Scrabble dictionary by default as in previous functions; doprint - whether the individual games should print (set to False because it gets obnoxious quickly); verbose - whether to print text and graphing output from THIS function
    #returns: a list of lists containing, in order - a list of the names of all the methods used, mean guesses for each method, mean success rate for each method, and number of sacrifice guesses used for the sacrifice methods
def computer_benchmark(n, word_length, word = "RANDOM", dictionary = "DEFAULT", doprint = False, verbose = True):
    if dictionary == "DEFAULT":
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length, doprint = doprint)
    if word == "RANDOM":
        word = random.sample(dictionary, n)
    else: 
        n = len(word)
    #Initialize the number of guesses for each method; I'm sure I could combine these into one but for now I value my sanity
    random_guess = [0]*n
    half_guess = [0]*n
    max_guess = [0]*n
    sacrifice_guess = [[0 for count in range(n)] for count in range(word_length)] #This one has to be a list of lists to account for the different thresholds
    sacrifice_sacrifices = [[0 for count in range(n)] for count in range(word_length)] #Great variable name
    sacrifice_names = [0]*word_length #need these later for plotting, so dumb
    for i in range(0, n):
        print(i+1, end = " ")
        random_guess[i] = play_game_computer_rand(word_length, word[i], list(dictionary), doprint) #I have these list conversions here because previously, the play_game_computer functions didn't do it. But I'm still keeping them here because python scares me
        half_guess[i] = play_game_computer_half(word_length, word[i], list(dictionary), doprint)
        max_guess[i] = play_game_computer_max(word_length, word[i], list(dictionary), doprint)
        for j in range(0, word_length):
            temp_game = play_game_computer_sacrifice(word_length, j + 1, word[i], list(dictionary), doprint)
            sacrifice_guess[j][i] = temp_game[0]
            sacrifice_sacrifices[j][i] = temp_game[1]
            sacrifice_names[j] = "Sacrifice T" + str(j + 1) #need these later
    random_success = sum(1 for n in random_guess if n <= 6)/n
    half_success = sum(1 for n in half_guess if n <= 6)/n
    max_success = sum(1 for n in max_guess if n <= 6)/n
    sacrifice_success = [0]*word_length
    for i in range(0, word_length):
       sacrifice_success[i] = sum(1 for n in sacrifice_guess[i] if n <= 6)/n
    if verbose:
        print("")
        print("Random guess has average score", mean(random_guess), "with success %", random_success * 100)
        print("Max guess has average score", mean(max_guess), "with success %", max_success * 100)
        print("Half guess has average score", mean(half_guess), "with success %", half_success * 100)
        for i in range(0, word_length):
            print("Sacrifice guess with threshold", i + 1, "has average score", mean(sacrifice_guess[i]), "with average sacrifices" , mean(sacrifice_sacrifices[i]), "with success %", sacrifice_success[i] * 100)
        #Scatterplot of mean guess vs methods
        plt.scatter(["Random", "Max guess", "Half guess"] + sacrifice_names, [mean(random_guess)] + [mean(max_guess)] + [mean(half_guess)] + [mean(x) for x in sacrifice_guess])
        plt.xticks(rotation = 45)
        plt.xlabel("Method")
        plt.ylabel("Number of Average Guesses, n = %d" % n)
        plt.show()
        #Scatterplot of mean success vs methods
        plt.scatter(["Random", "Max guess", "Half guess"] + sacrifice_names, [random_success * 100] + [max_success * 100] + [half_success * 100] + [x*100 for x in sacrifice_success])
        plt.xticks(rotation = 45)
        plt.xlabel("Method")
        plt.ylabel("Success, n = %d" % n)
        plt.show()
        #Lineplot of number of sacrifice guesses per threshold
        plt.plot(range(1, word_length + 1), [mean(x) for x in sacrifice_sacrifices])
        plt.xticks(range(1, 6))
        plt.xlabel("Threshold for sacrifice guesses")
        plt.ylabel("Number of Sacrifice Guesses, n = %d" % n)
        plt.show()
    return [["Random", "Max guess", "Half guess"] + sacrifice_names, [mean(random_guess)] + [mean(max_guess)] + [mean(half_guess)] + [mean(x) for x in sacrifice_guess], [random_success * 100] + [max_success * 100] + [half_success * 100] + [x*100 for x in sacrifice_success], [mean(x) for x in sacrifice_sacrifices]]

#computer_benchmark_dictionaries: This is a multi-benchmarking function that I used to make some of the key visualization figures. This function benchmarks all of the methods for five different dictionaries: the scrabble dictionary, full wordle accepted dictionary, and words taken from top 10,000, 20,000, and 100,000 most common English words (from slightly different sources) - please see the Github for all of the sources. Because some of these dictionaries only contain 5 letter words, this function does not allow you to choose word length - it is hard-coded in as 5.
    #parameters: n - number of simulations to run; word - If left as "RANDOM" it will default to a random list taken from that specific dictionary, otherwise uses the input user list
    #returns: none
def computer_benchmark_dictionaries(n, word = "RANDOM"):
    dictionary_names = ["Scrabble dictionary", "Wordle Accepted Words", "10000 Most Common", "20000 Most Common", "100000 Most Common"]
    dictionary_list = [load_words("/home/skannan4/Downloads/WORD.LST", word_length = 5, doprint = False), load_words("/home/skannan4/Downloads/wordle.txt", word_length = 5, doprint = False), load_words("/home/skannan4/Downloads/10000w.txt", word_length = 5, doprint = False), load_words("/home/skannan4/Downloads/20000w.txt", word_length = 5, doprint = False), load_words("/home/skannan4/Downloads/100000w.txt", word_length = 5, doprint = False)]
    stats = pd.DataFrame() #Yeaaaaah let's do some dataframes! The R side of my brain is happy
    sacrifices = pd.DataFrame()
    for i in range(0, 5):
        print(dictionary_names[i])
        benchmark = computer_benchmark(n, word_length = 5, word = word, dictionary = list(dictionary_list[i]), doprint = False, verbose = False) #verbose off cuz no one wants to see all that crap
        stats = pd.concat([stats, pd.DataFrame(list(map(list, zip(*[benchmark[0], benchmark[1], benchmark[2], [dictionary_names[i]] * len(benchmark[0])]))), columns = ["Method", "Guesses", "Success", "Library"])]) #The right side of this basically just transposes the lists to get them into tidy format as a dataframe, then appends to main dataframe
        sacrifices = pd.concat([sacrifices, pd.DataFrame(list(map(list, zip(*[benchmark[0][3:], benchmark[3], [dictionary_names[i]] * len(benchmark[0][3:])]))), columns = ["Method", "Sacrifices", "Library"])])
        print("")
    #Scatterplot of guesses vs method by library used
    sns.catplot(x="Method", y="Guesses", hue="Library", kind = "swarm", data=stats)
    plt.xticks(rotation = 45)
    plt.show()
    #Boxplot of guesses vs method, ignoring library
    sns.catplot(x="Method", y="Guesses", kind = "box", color = "white", data=stats)
    plt.xticks(rotation = 45)
    plt.show()
    #Boxplot of success rate vs method
    sns.catplot(x="Method", y="Success", kind = "box", color = "white", data=stats)
    plt.xticks(rotation = 45)
    #Lineplot of number of sacrifices used based on threshold
    sns.catplot(x="Method", y="Sacrifices", hue="Library", kind = "point", data=sacrifices)
    plt.xticks(rotation = 45)
    
#computer_benchmark_wordlength: Benchmarks all of the methods on one dictionary at multiple word lengths (3-8). In theory, I could have probably made this such that the dictionary was choosable, but I got lazy and so the dictionary is hard-coded in as the scrabble dictionary.
    #parameters: n - number of simulations; word - If left as "RANDOM" it will default to a random list taken from that specific dictionary, otherwise uses the input user list
    #returns: none
def computer_benchmark_wordlength(n, word = "RANDOM"):        
    stats = pd.DataFrame()
    sacrifices = pd.DataFrame()
    for i in range(3, 9):
        dictionary = load_words("/home/skannan4/Downloads/WORD.LST", word_length = i, doprint = False)  
        print("Word Length", i)
        benchmark = computer_benchmark(n, word_length = i, word = word, dictionary = list(dictionary), doprint = False, verbose = False)
        stats = pd.concat([stats, pd.DataFrame(list(map(list, zip(*[benchmark[0], benchmark[1], benchmark[2], [i] * len(benchmark[0])]))), columns = ["Method", "Guesses", "Success", "Word Length"])])
        sacrifices = pd.concat([sacrifices, pd.DataFrame(list(map(list, zip(*[benchmark[0][3:], benchmark[3], [i] * len(benchmark[0][3:])]))), columns = ["Method", "Sacrifices", "Word Length"])])
        print("")
    sns.catplot(x="Word Length", y="Guesses", hue="Method", kind = "point", data=stats)
    plt.show()
    sns.catplot(x="Word Length", y="Success", hue="Method", kind = "point", data=stats)
    plt.show()
    