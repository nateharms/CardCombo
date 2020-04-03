import os, sys
import requests
from bs4 import BeautifulSoup

parent_url = 'https://www.cardratings.com/credit-card-list.html'
res = requests.get(parent_url)
html_page = res.content
print(sys.getsizeof(html_page))
soup = BeautifulSoup(html_page, 'html.parser')
cc_urls = []
for link in soup.find_all('a', href=True):
    if 'cardratings.com/credit-card/' in link.get('href'):
        print(link.get('href'))
        cc_urls.append(link.get('href'))

def get_size(url):
    res = requests.get(url)
    html_page = res.content
    print(url)
    size = sys.getsizeof(html_page)
    return size

size = 0
for cc_url in cc_urls:
    if cc_url == "https://www.cardratings.com/credit-card/connect-classic":
        continue # known to be broken url
    size += get_size(cc_url)
    print(size)
    print()

print(f'Final size: {size}')
