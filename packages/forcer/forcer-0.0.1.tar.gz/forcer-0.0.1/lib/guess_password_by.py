from sys import path
path.append('.')

from string import ascii_letters, digits
from random import choice

from utils import Dictionary

class GuessPasswordBy: 
    def random_string(self, length: int = 8) -> str:
        return ''.join(choice(ascii_letters + digits) for _ in range(length + 1))
    
    def dictionary(self) -> str:
        return Dictionary().get_passwords()