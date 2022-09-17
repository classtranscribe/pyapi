import logging
import wikipedia
import wikipediaapi
from nltk.corpus import wordnet as wn

logger = logging.getLogger('pkg.agent.tasks.lib.accessibleglossary')
wiki_en = wikipediaapi.Wikipedia('en')

def look_up_wordnet(term):
    '''
    Currently not in used
    '''
    wn_term = wn.synsets(term, pos = wn.NOUN)
    if len(wn_term) != 0:
        return wn_term[0].definition()
    else:
        return 'Not available'

def get_one_sentence_wiki(term):
    if wiki_en.page(term).exists() == False:
        return 'Not available'
    
    summary = wiki_en.page(term).summary
    firstPeriod = summary.index('.') if '.' in summary else len(summary) - 1
    sentence = summary[0: firstPeriod + 1]
    if ' may refer to:' in sentence:
        return 'Ambiguous meaning'
    
    return sentence

def get_domain_wiki(raw_results):
    domains = []
    filtered_results = []
    wiki_term = raw_results[0]
    
    for entry in raw_results:
        if '(' in entry and ')' in entry and entry.index('(') < entry.index(')'):
            start = entry.index('(') + 1
            end = entry.index(')')
            domain = entry[start : end]
            
            if entry[ : len(wiki_term)] != wiki_term:
                continue
            if domain == 'disambiguation':
                continue
            domains.append(domain)
        else:
            filtered_results.append(entry)
            
    return domains, filtered_results

def look_up_wiki(term):
    integrated_result = []
    search_results = wikipedia.search(term).copy()
    if len(search_results) == 0:
        return integrated_result
    
    wiki_term = search_results[0]
    domains, filtered_results = get_domain_wiki(search_results)
    for i in range(min(2, len(filtered_results))):
        formated_term = '_'.join(filtered_results[i].split(' '))
        integrated_result.append([filtered_results[i], get_one_sentence_wiki(formated_term), 'General', 'Wikipedia'])

    for domain in domains:
        formated_term = term + '_(' + '_'.join(domain.split(' ')) + ')'
        integrated_result.append([wiki_term, get_one_sentence_wiki(formated_term), domain, 'Wikipedia'])
        
    return integrated_result

def look_up(phrase_hints):
    raw_terms = phrase_hints.splitlines()

    glossary = []
    for term in raw_terms:
        glossary.extend(look_up_wiki(term))

    for i in range(len(glossary)):
        print(str(glossary[i][0]) + ' -> ' + str(glossary[i][1]) + ' -> ' + str(glossary[i][2]))

    return glossary