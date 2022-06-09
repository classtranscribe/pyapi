from pkg.agent.tasks.lib.scenedetection.base import SceneDetectionAlgorithm

import logging


import math
import json
import os

import numpy as np
import pytesseract
import cv2
import decord
from time import perf_counter
from skimage.metrics import structural_similarity as ssim
from collections import Counter

from mtcnn_cv2 import MTCNN

logger = logging.getLogger('pkg.agent.tasks.lib.scenedetection.sim_structural.v1')

TARGET_FPS = float(os.getenv('SCENE_DETECT_FPS', 0.5))
SCENE_DETECT_USE_FACE = os.getenv('SCENE_DETECT_USE_FACE', 'true') == 'true'
SCENE_DETECT_USE_OCR = os.getenv('SCENE_DETECT_USE_OCR', 'true') == 'true'
SCENE_DETECT_USE_EARLY_DROP = os.getenv('SCENE_DETECT_USE_EARLY_DROP', 'true') == 'true'

# Threshold for max number of samples for scene candidate selection
# sample_rate is determined by FPS, samples = frames / sample_rate
# if samples exceeds our threshold, we artificially lower the sampling rate
MAX_SAMPLES = os.getenv('SCENE_DETECT_MAX_SAMPLES', 3000)  # default ~ 100 minutes at 0.5 fps
MIN_SCENE_LENGTH = 1  # Minimum scene length in seconds
ABS_MIN = 0.7  # Minimum combined_similarities value for non-scene changes, i.e. any frame with combined_similarities < ABS_MIN is defined as a scene change

detector = MTCNN()


def require_ssim_with_face_detection(curr_frame, curr_result, last_frame, last_result):
    """
    Given two frames with their face & upper body bounding boxes,
        find SSIM between them after removing face & upper body

    Parameters:
    curr_frame (image): Image of the first frame
    curr_result (tuple): Face & upper body detection result of the first frame
    last_frame (image): Image of the second frame
    last_result (tuple): Face & upper body detection result of the second frame

    Returns:
    float: SSIM after removing face & upper body
    """

    curr_frame_with_face_removed = curr_frame.copy()
    last_frame_with_face_removed = last_frame.copy()

    if curr_result[0]:
        curr_boxes = curr_result[1]
        for j in range(len(curr_boxes)):
            x1, x2, y1, y2 = curr_boxes[j]
            curr_frame_with_face_removed[x1:x2, y1:y2] = 0
            last_frame_with_face_removed[x1:x2, y1:y2] = 0

    if last_result[0]:
        last_boxes = last_result[1]
        for j in range(len(last_boxes)):
            x1, x2, y1, y2 = last_boxes[j]
            curr_frame_with_face_removed[x1:x2, y1:y2] = 0
            last_frame_with_face_removed[x1:x2, y1:y2] = 0

    return ssim(last_frame_with_face_removed, curr_frame_with_face_removed)


def require_face_result(curr_frame):
    """
    Find all the bounding boxes of face & upper body appeared in a given frame.

    Parameters:
    curr_frame (image): Frame image

    Returns:
    tuple:
        First element: a boolean indicating if there is any face & upper body found inside the frame
        Second element: a list of bounding boxes of face & upper body
    """

    # Convert the input image to gray scale
    gray_frame = cv2.cvtColor(cv2.resize(
        curr_frame, (320, 240)), cv2.COLOR_BGR2RGB)

    # Run the face detection
    faces = detector.detect_faces(gray_frame)

    curr_frame_boxes = []  # [x1, x2, y1, y2]
    has_body = False

    # Iterate through all the bounding boxes for one frame
    for face in faces:
        x, y, width, height = face['box']
        curr_frame_boxes.append([x, x + width, y, y + height])

        # Move x to the center of the face bounding box
        x = x + width / 2

        # Check if the face is at the center
        if x > 0.2 * gray_frame.shape[1] and x < 0.8 * gray_frame.shape[1]:

            # Check if the face is large enough
            if width / gray_frame.shape[1] > 0.1 or height / gray_frame.shape[0] > 0.1:
                has_body = True
                body_x = int(x - 2 * width)
                if body_x < 0:
                    body_x = 0

                body_y = y + height
                body_width = width * 4
                body_height = height * 3

                curr_frame_boxes.append(
                    [body_x, body_x + body_width, body_y, body_y + body_height])

    return (has_body, curr_frame_boxes)


def compare_ocr_difference(word_dict_a, word_dict_b):
    """
    Calculate the sim_OCR between two frames.

    Parameters:
    word_dict_a (dict): Key is the words that appeared in the OCR output for frame A
                        Value is the sum of confidence of each word
    word_dict_b (dict): Key is the words that appeared in the OCR output for frame B
                        Value is the sum of confidence of each word

    Returns:
    float: Relative OCR similarty between the two frames
    """

    total_amount = 0
    for k in word_dict_a.keys():
        total_amount += word_dict_a[k]
    for k in word_dict_b.keys():
        total_amount += word_dict_b[k]

    if total_amount == 0:
        return 1.0

    score = 0
    for key_a in word_dict_a.keys():
        if key_a in word_dict_b.keys():
            score += (word_dict_a[key_a] + word_dict_b[key_a])

    for key_b in list(set(word_dict_b.keys()) - set(word_dict_a.keys())):
        if key_b in word_dict_a.keys():
            score += (word_dict_a[key_b] + word_dict_b[key_b])

    return score / total_amount


def calculate_score(sim_structural, sim_ocr, sim_structural_no_face):
    """
    Calculate the final similarities score between two frames.

    Parameters:
    sim_structural (list of float): List of similarities (SSIMs) between frames
    sim_ocr (list of float): List of OCR similarities
    sim_structural_no_face (list of float): List of similarities (SSIMs) between frames when face is removed

    Returns:
    list of float: List of combined_similarities between frames
    """
    # NOTE: This will eventually use results from a support-vector machine
    return 0.3 * sim_structural + 0.3 * sim_structural_no_face + 0.4 * sim_ocr


def generate_frame_similarity(video_path, num_samples, everyN, start_time):
    """
    Generate simlarity values for each sample frames.

    Parameters:
    video_path (string): Video path
    num_samples (list of float): Amount of samples
    everyN (list of float): Number of frames that is ignored each iteration
    start_time (list of float): Start time of the whole process

    Returns:
    List of string: Timestamps array of each sample frame
    List of float: sim_structural array of each sample frame
    List of float: sim_structural_no_face array of each sample frame
    List of float: sim_ocr array of each sample frame
    """

    SIM_OCR_CONFIDENCE = 55  # OCR confidnece used to generate sim_ocr
    DROP_THRESHOLD = 0.95  # Minimum sim_structural confidnece to conclude no scene changes

    # Stores the last frame read
    last_frame = 0

    # Stores the last face detetion result
    last_face_detection_result = 0

    # Stores the OCR output of last frame read
    last_ocr = dict()

    # List of similarities (SSIMs) between frames
    sim_structural = np.zeros(num_samples)

    # List of OCR outputs and OCR similarities
    ocr_output = []
    sim_ocr = np.zeros(num_samples)

    # List of similarities (SSIMs) between frames when face is removed
    sim_structural_no_face = np.zeros(num_samples)

    timestamps = np.zeros(num_samples)

    # Video Reader
    vr_full = decord.VideoReader(video_path, ctx=decord.cpu(0))
    last_log_time = 0
    # For this loop only we are not using real frame numbers; we are skipping frames to improve processing speed

    # Avoid memory leak by using del
    curr_face_detection_result = None
    last_face_detection_result = None
    frame_vr = None
    frame = None
    last_frame = None
    ocr_frame = None
    str_text = None

    for i in range(0, num_samples):

        t = perf_counter()
        if t >= last_log_time + 30:
            logger.info(
                f"find_scenes({video_path}): {i}/{num_samples}. Elapsed {int(t - start_time)} s")
            last_log_time = t

        # Read the next frame, resizing and converting to grayscale
        frame_vr = vr_full[i * everyN]
        frame = cv2.cvtColor(frame_vr.asnumpy(), cv2.COLOR_RGB2BGR)

        # Save the time stamp of each frame
        timestamps[i] = vr_full.get_frame_timestamp(i * everyN)[0]

        curr_frame = cv2.cvtColor(cv2.resize(
            frame, (320, 240)), cv2.COLOR_BGR2GRAY)

        # Calculate the SSIM between the current frame and last frame
        if i >= 1:
            sim_structural[i] = ssim(last_frame, curr_frame)

        # Check the sim_structural score to ignore Face Detection and OCR
        is_early_drop = (i >= 1 and sim_structural[i] >= DROP_THRESHOLD and SCENE_DETECT_USE_EARLY_DROP)

        # Drop Face Detection and OCR
        if is_early_drop:
            sim_structural[i] = 1  # By setting all of these to 1 we declare that there is no change in frame here.
            sim_structural_no_face[i] = 1
            sim_ocr[i] = 1

        # Continue Face Detection and OCR
        else:
            if SCENE_DETECT_USE_FACE:
                # Run Face Detection upon the current frame
                curr_face_detection_result = require_face_result(curr_frame)

                # Calculate the SSIM between the current frame and last frame when face & upper body are removed
                if i >= 1:
                    sim_structural_no_face[i] = require_ssim_with_face_detection(
                        curr_frame, curr_face_detection_result, last_frame, last_face_detection_result)

                # Save the current face detection result for the next iteration
                del last_face_detection_result
                last_face_detection_result = curr_face_detection_result
            else:
                sim_structural_no_face[i] = sim_structural[i]

            if SCENE_DETECT_USE_OCR:
                # Calculate the OCR difference between the current frame and last frame
                ocr_frame = cv2.cvtColor(cv2.resize(
                    frame, (480, 360)), cv2.COLOR_BGR2GRAY)
                str_text = pytesseract.image_to_data(
                    ocr_frame, output_type='dict')

                phrases = Counter()
                for j in range(len(str_text['conf'])):
                    if int(str_text['conf'][j]) >= SIM_OCR_CONFIDENCE and len(str_text['text'][j].strip()) > 0:
                        phrases[str_text['text'][j]
                        ] += (float(str_text['conf'][j]) / 100)

                del str_text
                curr_ocr = dict(phrases)

                if i >= 1:
                    sim_ocr[i] = compare_ocr_difference(last_ocr, curr_ocr)

                ocr_output.append(phrases)

                # Save the current OCR output for the next iteration
                if last_ocr:
                    del last_ocr
                last_ocr = curr_ocr
            else:
                sim_ocr[i] = 1 if i >= 1 else 0

        # Save the current frame for the next iteration
        if last_frame is not None:
            del last_frame
        last_frame = curr_frame

        # One or more these prevents a memory leak. (16GB over 10,000 samples)
    if SCENE_DETECT_USE_OCR:
        del curr_face_detection_result
        del last_ocr

    del last_frame  # May prevent a memory leak
    del frame_vr
    del frame
    del curr_frame

    return timestamps, sim_structural, sim_structural_no_face, sim_ocr


def _enumerate_scene_candidates(result_queue, args):
    """
    Given a video path, parse the video file and look for possible location where scenes could be cut.

    Parameters:
    video_path (string): Video path
    start_time (datetime): the time at which the task started (for reporting incremental performance or progress)

    Returns:
    string: Features of detected scenes
    """
    (video_path, start_time) = args

    # Extract frames s1,e1,s2,e2,....
    # e1 != s2 but s1 is roughly equal to m1
    # s1 (m1) e1 s2 (m2) e2

    logger.info(f"find_scenes({video_path}) starting...")
    logger.info(
        f"SCENE_DETECT_USE_FACE={SCENE_DETECT_USE_FACE}, SCENE_DETECT_USE_OCR={SCENE_DETECT_USE_OCR}, TARGET_FPS={TARGET_FPS}")

    # Check if the video file exists
    if os.path.exists(video_path):
        logger.info(f"{video_path}: Found file!")
    else:
        logger.warning(f"{video_path}: File not found -returning empty scene cuts ")
        return json.dumps([])

    # Get the video capture and number of frames and fps
    cap = cv2.VideoCapture(video_path)
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fps = float(cap.get(cv2.CAP_PROP_FPS))

    # Input FPS could be < targetFPS
    everyN = max(1, int(fps / TARGET_FPS))

    num_samples = num_frames // everyN

    logger.info(
        f"find_scenes({video_path}): frames={num_frames}. fps={fps}. everyN={everyN}. samples={num_samples}.")

    # examine num_samples < 3000 (tbd)? if so, lower sampling rate (TARGET_FPS?)
    # probably ~3000 will be maximum in practice
    if num_samples > MAX_SAMPLES:
        logger.warning(
            f" >>> WARNING: Sampling every {everyN} frame with {num_frames} frames would "
            f"exceed maximum number of samples {MAX_SAMPLES}.")
        everyN = int(math.ceil(num_frames / MAX_SAMPLES))
        num_samples = num_frames // everyN
        logger.warning(f" >>> WARNING: Using alternative sampling rate. everyN={everyN}. samples={num_samples}.")

    # Mininum number of frames per scene
    min_samples_between_cut = max(0, int(MIN_SCENE_LENGTH * TARGET_FPS))

    # Scene Analysis
    timestamps, sim_structural, sim_structural_no_face, sim_ocr = generate_frame_similarity(video_path, num_samples,
                                                                                            everyN, start_time)

    t = perf_counter()
    logger.info(
        f"find_scenes('{video_path}',...) Scene Analysis Complete.  Time so far {int(t - start_time)} seconds. Defining Scene Cut points next")

    result = (min_samples_between_cut, num_samples, num_frames, everyN, timestamps, sim_structural, sim_structural_no_face, sim_ocr)
    result_queue.put(result)

    return result


class SimStructuralV1(SceneDetectionAlgorithm):

    def enumerate_scene_candidates(self, video_path, start_time):
        return self.run_as_subprocess(target=_enumerate_scene_candidates, args=(video_path, start_time))

    def find_scenes(self, video_path):
        """
        The main method of the SceneDetectionAlgorithm. Override this in your subclass.

        Parameters:
        video_path (string): Video path

        Returns:
        string: Features of detected scenes
        """
        start_time = perf_counter()

        # 1. Enumerate candidates as subprocess and block until it completes
        logger.info(' >>>>> SceneDetection Running Step 1/3 (subprocess): ' + video_path)
        (min_samples_between_cut, num_samples, num_frames, everyN, timestamps,
            sim_structural, sim_structural_no_face, sim_ocr) = self.enumerate_scene_candidates(video_path, start_time)

        # 2. Calculate the combined similarities score
        logger.info(' >>>>> SceneDetection Running Step 2/3 (main process): ' + video_path)
        combined_similarities = calculate_score(
            sim_structural, sim_ocr, sim_structural_no_face)

        # actual pixels/color differences, text/object differences, face/mouth differences

        # Find cuts by finding where combined similarities < ABS_MIN
        samples_cut_candidates = np.argwhere(
            combined_similarities < ABS_MIN).flatten()

        logger.info(f"{video_path}: {len(samples_cut_candidates)} candidates identified")
        if len(samples_cut_candidates) == 0:
            logger.warning(f"{video_path}:Returning early - no scene cuts found")
            return json.dumps([])

        # Get real scene cuts by filtering out those that happen within min_frames of the last cut
        sample_cuts = [samples_cut_candidates[0]]
        for i in range(1, len(samples_cut_candidates)):
            if samples_cut_candidates[i] >= samples_cut_candidates[i - 1] + min_samples_between_cut:
                sample_cuts += [samples_cut_candidates[i]]

        if num_samples > 1:
            sample_cuts += [num_samples - 1]

        # Now work in frames again. Make sure we are using regular ints (not numpy ints) other json serialization will fail
        frame_cuts = [int(s * everyN) for s in sample_cuts]

        # Finish up by calling helper method to cut scenes and run OCR
        logger.info(' >>>>> SceneDetection Running Step 3/3 (subprocess): ' + video_path)
        return self.extract_scene_information(video_path, timestamps, frame_cuts, everyN, start_time)

