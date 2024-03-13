#!/usr/bin/python3

import json, requests
import xml.etree.ElementTree as ET

from utils.str_utils import StrUtils

from arxiv.build_urls import BuildUrls

class AxivBuild:
    
    @classmethod
    def get_json(self, search: str, max_results: int) -> object:
        url = BuildUrls.api_search(
            search.replace('', '+'), max_results
        )
        
        response = requests.get(url)

        if response.status_code == 200:
            root = ET.fromstring(response.content)

            articles = []

            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                article_data = {}

                article_data['title'] = StrUtils.clean_string(
                    entry.find('{http://www.w3.org/2005/Atom}title').text
                )

                article_data['authors'] = [
                    {
                        'name': StrUtils.fix_unicode_name(author), 
                        'link': BuildUrls.author_page_link(author)
                    } for author in [
                        author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')
                    ]
                ]

                article_data['categories'] = [
                    {
                        'name': category, 
                        'link': BuildUrls.category_search_link(category)
                    } for category in [
                        category.get('term') for category in entry.findall('{http://www.w3.org/2005/Atom}category')
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

            return json.dumps({
                'data': articles,
                'status_code': response.status_code
            }, indent = 2)
        else:
            return json.dumps({
                'status_code': response.status_code
            }, indent = 2)
