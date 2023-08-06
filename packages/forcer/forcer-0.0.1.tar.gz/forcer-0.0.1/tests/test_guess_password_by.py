from sys import path
path.append('.')

from pyforcer import GuessPasswordBy

print(GuessPasswordBy().random_string(length=8))

for password in GuessPasswordBy().dictionary():
    print(password)