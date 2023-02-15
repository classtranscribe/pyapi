import logging
import wikipedia
import wikipediaapi
from nltk.corpus import wordnet as wn

logger = logging.getLogger('pkg.agent.tasks.lib.accessibleglossary')
wiki_en = wikipediaapi.Wikipedia('en')

PREFIXES = ['Dr', 'Gov', 'Miss', 'Mr', 'Mrs', 'Ms', 'Pres', 'Prof', 'Rep', 
            'Jr', 'Sr', 'Esq', 'Hon', 'Messrs', 'Mmes', 'Msgr', 'Rev', 'Sr', 'Rt']

def look_up_wordnet(term):
    '''
    Currently not in used
    '''
    wn_term = wn.synsets(term, pos = wn.NOUN)
    if len(wn_term) != 0:
        return wn_term[0].definition()
    else:
        return 'Not available'

def first_valid_period(sentence, prefixes=PREFIXES):
    if '.' not in sentence:
        return len(sentence)
    
    first_period = sentence.index('.')
    
    # Check for prefix abbreviations
    for pre in prefixes:
        pre_start = first_period - len(pre)
        if pre_start < 0:
            continue
        
        if sentence[pre_start : first_period] == pre:
            return first_period + 1 + first_valid_period(sentence[first_period + 1 :], prefixes)
    
    # Check for 12-hour clock
    prev_1 = sentence[first_period - 1] if first_period - 1 >= 0 else ''
    prev_2 = sentence[first_period - 2] if first_period - 2 >= 0 else ''
    next_1 = sentence[first_period + 1] if first_period + 1 < len(sentence) else ''
    
    prev_1 = prev_1.lower()
    prev_2 = prev_2.lower()
    next_1 = next_1.lower()
    
    if next_1 == 'm' and (prev_1 == 'a' or prev_1 == 'p'):
        return first_period + 1 + first_valid_period(sentence[first_period + 1 :], prefixes)
    if prev_1 == 'm' and prev_2 == '':
        return first_period + 1 + first_valid_period(sentence[first_period + 1 :], prefixes)
    
    return first_period

sentence1 = 'Mr. Eric is gently playing the guitar. He was enjoying the music.'
assert sentence1[0 : first_valid_period(sentence1) + 1] == 'Mr. Eric is gently playing the guitar.'

sentence2 = 'It is now 5:00 P.M. Let get sterted for dinner. Where are we going?'
assert sentence2[0 : first_valid_period(sentence2) + 1] == 'It is now 5:00 P.M. Let get sterted for dinner.'

def get_one_sentence_and_url(term):
    if wiki_en.page(term).exists() == False:
        return 'Not available', 'Not available', 'Not available'
    
    summary = wiki_en.page(term).summary
    url = wiki_en.page(term).fullurl
    first_period = first_valid_period(summary)
    sentence = summary[0: first_period + 1]
    if 'refer to:' in sentence or 'refers to:' in sentence:
        return 'Ambiguous meaning', 'Ambiguous meaning', url
    
    return sentence, summary, url

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

def new_look_up_wiki(term):
    integrated_result = []
    search_results = wikipedia.search(term).copy()
    if len(search_results) == 0:
        return integrated_result
    
    wiki_term = search_results[0]
    domains, filtered_results = get_domain_wiki(search_results)
    
    if len(filtered_results) == 0:
        return []
    else:
        formated_term = '_'.join(filtered_results[0].split(' '))
        sentence, summary, url = get_one_sentence_and_url(formated_term)
        if sentence == 'Ambiguous meaning' or sentence == 'Not available':
            return []
        else:
            return [filtered_results[0], sentence, 'General', 'Wikipedia', 'CC BY-SA', url, summary]

def look_up(phrase_hints):
    raw_terms = phrase_hints.splitlines()

    glossary = []
    for term in raw_terms:
        glossary.extend(new_look_up_wiki(term))

    return glossary