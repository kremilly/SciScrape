#!/usr/bin/python3

from enum import Enum

class BuildUrls(Enum):
    
    BASE_URL = 'https://arxiv.org/'
    SEARCH_BASE = f'{BASE_URL}search'
    API_BASE = f"{BASE_URL.replace('//', '//export.')}api/"
    
    @classmethod
    def api_search(self, search_term, max_results):
        return f'{self.API_BASE.value}query?search_query={search_term}&max_results={max_results}'
    
    @classmethod
    def author_page_link(self, author_name):
        author = author_name.replace(' ', '+')
        return f'{self.SEARCH_BASE.value}?searchtype=author&query={author}&abstracts=show&order=-announced_date_first&size=50'

    @classmethod
    def category_search_link(self, category):
        return f'{self.API_BASE.value}query?search_query={category}&abstracts=show&order=-announced_date_first&size=50'

    @classmethod
    def source_link(self, abs_link):
        return abs_link.replace('pdf', 'src')
