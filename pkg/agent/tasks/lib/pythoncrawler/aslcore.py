import requests
from pkg.agent.tasks.lib.pythoncrawler import sources
from bs4 import BeautifulSoup

aslcore_domains = sources.aslcore_domains
aslcore_site = sources.aslcore_site
kind = '1'

def find_page(url):
    glossaries = []

    response = requests.get(url)
    if response.status_code != 200:
        print("Cannot fetch this page...")
    else:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        for link in links: 
            if str(link.get('href')).count('<a href=') == 0 and str(link.get('href')).count('?id') == 1:
                glossaries.extend(find_video(url + str(link.get('href'))))
    
    return glossaries

def find_video(url):
    glossaries = []

    response = requests.get(url)
    if response.status_code != 200:
        print("Cannot fetch this glossary...")
    else:
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            raw_term = soup.title.string.split('|')[0].strip()
            title_tag = soup.title.string.replace(" ", "").split('|')
            domain = title_tag[1].strip().replace(aslcore_site, "")

            term_splited = raw_term.split('/')
            for s_term in term_splited:
                term = s_term.strip()

                glossary_links = soup.findAll('iframe')
                for link in glossary_links:
                    if (link['src'] != 'https://player.vimeo.com/video/'):
                        source_identifier = link['src'].replace('https://player.vimeo.com/video/', "")
                        uuid = aslcore_site.lower() + '-' + domain.lower() + '-' + term.lower() + '-' + kind.lower() + '-' + source_identifier.lower()

                        glossaries.append([aslcore_site, domain, term, kind, term, url, link['src'], uuid])
        
        except:
            print("An exception occurred when processing the following url", url)
    
    return glossaries

def crawler():
    glossaries = []
    for domain_url in aslcore_domains:
        glossaries.extend(find_page(domain_url))
    
    return glossaries

