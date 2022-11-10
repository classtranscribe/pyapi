import requests
from pkg.agent.tasks.lib.pythoncrawler import sources
from bs4 import BeautifulSoup
from string import ascii_lowercase

deaftec_site = sources.deaftec_site
deaftec_headers = sources.deaftec_headers
deaftec_base = sources.deaftec_base
deaftec_domains = sources.deaftec_domains
deaftec_ls_alphabet = sources.deaftec_ls_alphabet

def find_page(url, domain):  
    glossaries = []

    response = requests.get(url, headers=deaftec_headers)
    if response.status_code != 200:
        print("Cannot fetch this page...", response.status_code)

    else:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.findAll("h4", {"class": "dce-post-title"})
        for link in links: 
            term = link.find('a').contents[0].strip()
            video_url = str(link.find('a')['href'])
            glossaries.extend(find_video(video_url, domain, term))
    
    return glossaries

def find_video(url, domain, term):
    glossaries = []

    response = requests.get(url, headers=deaftec_headers)
    if response.status_code != 200:
        print("Cannot fetch this page...", response.status_code)

    else:
        soup_video = BeautifulSoup(response.content, 'html.parser')
        video_links = soup_video.findAll('video')
        video_descriptions = soup_video.findAll("div", {"class":"elementor-text-editor elementor-clearfix"})
        explanation = str(video_descriptions[0]).split('>')[1].strip().split('<')[0]
        example = str(video_descriptions[1]).split('>')[1].strip().split('<')[0]

        for i, link in enumerate(video_links): 
            video_url = str(link.get('src'))
            video_split = video_url.split('/')
            source_identifier = video_split[len(video_split)-1].split('.')[0]
            
            if i == 0:
                kind = '2'
                text = explanation
            else:
                kind = '3'
                text = example
            
            uuid = deaftec_site.lower() + '-' + domain.lower() + '-' + term.lower() + '-' + kind.lower() + '-' + source_identifier.lower()
            glossaries.append([deaftec_site, domain, term, kind, text, url, video_url, uuid])
    
    return glossaries

def crawler():
    glossaries = []
    for (combined, domain) in deaftec_domains:
        if combined == '':
            for c in deaftec_ls_alphabet:
                url = deaftec_base + c + '/'
                glossaries.extend(find_page(url, domain))
        else:
            for c in ascii_lowercase:
                url = deaftec_base + c + '-' + combined + '/'
                glossaries.extend(find_page(url, domain))
    
    return glossaries