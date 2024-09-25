import json
from bs4 import BeautifulSoup
import basebrowser
import warnings 
warnings.filterwarnings("ignore")
import requests

class WebAutoBot(basebrowser.BaseBrowser):

    def __init__(self):
        super(WebAutoBot, self).__init__("Web Scrapper Bot", "www.kilimo.go.tz", use_ssl=True)

    def _execute(self):
        self.__search()

    def __search(self):
        url=self._get_base_url()
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.__parse_content(response.text)
            else:
                print(f"Failed to access the website. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    
    def __parse_content(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        machapisho_link = soup.find('a', title="Machapisho")
        
        if machapisho_link:
            href = machapisho_link.get('href')
            link_text = machapisho_link.get_text(strip=True)
            self.__fetch_machapisho_page(href)
        else:
            print("Machapisho link not found.")

    def __fetch_machapisho_page(self, machapisho_url):
        try:
            response = requests.get(machapisho_url)
            if response.status_code == 200:
                print(f"Successfully accessed Machapisho page: {machapisho_url}")
                self.__parse_machapisho_content(response.text)
            else:
                print(f"Failed to access the Machapisho page. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while accessing Machapisho page: {e}")

    def __parse_machapisho_content(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        paragraphs = soup.find_all('a')
        print("Content from Machapisho page:")
        for paragraph in paragraphs:
            print(paragraph.get_text())

        # You can extend this to scrape other specific content as needed
        # such as articles, links, or any other structured data

WebAutoBot()


