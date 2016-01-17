#!/usr/bin/python

import random

def genPasswd(n):
    word_file = "words"
    wordList = open(word_file).read().splitlines()
    choices = len(wordList)

    passwd = ""
    for x in range(0,n):
        passwd = passwd + wordList[random.randint(0,choices)].lower().capitalize()
    return passwd

