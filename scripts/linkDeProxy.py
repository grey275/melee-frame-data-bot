import re
import sys

import requests
import fuzzywuzzy

from bs4 import BeautifulSoup

import sheets
import serviceAccount



example_page_url = "https://smashboards.com/threads/complete-marth-hitboxes-and-frame-data.285324/#post-11073667"


def getPage(url_file):
    response = requests.get(url_file)
    # parse html
    return str(BeautifulSoup(response.content))


def findPageGifs(page):
    """
    :param page: html of web page (here: Python home page)
    :return: urls in that page
    """
    gifs = set()
    while True:
        gif = re.search("imgur.+?gif", page)
        if not gif:
            break
        print(gif)
        gifs.add("https://{}\n".format(gif.group(0)))
        if len(page) > gif.end():
            page = page[gif.end():]
        else:
            break
    return gifs

def findName(gif, page, moves):
    for move in moves:
        re.find("move")
def save(strings, output_file):
    with open(output_file, 'w') as f:
        for string in strings:
            pass
            # print(type(url))
            print(string)
            f.write(string+"\n")

def getMoveNamesFromSheet(char_name):
    pass

# session = serviceAccount.createSession()
# data = sheets.AllStructuredData()

def deProxy(url):
    addr = re.search("imgur.+?gif", url)
    addr = addr.group(0).replace("%2F", "/")
    return "https://{}".format(addr)

print(deProxy(sys.argv[1]))

# url, char_name = sys.argv[1:3]
# url = example_page_url
# page = getPage(url)
# print(page)
# gifs = findPageGifs(page)
# # named = findNames(gifs)
# save(gifs, "gifs.txt")
