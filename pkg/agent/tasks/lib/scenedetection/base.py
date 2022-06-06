import logging

import pytesseract
import cv2
import decord
import os

from abc import ABC, abstractmethod
from datetime import datetime
from multiprocessing import Queue, Process
from time import perf_counter

import pkg.agent.tasks.lib.titledetector as td


# CONSTANTS
OCR_CONFIDENCE = 80  # OCR confidnece used to extract text in detected scenes. Higher confidence to extract insightful information


class SceneDetectionAlgorithm(ABC):

    def __init__(self):
        self.logger = logging.getLogger('SceneDetectionAlgorithm')

    @abstractmethod
    def find_scenes(self, video_path):
        """
        The main method of the SceneDetectionAlgorithm. Override this in your subclass.

        Parameters:
        video_path (string): Video path

        Returns:
        string: Features of detected scenes
        """
        pass

    def parse_dir_and_filename(self, video_path):
        """
        Given a video path, return directory and filename (minus extension) as separate values.

        Parameters:
        video_path (string): Video path

        Returns:
        directory (string): directory for the given path
        short_file_name (string): the base filename for the given path (minus extension)
        """
        short_file_name = os.path.basename(video_path)[:video_path.find('.')]
        directory = os.path.dirname(video_path)
        return directory, short_file_name

    def run_as_subprocess(self, target, args):
        """
        Run a method as a subprocess using a result queue to return items, wait for completion, and return the result.

        Parameters:
        target (Function): Function to call as a subprocess
        args (list of object): Arguments to pass to the subprocess function

        Returns:
        anything: the return type of the target Function
        """
        result_queue = Queue()
        p = Process(target=target, args=(result_queue, args,))

        # run as subprocess and block until it completes
        p.start()
        results = result_queue.get()
        p.join()

        return results

    def extract_scene_information(self, video_path, timestamps, frame_cuts, everyN, start_time):
        """
        Wrapper to extract useful features from each detected scenes and output scene images as a subprocess.

        Parameters:
        video_path (string): Video path
        timestamps (list of float): Timestamp array for sample frames
        frame_cuts (list of float): Frame number array for sample frames
        everyN (list of float): Number of frames that is ignored
        start_time (list of float): Start time of the whole process

        Returns:
        string: Features of detected scenes
        """
        args = (video_path, timestamps, frame_cuts, everyN, start_time)
        return self.run_as_subprocess(target=self._extract_scene_information, args=args)

    def _extract_scene_information(self, result_queue, args):
        """
        Internal helper method to extract useful features from each detected scenes and output scene images.

        Parameters:
        video_path (string): Video path
        timestamps (list of float): Timestamp array for sample frames

        Returns:
        string: Features of detected scenes
        """
        (video_path, timestamps, frame_cuts, everyN, start_time) = args

        # grab filename and directory from video_path
        # note: we don't want the '.mp4' extension (if it exists)
        short_file_name = os.path.basename(video_path)[:video_path.find('.')]
        data_directory = os.path.dirname(video_path)

        # build up output path based on video's current location
        out_directory = os.path.join(data_directory, 'frames', short_file_name)

        # Initialize list of scenes
        scenes = []

        # Iterate through the scene cuts
        for i in range(1, len(frame_cuts)):
            scenes += [{'frame_start': frame_cuts[i - 1],
                        'frame_end': frame_cuts[i]}]

        cut_detect_time = perf_counter()
        print(
            f"find_scenes('{video_path}',...) Scene Cut Phase Complete.  Time so far {int(cut_detect_time - start_time)} seconds. Starting Image extraction and OCR")

        # Write the image file for each scene and convert start/end to timestamp

        os.makedirs(out_directory, exist_ok=True)
        last_log_time = 0

        # Video Reader
        vr_full = decord.VideoReader(video_path, ctx=decord.cpu(0))

        for i, scene in enumerate(scenes):
            requested_frame_number = (scene['frame_start'] + scene['frame_end']) // 2

            t = perf_counter()
            if t >= last_log_time + 30:
                print(
                    f"find_scenes({video_path}): {i}/{len(scenes)}. Elapsed {int(t - cut_detect_time)} s")
                last_log_time = t

            # Read a frame through decord
            frame_vr = vr_full[requested_frame_number]
            frame = cv2.cvtColor(frame_vr.asnumpy(), cv2.COLOR_RGB2BGR)

            img_file = os.path.join(
                out_directory, f"{short_file_name}_frame-{requested_frame_number}.jpg")
            cv2.imwrite(img_file, frame)

            # OCR generation
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            str_text = pytesseract.image_to_data(gray_frame, output_type='dict')

            phrases = []
            last_block = -1
            phrase = []
            for i in range(len(str_text['conf'])):
                if int(float(str_text['conf'][i])) >= OCR_CONFIDENCE and len(str_text['text'][i].strip()) > 0:
                    curr_block = str_text['block_num'][i]
                    if curr_block != last_block:
                        if len(phrase) > 0:
                            phrases.append(' '.join(phrase))
                        last_block = curr_block
                        phrase = []
                    phrase.append(str_text['text'][i])
            if len(phrase) > 0:
                phrases.append(' '.join(phrase))

                # Title generation
            frame_height, frame_width, frame_channels = frame.shape
            title = td.title_detection(str_text, frame_height, frame_width)

            # we dont want microsecond accuracy; the [:12] cuts off the last 3 unwanted digits
            scene['start'] = datetime.utcfromtimestamp(timestamps[scene['frame_start'] // everyN]).strftime(
                "%H:%M:%S.%f")[:12]
            scene['end'] = datetime.utcfromtimestamp(timestamps[scene['frame_end'] // everyN]).strftime("%H:%M:%S.%f")[
                           :12]
            scene['img_file'] = img_file
            # Internal debug format; subject to change uses phrases instead
            scene['raw_text'] = str_text
            scene['phrases'] = phrases  # list of strings
            scene['title'] = title  # detected title as string

            # One or more these prevents a memory leak. in the previous stage we observed 16GB over 10,000 samples
            # Leading to OOM
            # Replaced with 'with' statement instead for testing

            del frame_vr
            del frame

            del gray_frame
            del str_text

        del vr_full

        result_queue.put(scenes)

        return scenes

