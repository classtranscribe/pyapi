import json
import os
import requests
import time

from .AbstractTask import AbstractTask, TaskNames

from pkg.agent.tasks.lib import accessibleglossary

VIDEO_GLOSSARY_KEY = 'glossary'
VIDEO_PHRASEHINTS_KEY = 'phraseHints'

VIDEO_SCENE_ID = 'SceneObjectDataId'
VIDEO_PH_ID = 'PhraseHintDataId'

class AccessibleGlossary(AbstractTask):

    @staticmethod
    def get_name():
        return TaskNames.AccessibleGlossary
    
    def generate_accessible_glossary(self, video_id, video, phrase_hints, readonly):
        # Look up definitions for generated phrases
        self.logger.info(' [%s] AccessibleGlossary looking up terms...' % video_id)
        
        ''' 
        TODO: 829 Check if terms has been looked up
        all_phrases = [str(scene[SCENE_PHRASES_KEY]) for scene in scenes]
        self.logger.debug(' [%s] PhraseHinter found phrases' % (video_id))
        '''

        try:
            self.logger.info(' [%s] AccessibleGlossary generating term descriptions...' % video_id)
            glossary = accessibleglossary.look_up(phrase_hints)

            if readonly:
                self.logger.info(' [%s] AccessibleGlossary running as READONLY.. term descriptions have not been saved: %s' % (video_id, terms.join('')))
            else:
                # save generated terms to glossary table in api
                self.jwt = self.update_jwt()
                resp = requests.post(url='%s/api/Task/UpdateGlossary?videoId=%s' % (self.target_host, video_id),
                                    headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.jwt},
                                    data=json.dumps({"Glossary": glossary}))
                resp.raise_for_status()

                # fetch offeringId for from videoId
                resp = requests.get(url='%s/api/Playlists/ByVideo/%s' % (self.target_host, video_id),
                                    headers={'Authorization': 'Bearer %s' % self.jwt})
                resp.raise_for_status()
                data = json.loads(resp.text)
                offeringId = data['offeringId']

                # fetch courseId for from offeringId
                resp = requests.get(url='%s/api/CourseOfferings/ByOffering/%s' % (self.target_host, offeringId),
                                    headers={'Authorization': 'Bearer %s' % self.jwt})
                resp.raise_for_status()
                data = json.loads(resp.text)
                courseId = data['id']

                # save glossary to the glossary table
                for g in glossary:
                    resp = requests.post(url='%s/api/Glossary' % (self.target_host),
                                        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.jwt},
                                        data=json.dumps({
                                            "term": g[0],
                                            "link": g[5],
                                            "description": g[1],
                                            "source": g[3],
                                            "licenseTag": g[4],
                                            "domain": g[2],
                                            "likes": 0,
                                            "shared": True,
                                            "editable": True,
                                            "courseId": courseId,
                                            "offeringId": offeringId
                                        }))
                    resp.raise_for_status()
                    data = json.loads(resp.text)
                    glossary_id = data['id']

                    # Connect Glossary to ASLVideos
                    resp = requests.get(f'{self.target_host}/api/ASLVideo/GetASLVideosByTerm', 
                                    headers={'Authorization': 'Bearer %s' % self.jwt}, 
                                    params={'term' : g[0]})
                    resp.raise_for_status()
                    # data is a list
                    data = json.loads(resp.text)

                    for asl in data:
                        resp = requests.post(url='%s/api/ASLVideoGlossaryMap' % (self.target_host),
                                        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.jwt},
                                        data=json.dumps({
                                            "glossaryId": glossary_id,
                                            "aslVideoId": asl['id'],
                                            "published": True
                                        }))
                        resp.raise_for_status()

            return video
        except Exception as e:
            self.logger.error(
                ' [%s] AccessibleGlossary failed to look up terms in videoId=%s: %s' % (video_id,
                    video_id, str(e)))
            return
    
    def run_task(self, body, emitter):
        self.logger.info(' [.] AccessibleGlossary message recv\'d: %s' % body)
        video_id = body['Data']
        parameters = body.get('TaskParameters', {})
        force = parameters.get('Force', False)
        readonly = parameters.get('ReadOnly', False)
        self.logger.info(' [%s] AccessibleGlossary started on videoId=%s...' % (video_id, video_id))

        # fetch video metadata by id to get path
        video = self.get_video(video_id=video_id)

        # short-circuit if we already have phrase hints
        # if not force and VIDEO_GLOSSARY_KEY in video and video[VIDEO_GLOSSARY_KEY]:
        if not force and VIDEO_PH_ID in video and video[VIDEO_PH_ID]:
            # TODO: trigger TranscriptionTask
            self.logger.warning(' [%s] Skipping AccessibleGlossary: glossary already exist' % video_id)
            return

        if video is None:
            self.logger.error(' [%s] AccessibleGlossary FAILED to lookup terms in videoId=%s' % (video_id, video_id))
            return

        # TODO: Check for empty phrases / error-handling
        # phrases = video[VIDEO_PHRASEHINTS_KEY]
        phrases = self.get_phrase_hints(video_id=video_id)

        if len(phrases) == 0:
            self.logger.error(' [%s] AccessibleGlossary FAILED for videoId=%s: no detected phrases found' % (video_id, video_id))

        self.generate_accessible_glossary(video_id, video, phrases, readonly)

        self.logger.info(' [%s] AccessibleGlossary complete!' % video_id)

        return