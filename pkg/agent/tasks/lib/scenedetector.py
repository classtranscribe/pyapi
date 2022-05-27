import logging
import multiprocessing
import os
import math
import json
import sys

import importlib


# Default to SimStructuralV1 implementation
SCENE_DETECT_ALGORITHM_CLASS = os.getenv('SCENE_DETECT_ALGORITHM_CLASS', 'ExampleV1')
SCENE_DETECT_ALGORITHM_MODULE = os.getenv('SCENE_DETECT_ALGORITHM_MODULE', 'pkg.agent.tasks.lib.scenedetection.example')


# Three sections:
#   1. (Multi?) Subprocess: Analyze scenes - create metrics for every sampled image from the video
#   2. Main process: Produce scene cut points - find scene start/end points
#   3. Subprocess: Extract scene image / high-res OCR
#
# Steps 1 and 2 are handled by an algorithm-specific subclass. This allows us to easily swap back and forth between
#
def find_scenes(video_path):
    """
    Detects scenes within a video.

    Calculates the similarity between each subsequent frame to identify where scene changes are. Report key features
        about each scene change.

    Parameters:
    video_path (string): Path of the video to be used.

    Returns:
    string: List of dictionaries dumped to a JSON string. Each dict corresponds to a scene/subscene,
        with the key/item pairs being:
        frame_start (int): Numbering of the frame where the scene starts
        frame_end (int): Numbering of the frame where the scene ends
        is_subscene (boolean): Indicating if it's a scene or subscene
        start (string): Starting timestamp of the scene
        end (string): Ending timestamp of the scene
        img_file (string): File name of the detected scene image
        raw_text (dict): Raw pytesseract result as a dict
        phrases (list of strings): Cleaned pytesseract result as a list of strings
        title (string): Detected title of the current scene
    """

    try:
        SceneDetectionAlgorithm_ = getattr(importlib.import_module(SCENE_DETECT_ALGORITHM_MODULE),
                                                     SCENE_DETECT_ALGORITHM_CLASS)

        scene_detection_algorithm = SceneDetectionAlgorithm_()
        return scene_detection_algorithm.find_scenes(video_path)
    except Exception as e:
        print(f"find_scenes({video_path}) throwing Exception:" + str(e))
        print('Failed to lookup SceneDetection Algorithm: %s.%s' % (
            SCENE_DETECT_ALGORITHM_MODULE, SCENE_DETECT_ALGORITHM_CLASS))
        raise e