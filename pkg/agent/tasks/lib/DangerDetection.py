import numpy as np
import math
import RegionShape

def calculate_average_luminance(segment):
    # Luminance is in the Lightness channel (index 1) of HLS
    return np.mean(segment[:, :, 1])

# Function to process the dangerous array
def process_dangerous(dangerous, frame_rate):
    num_frames = dangerous.shape[0]
    height, width = dangerous.shape[1], dangerous.shape[2]
    # Get the size of a grid tile (currently magic numbers for params)
    # number of pixels in each dimension on the screen
    screen_resolution = (height,width)
    # length of screen diagonal (cm)
    screen_size = 15*2.54
    # screen view distance (cm)
    view_distance = 26*2.54
    # viewport angle (default 10)
    viewport_angle = 10
    square_length = RegionShape.calc_viewport(screen_resolution=screen_resolution, screen_size=screen_size, view_distance=view_distance, viewport_angle=viewport_angle)[2]
    sections = max(height // square_length, width // square_length) # multiply by zoom
    segment_height = height // sections
    segment_width = width // sections
    luminance_threshold = 0.5 * 255
    num_flashes = np.zeros((sections, sections))

    # Initialize luminance tracking and timestamps for each segment
    luminances = np.zeros((num_frames, sections, sections))

    # Precalculate all luminance values ahead of time
    for frame_idx in range(num_frames):
        for row in range(sections):
            for col in range(sections):
                y1, y2 = row * segment_height, (row + 1) * segment_height
                x1, x2 = col * segment_width, (col + 1) * segment_width
                segment = dangerous[frame_idx, y1:y2, x1:x2]
                average_luminance = calculate_average_luminance(segment)
                luminances[frame_idx, row, col] = average_luminance

    # Detect luminance changes
    for frame_idx in range(num_frames):
        for future_frame in range(frame_idx + 1, num_frames):
            for row in range(sections):
                for col in range(sections):
                    if (abs(luminances[frame_idx, row, col] - luminances[future_frame, row, col]) > luminance_threshold) and ((luminances[frame_idx, row, col] < 0.8 * 255) or (luminances[future_frame, row, col] < 0.8 * 255)):
                        num_flashes[row, col] += 1
                        # skip to next relevant frame
                        if future_frame < num_frames - 1:
                            frame_idx = future_frame
                            future_frame = frame_idx + 1
                            row = 0
                            col = 0
                        else:
                            return np.max(num_flashes)
    return np.max(num_flashes)