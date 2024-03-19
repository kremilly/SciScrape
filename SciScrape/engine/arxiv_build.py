#!/usr/bin/python3

import json, time, requests

import xml.etree.ElementTree as ET

from utils.str_utils import StrUtils

from configs.settings import Settings

from configs.build_urls import BuildUrls

class ArxivBuild:
    
    @classmethod
    def calculate_request_time(self, start_time: time, end_time: time) -> str:
        elapsed_time_seconds = end_time - start_time
        
        return str(
            round(elapsed_time_seconds * 1000)
        )+ ' ms'
    
    @classmethod
    def make_request(self, search: str, max_results: int) -> object:
        url = BuildUrls.api_search(
            search.replace(' ', '+'), max_results
        )
        
        if Settings.get('general.enable_cache', 'BOOLEAN'):
            return requests.get(url, headers={
                'Cache-Control': 'no-cache'
            })
            
        return requests.get(url)
    
    @classmethod
    def get_json(self, search: str, max_results: int) -> object:
        start_time = time.time()
        
        response = self.make_request(search, max_results)
        
        end_time = time.time()

        if response.status_code == 200:
            root = ET.fromstring(response.content)

            articles = []

            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                article_data = {}

                article_data['title'] = StrUtils.clean_string(
                    entry.find('{http://www.w3.org/2005/Atom}title').text
                )

                el_authors = entry.findall('{http://www.w3.org/2005/Atom}author')
                article_data['authors'] = [
                    {
                        'name': StrUtils.fix_unicode_name(author), 
                        'link': BuildUrls.author_page_link(author)
                    } for author in [
                        author.find('{http://www.w3.org/2005/Atom}name').text for author in el_authors
                    ]
                ]

                el_categories = entry.findall('{http://www.w3.org/2005/Atom}category')
                article_data['categories'] = [
                    {
                        'name': category, 
                        'link': BuildUrls.category_search_link(category)
                    } for category in [
                        category.get('term') for category in el_categories
                    ]
                ]

                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                if summary:
                    article_data['summary'] = StrUtils.clean_string(summary)

                article_links = {}
                for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                    link_type = link.get('title')
                    link_href = link.get('href')
                    
                    if link_type == 'pdf':
                        article_links['pdf'] = link_href
                        article_links['src'] = BuildUrls.source_link(link_href)
                        
                    elif link_type == 'doi':
                        article_links['doi'] = link_href
                        
                    else:
                        article_links['page'] = link_href
                        
                article_data['links'] = article_links

                article_data['date'] = {
                    'published': entry.find('{http://www.w3.org/2005/Atom}published').text,
                    'updated': entry.find('{http://www.w3.org/2005/Atom}updated').text
                }

                articles.append(article_data)
                
            results_data = {
                'articles': articles,
                'total': len(articles),
                'status_code': response.status_code,
            }
        else:
            results_data['status_code'] = response.status_code
            
        if Settings.get('general.calculate_request_time', 'BOOLEAN'):
            results_data['calculate_request_time'] = self.calculate_request_time(start_time, end_time)

        return json.dumps(results_data, indent = 2)

    @classmethod
    def get_xml(self, search: str, max_results: int) -> object:
        json_data = self.get_json(search, max_results)
        xml_data = StrUtils.json_to_xml(json_data)   
        return ET.tostring(xml_data, encoding = 'unicode')
