from time import perf_counter

import numpy as np

from pkg.agent.tasks.lib.scenedetection.base import SceneDetectionAlgorithm


# Write algorithm code up here

class SimStructuralV1(SceneDetectionAlgorithm):

    def find_scenes(self, video_path):
        # Record how long the task takes and return that at the end
        start_time = perf_counter()

        self.logger.info('Given a video path, this method will parse the video to look for possible scene candidates.')


        self.logger.info('To run as a subprocess (in case of memory leaks), you can use self.run_as_subprocess')

        num_samples = 10
        # vr_full = decord.VideoReader(video_path, ctx=decord.cpu(0))

        timestamps = np.zeros(num_samples)
        everyN = 1

        # Now work in frames again. Make sure we are using regular ints (not numpy ints) other json serialization will fail
        frame_cuts = [int(s * everyN) for s in sample_cuts]

        # must return an array of timestamps, array of frame cut points, the sampling period, and the start time
        return timestamps, frame_cuts, everyN, start_time







