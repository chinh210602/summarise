import requests
from bs4 import BeautifulSoup
import lxml

class GetUrls():
    def __init__(self, father_urls) -> None:
        self.father_urls = father_urls
        
    def getlist(self, number_of_news):
        """
        number_of_news: The number of news to scape from the Father URL

        return list of Child URL scape from Father URL
        """
        child_urls = [] #Contain the URLs
        #Loop and scrape URL of the latest news on the original URL
        for newspaper_url in self.father_urls:
            newspaper_html = requests.get(newspaper_url).text
            newspaper_soup = BeautifulSoup(newspaper_html, 'lxml')
            news_title = newspaper_soup.find_all('h2', class_ = 'title-news')
            for i, new_title in enumerate(news_title):
                if i == number_of_news:
                    break
                new_url = new_title.find('a')['href']
                child_urls.append(new_url)
        return child_urls
    
# get_urls = GetUrls(father_urls = ["https://vnexpress.net/kinh-doanh/vi-mo"])
# print(get_urls.getlist(2))