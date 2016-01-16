#!/usr/bin/python
from random import randint

colors = ["orange", "blue", "green", "gold", "silver", "purple", "red", "black", "brown", "white"]
animals = ["lion", "tiger", "bear", "eagle", "fox", "elephant", "racoon", "gator", "fish", "whale"]

x = randint(0, 9)
y = randint(0, 9)

print colors[x] + animals[y]
