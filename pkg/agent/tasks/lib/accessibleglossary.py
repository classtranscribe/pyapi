import logging
import wikipediaapi

logger = logging.getLogger('pkg.agent.tasks.lib.accessibleglossary')
wiki_en = wikipediaapi.Wikipedia('en')

def get_one_sentence_description(term):
    summary = wiki_en.page(term).summary
    firstPeriod = summary.index('.') if '.' in summary else len(summary) - 1
    sentence = summary[0: firstPeriod + 1]
    return sentence

def look_up(phrase_hints):
    raw_terms = phrase_hints.splitlines()

    extracted_terms = []
    descriptions = []

    for term in raw_terms:
        if wiki_en.page(term).exists():
            extracted_terms.append(term)
            descriptions.append(get_one_sentence_description(term))
    
    for i in range(len(extracted_terms)):
        print(str(extracted_terms[i]) + ' -> ' + str(descriptions[i]))

    return extracted_terms, descriptions