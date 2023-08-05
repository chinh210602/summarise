import requests
from bs4 import BeautifulSoup
from datetime import *

class Scaper():
    def __init__(self):
        pass
    
    def scape(self, url_list):
        tmp_dict = {}
        for url in url_list:
            html_text = requests.get(url).text
            soup = BeautifulSoup(html_text, "lxml")
            #Title
            try:
                title = soup.find('h1', class_ = 'title-detail').text
            except:
                print("Can't find any title")
                title = None
            #Date
            try:
                date = soup.find('span', class_ = 'date').text
                day = str(datetime.strptime(date.split(', ')[1], '%d/%m/%Y').date())
            except:
                print("Can't find published date")
                day = None

            #Body
            try:
                descript = soup.find('p', class_ = 'description').text 
            except:
                print("Can't find description")
                descript = None
            try:
                chunks = soup.find_all('p', class_ = 'Normal')
                chunks = [chunk.text for chunk in chunks]
            except:
                print("Can't find any body of text")
                chunks = None
            tmp_dict[(url, day, title)] = [descript] + chunks

        return tmp_dict
