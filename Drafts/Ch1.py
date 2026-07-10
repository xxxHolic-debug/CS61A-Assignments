from urllib. request import urlopen

shakespear = urlopen('http://composingprograms.com/shakespeare.txt')

from math import sqrt

from operator import add, sub, mul, truediv

from math import pi

radius = 10
print(radius * radius * pi)
print(radius)
print('radius')

f = max
print( f(2,3,4) )

x = 2
x = x + 1
print(x)

area, circumference = pi * radius * radius, 2 * pi * radius
print(area)
print(circumference)

x, y = 3, 7
y, x = x, y
print(x)
print(y)



from operator import add, sub, mul, truediv
def square(x):
    return x * x
def average(x, y):
    return (x + y) / 2 

from operator import add, sub, mul, truediv
def square(x):
    return x * x