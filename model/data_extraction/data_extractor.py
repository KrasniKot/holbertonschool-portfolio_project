""" This module contains the class DataExtractor that holds methods to fetch the data to be used """

import json
import re

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from unidecode import unidecode


class DataExtractor:
    """ Defines a Data Extractor """

    def __init__(self, jsonfile=''):
        """ Initializes a Data Extractor
            - jsonfile .... json file to use
        """
        # DB Set up
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db     = self.client['laws_db']

        self.jsonfile = jsonfile
        self.laws     = None

    def fetch_json(self):
        """ Fetches a json file """
        with open(self.jsonfile, 'r') as f:
            self.laws = json.load(f)
            return self.laws

    def get_law_articles(self, url):
        """ Fetches a single page
            - url .... webpage's url to fetch
        """
        response = requests.get(url)  # Request to the webpage
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')  # Parse the HTML content

            articles = {}
            for h4 in soup.find_all('h4'):
                article_title = h4.text.strip()  # Extract article number

                if 'Artículo' in article_title:
                    article_key = article_title.replace('' '', '_').lower()
                    article_text = h4.find_next('pre').text.strip()  # Extract corresponding text
                    articles[article_key] = article_text

            return articles

        else:
            print('Could not fetch law', url, 'with code', response.status_code)

    def get_all_json_laws(self):
        """ Fetches information about all laws found in the json file and saves it into a json file """
        print('Fetching laws form from 01-01-2000 up to 01-01-2025...')

        lupdated_texts = self.db['laws-updated_texts']
        jsonfile = self.laws  # Retrieve the laws metadata

        # Iterate over the laws and store them
        for li, lmeta in enumerate(jsonfile):
            lnum = lmeta.get('Numero_de_Ley')
            lurl = lmeta.get('Texto_Actualizado')
            print(f'>>> Fetching law number {lnum:<8} in {lurl:<50} - {li:>5} out of {len(jsonfile):<5} ({li / len(jsonfile):<6.5f})...', end='\r')

            law = {'lnum': lnum, 'title': lmeta.get('Titulo'), 'articles': self.get_law_articles(lurl)}   # Create the dictionary to inster
            lupdated_texts.insert_one(law)  # Insert the law into de collection

        print()

    def get_constitution(self):
        """ Fetches the uruguayan constitution, articles and chapters """
        print('\nFetching Constitution...')
        fetching = {
            'CAPITULO': "",
            'SECCION': ""
        }

        self.__fetch_save_info('constitution_articles', 'https://www.impo.com.uy/bases/constitucion/1967-1967', fetching)

    def get_pcode(self):
        """ Fetches the uruguayan Penal Code """
        print('\nFetching Penal Code...')
        fetching = {
            'LIBRO': '',
            'CAPITULO': '',
            'TITULO': ''
        }

        self.__fetch_save_info('penal_code_articles', 'https://www.impo.com.uy/bases/codigo-penal/9155-1933', fetching)

    def get_ccode(self):
        """ Fetches the uruguayan Civil Code """
        print('\nFetching Civil Code...')
        fetching = {
            'LIBRO': "",
            'CAPITULO': "",
            'TIUTLO': "",
            'SECCION': ""
        }

        self.__fetch_save_info('civil_code_articles', 'https://www.impo.com.uy/bases/codigo-civil/16603-1994', fetching)

    def get_comcode(self):
        """ Fetches the uruguayan Commercial Code """
        print('\nFetching commercial code...')
        fetching = {
            'LIBRO': "",
            'CAPITULO': "",
            'TITULO': "",
            'SECCION': ""
        }

        self.__fetch_save_info('commercial_code_articles', 'https://www.impo.com.uy/bases/codigo-comercio/817-1865', fetching)

    def get_tcode(self):
        """ Fetches the uruguayan Tax Code """
        print('\nFetching Tax Code...')
        fetching = {
            'CAPITULO': "",
            'TIUTLO': "",
            'SECCION': ""
        }

        self.__fetch_save_info('tax_code_articles', 'https://www.impo.com.uy/bases/codigo-tributario/14306-1974', fetching)

    def get_cpcode(self):
        """ Fetches the uruguayan Criminal Procedure Code """
        print('\nFetching Criminal Procedure Code...')
        fetching = {
            'LIBRO': '',
            'CAPITULO': '',
            'TIUTLO': '',
            'SECCION': '',
        }
        self.__fetch_save_info('criminal_procedure_code_articles', 'https://www.impo.com.uy/bases/codigo-proceso-penal-2017/19293-2014', fetching)

    def get_gpcode(self):
        """ Fetches the uruguayan General Process Code """
        print('\nFetching General Process Code...')
        fetching = {
            'LIBRO': '',
            'CAPITULO': '',
            'TIUTLO': '',
            'SECCION': '',
        }
        self.__fetch_save_info('general_procedure_code_articles', 'https://www.impo.com.uy/bases/codigo-general-proceso/15982-1988', fetching)

    def __fetch_save_info(self, collection, url, fetching): 
        """ Fetches any given information and saves it
            - collection .... collection where data should be saved
            - url ........... url of the page where the data should be retrieved from
            - fetching ...... dictionary indicating the key for the attribute in the collection,
                              and the regex pattern to find the attribute values in the h4 heading
        """
        self.db[collection].drop() # Drop the collection if it already exists

        col      = self.db[collection]
        response = requests.get(url)    # Perform the request

        # If request was successful, then scrape the page
        if response.status_code == 200:
            art_data = {k: None for k in fetching.keys()}  # Main data to extract
            art_data['_id'] = 0

            soup = BeautifulSoup(response.content, 'html.parser')
            for tag in soup.find_all(['h3', 'h4']):
                if tag.name == 'h3':
                    text = tag.decode_contents()

                    # Remove the <pre> and </pre> tags from the text
                    text = text.replace('<pre>', '').replace('</pre>', '').strip()
                    text = re.sub(r'</?br\s*/?>', '||BR||', text)
                    text = text.split('||BR||')

                    for k, v in fetching.items():
                        for part in text:
                            part = part.strip()  # Clean up any excess whitespace

                            # Check if the current key is in the part of the text
                            if k.lower() in unidecode(part.lower()):
                                art_data[k] = re.sub(r'\s+', ' ', part.strip())  # Directly assign the part to art_data
                                break  # Exit after finding the first match for the key
                            
                elif tag.name == 'h4':
                    # Extract article number
                    article_text = tag.get_text(strip=True)
                    print('>>> Reading article:', article_text, end='\r')

                    # Get the corresponding <pre> for article content
                    next_pre = tag.find_next_sibling("pre")
                    article_content = next_pre.get_text(strip=True) if next_pre else ""

                    # Ensure previously extracted book/title data persists
                    art_data['_id']    += 1
                    art_data['article'] = article_text
                    art_data['content'] = re.sub(r'\s+', ' ', article_content)
                    col.insert_one(art_data)
            print()
        else:
            print('Could not fetch law, code', response.status_code)
