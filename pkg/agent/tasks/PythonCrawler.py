import json
import os
import requests
import time

from .AbstractTask import AbstractTask, TaskNames

#from pkg.agent.tasks.lib import accessibleglossary

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

        self.logger.info(' [%s] PythonCrawler complete!' % source_id)

        return