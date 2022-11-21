from pkg.agent.tasks.lib.pythoncrawler import aslcore
from pkg.agent.tasks.lib.pythoncrawler import deaftec

def extract_raw_glossaries(source_id):
    raw_glossaries = []
    if source_id == '0':
        raw_glossaries.extend(aslcore.crawler())
        raw_glossaries.extend(deaftec.crawler())
    elif source_id == '1':
        raw_glossaries.extend(aslcore.crawler())
    elif source_id == '2':
        raw_glossaries.extend(deaftec.crawler())
    
    return raw_glossaries
