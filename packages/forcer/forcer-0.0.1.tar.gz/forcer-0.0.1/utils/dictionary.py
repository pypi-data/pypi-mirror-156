from requests import get

from bs4 import BeautifulSoup

class Dictionary:
    def __init__(self) -> None:
        page = get("https://github.com/danielmiessler/SecLists/blob/master/Passwords/2020-200_most_used_passwords.txt")
        soup = BeautifulSoup(page.content, features='html.parser')
        self.__most_used_password = soup.find_all('td', class_='blob-code blob-code-inner js-file-line')
        
    def get_passwords(self) -> list:
        return [password.text for password in self.__most_used_password]