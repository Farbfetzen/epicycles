"""This script is just for figuring out stuff."""


import math
import os
import pygame as pg
from time import time



p1 = (1, 2)
pn = ((3, 4), (5, 6), (7, 8), (3, 4), (5, 6), (7, 8), (3, 4), (5, 6), (7, 8), (3, 4), (5, 6), (7, 8), (3, 4), (5, 6), (7, 8), (3, 4), (5, 6), (7, 8))
p2 = (9, 10)

n = 10**7

start = time()
for i in range(n):
    foo = p1 + pn + p2
    #foo = (p1, *pn, p2)
end = time()

print(foo)
print(end - start)

bar = () + ((1, 2))
print(bar)