from time import perf_counter

from pkg.agent.tasks.lib.scenedetection.base import SceneDetectionAlgorithm




# Write static code here




class ExampleV1(SceneDetectionAlgorithm):

    def find_scenes(self, video_path):
        """
        The main method of the SceneDetectionAlgorithm. Override this in your subclass.

        Parameters:
        video_path (string): Video path

        Returns:
        string: Features of detected scenes
        """
        # This should return an array of scenes
        scenes = []

        start_time = perf_counter()

        self.logger.info('Given a video path, this method will parse the video and build up a list of scenes.')

        self.logger.info('To run a method as a subprocess (in case of resource leaks), '
                         'you can use self.run_as_subprocess')

        end_time = perf_counter()
        self.logger.info('perf_counter() can be used to further measure incremental task duration: %d ms' %
                         (end_time - start_time))

        # must return array of detected scenes at the end
        return scenes

        # If desired, a helper method has been included to cut the scenes and run OCR:
        # return self.extract_scene_information(video_path, timestamps, frame_cuts, everyN, start_time)







