from bs4 import BeautifulSoup
import numpy as np
from datetime import date,timedelta
import pandas as pd
import requests

class WSJScraper():

    """
    This is our WebScraper Class. As of right now it will only parse through the Wall Street Journal
    Archive Website to build text data sets about any given topic, in a given date range
    In the future this class will be expanded to include other news sources, and also build text data sets
    from other sites like Instagram, Reddit, Wikipedia, YouTube,etc.
    """

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0 '}


    def __init__(self,start_date,end_date,topics=[]):
        """
        Initial constructor. Use this constructor for now when gathering text data from news sources,
        which as of right now we are only web scraping from the WSJ News Archive Website.
        For now format of start and end date is YYYY/MM/DD
        """
        self.start_date = start_date
        self.end_date = end_date
        self.topics = topics

    def get_dates_array(self):
        """
        Will return all days between the range of dates passed into the constructor as a numpy array
        """

        start_year,end_year = int(self.start_date.split('/')[0]),int(self.end_date.split('/')[0])
        start_month,end_month = int(self.start_date.split('/')[1]),int(self.end_date.split('/')[1])
        start_day,end_day = int(self.start_date.split('/')[2]),int(self.end_date.split('/')[2])

        start_date = date(start_year,start_month,start_day)
        end_date = date(end_year,end_month,end_day)

        date_delta = end_date - start_date
        dates_array = np.array([start_date + timedelta(days=i) for i in range(date_delta.days + 1)])
        return dates_array

    def generate_wsj_archive_urls(self):
        """
        Will return all relevant page urls (not actual article urls yet) from the relevant date on WSJ archive site
        as a numpy array
        """
        dates_array = self.get_dates_array()
        base_url_format = 'https://www.wsj.com/news/archive/'
        url_array = np.array([base_url_format + str(dates_array[i]).replace('-','/')
                              for i in range(len(dates_array))])

        return url_array

    def get_num_pages_wsj(self):
        """
        For the given url in our array resulting for the generate_wsj_archive_urls method, we can get the number of
        pages of news stories on that given page so that we can go through each page. Is broken for now
        """
        pass

    def get_article_urls(self):

        """
        Returns an array of all article urls that are relevant to the list of topics passed in the constructor
        """

        wsj_date_urls = self.generate_wsj_archive_urls()
        article_urls = np.array([])

        for url in wsj_date_urls:
            req = requests.get(url,headers=self.headers)
            soup = BeautifulSoup(req.content,'lxml')
            links = soup.find_all('a')
            for link in links:
                try:
                    if len(link.attrs['class']) == 0:
                        article_title_as_list = link.text.lower().split(' ')
                        for word in article_title_as_list:
                            if word in self.topics:
                                article_urls = np.append(article_urls,link.attrs['href'])
                except KeyError:
                    pass

        return article_urls

    def get_article_contents(self):

        """"
        Returns a summary of all relevant articles based on the list of topics passed in the constructor
        """

        article_urls = self.get_article_urls()
        article_contents = np.array([])

        for url in article_urls:
            req = requests.get(url,headers=self.headers)
            soup = BeautifulSoup(req.content,'lxml')
            meta_tags = soup.find_all('meta')
            for meta_tag in meta_tags:
                try:
                    if meta_tag.attrs['name'] == 'article.summary':
                        article_contents = np.append(article_contents,meta_tag.attrs['content'])
                except KeyError:
                    pass

        return article_contents

scraper = WSJScraper('2020/12/01','2020/12/24',topics=['election','voter','fraud','president','trump','presidency'
                                                        'nsa','polls','fbi','cia','biden','white','house'])

articles = scraper.get_article_contents()
for article in articles:
    print(article + '\n')

