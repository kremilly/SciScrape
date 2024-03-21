#!/usr/bin/python3

import json, time, requests

import xml.etree.ElementTree as ET

from utils.str_utils import StrUtils
from utils.file_size import FileSize

from configs.settings import Settings

from configs.build_urls import BuildUrls

from engine.arxiv_utils import ArxivUtils

class ArxivBuild:
    
    @classmethod
    def make_request(self, search: str, max_results: int) -> object:
        headers = {}
        default_user_agent = Settings.get('general.default_user_agent', 'STRING')
        
        url = BuildUrls.api_search(
            search.replace(' ', '+'), max_results
        )
        
        if default_user_agent != '':
            headers['User-Agent'] = default_user_agent
        
        if Settings.get('general.enable_cache', 'BOOLEAN'):
            headers['Cache-Control'] = 'no-cache'
        
        return requests.get(url, headers=headers)
    
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
                
                article_data['id'] = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1]

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
                        pdf_link = link_href
                        src_link = BuildUrls.source_link(link_href)
                        
                        article_links['pdf'] = {
                            'link': pdf_link,
                            'size': FileSize.remote_file(pdf_link),
                            'pages': ArxivUtils.get_pdf_page_count(pdf_link),
                        }
                        
                        article_links['src'] = {
                            'link': src_link,
                            'size': FileSize.remote_file(src_link)
                        }
                    
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
            results_data['calculate_request_time'] = ArxivUtils.calculate_request_time(start_time, end_time)

        return json.dumps(results_data, indent = 2)

    @classmethod
    def get_xml(self, search: str, max_results: int) -> object:
        json_data = self.get_json(search, max_results)
        dict_data = json.loads(json_data)
        xml_data = StrUtils.json_to_xml(dict_data)   
        return ET.tostring(xml_data, encoding='unicode')
