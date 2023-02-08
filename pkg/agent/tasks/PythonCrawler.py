import json
import os
import requests
import time
from urllib.request import Request, urlopen 

from .AbstractTask import AbstractTask, TaskNames
from pkg.agent.tasks.lib import accessiblecrawler
from pkg.agent.tasks.lib.pythoncrawler import vimeodownload

ASLCORE_PATH = '/data/aslvideos/aslcore/original/'
DEAFTEC_PATH = '/data/aslvideos/deaftec/original/'
if os.path.exists(ASLCORE_PATH) == False:
    os.makedirs(ASLCORE_PATH)
if os.path.exists(DEAFTEC_PATH) == False:
    os.makedirs(DEAFTEC_PATH)

class PythonCrawler(AbstractTask):

    @staticmethod
    def get_name():
        return TaskNames.PythonCrawler
    
    def run_task(self, body, emitter):
        self.logger.info(' [.] PythonCrawler message recv\'d: %s' % body)
        source_id = body['Data']
        parameters = body.get('TaskParameters', {})
        force = parameters.get('Force', False)
        readonly = parameters.get('ReadOnly', False)
        self.logger.info(' [%s] PythonCrawler started on sourceId=%s...' % (source_id, source_id))

        raw_glossaries = accessiblecrawler.extract_raw_glossaries(source_id)

        num_glossary = len(raw_glossaries)
        if source_id == 't':
            num_glossary = 2

        for i in range(num_glossary):
            try:
                glossary_single = raw_glossaries[i]

                # remove '/' from the term
                if '/' in glossary_single[2]:
                    glossary_single[7] = glossary_single[7].replace('/', '')

                # Checked if this glossary has already been saved
                resp = requests.get(f'{self.target_host}/api/ASLVideo/GetASLVideosByUniqueASLIdentifier', 
                            headers={'Authorization': 'Bearer %s' % self.jwt}, 
                            params={'uniqueASLIdentifier' : glossary_single[7]})
                resp.raise_for_status()

                if len(resp.text) > 0:
                    print('Already Saved')
                else:
                    print('Not Saved')
                    # Save to Database
                    asl_id = ''
                    resp = requests.post(url='%s/api/ASLVideo' % (self.target_host),
                                            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.jwt},
                                            data=json.dumps({
                                                "term": glossary_single[2],
                                                "kind": glossary_single[3],
                                                "text": glossary_single[4],
                                                "websiteURL": glossary_single[5],
                                                "downloadURL": glossary_single[6],
                                                "source": glossary_single[0],
                                                "licenseTag": "RIT/NTID",
                                                "domain": glossary_single[1],
                                                "likes": 0,
                                                "uniqueASLIdentifier": glossary_single[7]
                                            }))
                    resp.raise_for_status()
                    data = json.loads(resp.text)
                    asl_id = data['id']

                    # Download
                    if glossary_single[0] == 'ASLCORE':
                        vimeodownload.download_vimeo_video(glossary_single[6], glossary_single[5], ASLCORE_PATH, glossary_single[7])
                    
                    elif glossary_single[0] == 'DeafTEC':
                        video_request = Request(glossary_single[6])
                        video_request.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0')
                        video_content = urlopen(video_request).read()

                        with open(os.path.join(DEAFTEC_PATH , glossary_single[7] + '.mp4'), 'wb') as f:
                            f.write(video_content)
                    
                    # Connect ASLVideos to Glossary
                    resp = requests.get(f'{self.target_host}/api/Glossary/GetGlossaryByTerm', 
                                        headers={'Authorization': 'Bearer %s' % self.jwt}, 
                                        params={'term' : glossary_single[2]})
                    resp.raise_for_status()
                    # data is a list
                    data = json.loads(resp.text)

                    for g in data:
                        g_id = g['id']
                        resp = requests.post(url='%s/api/ASLVideoGlossaryMap' % (self.target_host),
                                            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.jwt},
                                            data=json.dumps({
                                                "glossaryId": g_id,
                                                "aslVideoId": asl_id,
                                                "published": True
                                            }))
                        resp.raise_for_status()
                        
                for entry in glossary_single:
                    print(entry)
                print('')

            except Exception as e:
                self.logger.error(' [%s] PythonCrawler failed to look up for a specific term: %s' % (source_id, str(e)))
                return

        self.logger.info(' [%s] PythonCrawler complete!' % source_id)

        return