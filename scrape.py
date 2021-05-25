import requests
from bs4 import BeautifulSoup
import time


def webScrap(stringsearch):
    URL = "https://simbax.io/"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    if stringsearch in str(soup.text).lower():
        return True


#t0 = time.time()
#webScrap("T")
#t1 = time.time()
#print(t1-t0)
