import math

def parse_timestamp(timestamp):
    return int(timestamp[0:2]) * 3600 * 1. + int(timestamp[3:5]) * 60 * 1. + int(timestamp[6:8]) * 1. + int(timestamp[9:12]) / 1000.0

def parse_second(second):
    digit_3 = str("%.3f"%(math.floor(second * 1000) / 1000))
    dot_index = digit_3.index('.')
    return str("%02.f"%math.floor(second / 3600)) + ':' + str("%02.f"%math.floor(second / 60)) + ':' + str("%02.f"%math.floor(second % 60))  + ':' + digit_3[dot_index+1:]

def extract_glossary_timestamps(scenes, phrases):
    phrase_timestamps = dict()
    glossary_in_scenes = []
    found_phrases = set()

    for scene in scenes:
        glossary_in_scene = []
        for phrase in phrases:
            if phrase in found_phrases:
                continue
            
            existed = False
            for scene_ocr in scene['phrases']:
                if phrase in scene_ocr:
                    existed = True
                    break
            
            if existed:
                found_phrases.add(phrase)
                glossary_in_scene.append(phrase)
        
        glossary_in_scenes.append(glossary_in_scene)
    
    start_time = scenes[0]['start']
    end_time = scenes[0]['end']
    for i in range(len(glossary_in_scenes)):
        end_time = scenes[i]['end']
        if len(glossary_in_scenes[i]) <= 0:
            continue
            
        glossary_in_scene = glossary_in_scenes[i]
        for phrase in glossary_in_scene:
            phrase_timestamps[phrase] = (start_time, end_time)
        start_time = scenes[i]['end']
    
    return phrase_timestamps
    
    
