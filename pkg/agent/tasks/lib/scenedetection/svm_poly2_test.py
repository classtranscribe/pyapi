import cv2
import json
import numpy as np
import os
import shutil
import sys
import urllib.request
from skimage.metrics import structural_similarity as ssim
from sklearn import svm
import tempfile
#from pkg.agent.tasks.lib.scenedetection.svm_poly2 import SvmPoly2
from svm_poly2 import SvmPoly2

DIR = os.path.dirname(os.path.realpath(__file__)) # Path to the directory of the test file 
MODEL_PATH = os.path.join(DIR, 'models', 'poly2.json') # Path to the SVM model
TEST_SET_PATH = os.path.join(DIR, 'models', 'poly2_test.json') # Path to the testing set for SVM model
TOTAL_TEST_COUNT = 5 # Total number of test cases to run

def map_to_poly_kernel(features):
    '''
    Map the data from feature space to kernel space. A polynomial kernel of degree 2 is selected as the kernel.

    Parameters:
    X_train (numpy.ndarray): Data inside feature space

    Returns:
    numpy.ndarray: Data inside kernel space
    '''
    
    kernel_space = np.ndarray((len(features), 10))
    
    kernel_space[:, 0] = features[:, 0] * features[:, 0] # a * a
    kernel_space[:, 1] = features[:, 1] * features[:, 1] # b * b
    kernel_space[:, 2] = features[:, 2] * features[:, 2] # c * c
    
    kernel_space[:, 3] = features[:, 0] * features[:, 1] * np.sqrt(2) # a * b
    kernel_space[:, 4] = features[:, 0] * features[:, 2] * np.sqrt(2) # a * c
    kernel_space[:, 5] = features[:, 1] * features[:, 2] * np.sqrt(2) # b * c
    
    kernel_space[:, 6] = features[:, 0] * np.sqrt(2) # a
    kernel_space[:, 7] = features[:, 1] * np.sqrt(2) # b
    kernel_space[:, 8] = features[:, 2] * np.sqrt(2) # c
    
    kernel_space[:, 9] = np.ones(len(features)) # Constant    
    
    return kernel_space

def setup_sd():
    '''
    Initialize the SceneDetectionAlgorithm object

    Returns:
    SceneDetectionAlgorithm: the SceneDetectionAlgorithm object used for scene detection
    '''

    try:
        return SvmPoly2()

    except Exception as e:
        print(e)
        print('ERROR: Cannot initialize the SceneDetectionAlgorithm object!')

def setup_svm_testing_set(path):
    '''
    Load the data set to test the prediction accuracy of the model 

    Parameters:
    path (string): File path to the testing set for SVM model

    Returns:
    numpy.ndarray, numpy.ndarray: data in feature space and their expected labels
    '''

    try:
        # Load the SVM Model from JSON file
        with open(path, 'r') as f:
            svm_test_set = json.load(f)
        print(f"{path}: SVM Testing Data Set Loaded!")
        
        # Initialize the SVM Model and pass in the parameters
        x_test = np.array(svm_test_set['x_test'])
        y_expected = np.array(svm_test_set['y_expected'])

        return x_test, y_expected
    
    except Exception as e:
        print(e)
        print('ERROR: Path to SVM testing set is wrong or the file is missing!')

def setup_svm(path):
    '''
    Load the SVM model to be testing

    Parameters:
    path (string): Path to the SVM model

    Returns:
    sklearn.svm.SVC: SVM model with parameters loaded
    '''

    try:
        # Load the SVM Model from JSON file
        with open(path, 'r') as f:
            loaded_model_params = json.load(f)
        print(f"{path}: SVM Loaded!")
        
        # Initialize the SVM Model and pass in the parameters
        loaded_clf = svm.SVC(kernel='linear')

        loaded_clf._dual_coef_ = np.array(loaded_model_params['_dual_coef_'])
        loaded_clf.support_vectors_ = np.array(loaded_model_params['support_vectors_'])
        loaded_clf._sparse = loaded_model_params['_sparse']
        loaded_clf._n_support = np.array(loaded_model_params['_n_support'], dtype = np.int32)
        loaded_clf.support_ = np.array(loaded_model_params['support_'], dtype = np.int32)
        loaded_clf._intercept_ = np.array(loaded_model_params['_intercept_'])
        loaded_clf._probA = np.array(loaded_model_params['_probA'])
        loaded_clf._probB = np.array(loaded_model_params['_probB'])
        loaded_clf._gamma = loaded_model_params['_gamma']
        loaded_clf.classes_ = np.array(loaded_model_params['classes_'], dtype = np.int32)
        loaded_clf.gamma = loaded_model_params['gamma']
        
        return loaded_clf
        
    except Exception as e:
        print(e)
        print('ERROR: Path to SVM model is wrong or the file is missing!')

def test_model_parameters(model):
    '''
    Test if the model parameters are as expected

    Parameters:
    model (sklearn.svm.SVC): the SVM model

    Returns:
    int: 0 when test passed, 1 when test failed
    '''

    print("----------" + "SVM Parameters Test" + "---STARTED----------")
    try:
        assert len(model.support_vectors_[0]) == 10, f"Model has incorrect dimensions, {len(model.support_vectors_[0])} (expected 10)"
        assert model.get_params()['kernel'] == 'linear', f"Model has incorrect kernel, {model.get_params()['kernel']} (expected linear)"

        print("----------" + "SVM Parameters Test" + "---PASSED----------")
        return 0
        
    except Exception as e:
        print(e)
        print('ERROR: One of the model parameters is not as expected!')
        return 1

def test_model_prediction(model, x_test, y_expected):
    '''
    Test if the predicted results of x_test match with expected labels

    Parameters:
    model (sklearn.svm.SVC): the SVM model
    x_test (numpy.ndarray): data set in feature space for prediction
    y_expected (numpy.ndarray): expected label for data entry in x_test

    Returns:
    int: 0 when test passed, 1 when test failed
    '''
    
    print("----------" + "SVM Prediction Test" + "---STARTED----------")
    try:
        y_predicted = model.predict(map_to_poly_kernel(x_test))
        for i in range(len(y_predicted)):
            assert y_predicted[i] == y_expected[i], f"Predicted label dose not match with the expected label, {y_predicted[i]} (expected {y_expected[i]})"

        print("----------" + "SVM Prediction Test" + "---PASSED----------")
        return 0
        
    except Exception as e:
        print(e)
        print('ERROR: At least one of the prediction result of the model is wrong!')
        return 1

def sd_test_scheme(detector, video_name, url, expected_phrases):
    '''
    Run find_scenes() method on the given video, and check the OCR results and frame number for accuracy 

    Parameters:
    detector (SceneDetectionAlgorithm): the SceneDetectionAlgorithm object that will be called with find_scenes()
    video_name (string): name of the video to be passed into find_scenes()
    url (string): url to download the video from Box
    expected_phrases (list): expected phrases and words that are in the extracted OCR results
    '''

    print("----------" + video_name + "---STARTED----------")
    
    try:
        video_path = os.getcwd() + '/' + video_name + '.mp4'
        folder_path = os.getcwd() + '/frames/' + video_name + '.mp4'
        print("Path to the video:" + video_path)

        # Download the video file
        urllib.request.urlretrieve(url, video_path) 

        # Run SceneDetector on the video 
        video_json = detector.find_scenes(video_path)

        scenes = video_json
        
        corpus = []
        for scene in scenes:
            corpus.append(scene['phrases'])
        
        raw_phrases = '\n'.join( ['\n'.join(words) for words in corpus] )
        raw_phrases = raw_phrases.replace('``','')

        # Check phrase occurrence
        for phrase in expected_phrases:
            assert phrase in raw_phrases, f"Phrase {phrase} is expected to be inside the OCR output, but is not"
            print("Phrase " + phrase + " was in the OCR output")
        
        # Check frame number
        frame_list = os.listdir(folder_path)
        for frame_name in frame_list:
            frame_path = folder_path + '/' + frame_name
            output_frame = cv2.imread(frame_path)
            frame_number = frame_name[frame_name.rfind('-')+1 : frame_name.rfind('.')]

            cap = cv2.VideoCapture(video_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_number) )  
            ret, frame = cap.read()
            
            rezied_frame = cv2.cvtColor(cv2.resize(frame, (320,240)), cv2.COLOR_BGR2GRAY)
            resized_output_frame = cv2.cvtColor(cv2.resize(output_frame, (320,240)), cv2.COLOR_BGR2GRAY)
            
            sim = ssim(rezied_frame, resized_output_frame)
            print('Frame ' + frame_number + " Simlarity: " + str(sim))
            assert sim > 0.99, f"Frame {frame_number} extracted dose not match with the original frame inside the video"

        print("----------" + video_name + "---Passed----------")
    
    except Exception as e:
        print(e)
        print('ERROR: Error detected when running find_scenes()!')

def test_scenedetector_results(detector):
    '''
    Run find_scenes() method on three downloaded videos, and check results for accuracy 

    Parameters:
    detector (SceneDetectionAlgorithm): the SceneDetectionAlgorithm object that will be called with find_scenes()

    Returns:
    int: the number of failed cases
    '''

    video_names = ['test_1_toy_lecture', 'test_2_241_thread', 'test_3_adv582_w3']
    urls = [
        'https://app.box.com/index.php?rm=box_download_shared_file&shared_name=pec6m3vbjzu2l4d2m1gv9588npq9nw7o&file_id=f_827175578540',
        'https://app.box.com/index.php?rm=box_download_shared_file&shared_name=xbs7aqcsnrjdglplc6neh3fxdhkqz2fi&file_id=f_827616401395',
        'https://app.box.com/index.php?rm=box_download_shared_file&shared_name=t8lnoxyrmiff0g2xtvg9t5tlak0npnyl&file_id=f_828444986436'
    ]
    expected_phrases_list = [
        ['Slide One', 'float', 'char'],
        ['pthread_create', 'Compile', 'stacks', 'printf', 'nothing happens'],
        ['Merchants of Cool', 'Barak Goodman', 'New York Times']
    ]

    error = 0
    for i in range(len(video_names)):
        try:
            sd_test_scheme(detector, video_names[i], urls[i], expected_phrases_list[i])
        except Exception as e:
            error += 1
            print(e)
            print('ERROR: One video test case for find_scenes() failed!')
    return error

def run_tests(tempdir):
    '''
    Run all the test cases

    Parameters:
    tempdir (String): file path to store temporary downloaded files

    Returns:
    int: the number of failed test cases
    '''

    fail_count = 0
    try:
        print("Setting Up")
        detector = setup_sd()
        model = setup_svm(MODEL_PATH)
        x_test, y_expected = setup_svm_testing_set(TEST_SET_PATH)
        
        print("Running Tests")
        fail_count += test_model_parameters(model)
        fail_count += test_model_prediction(model, x_test, y_expected)
        fail_count += test_scenedetector_results(detector)
    except Exception as e:
        print(e)
    print(f"{TOTAL_TEST_COUNT} Test(s) finished {fail_count} failed")
    return fail_count

if __name__ == '__main__': 
    fail_count = 0
    with tempfile.TemporaryDirectory() as tempdir:
        print( f"Using {tempdir} for downloads")
        os.chdir(tempdir)
        fail_count = run_tests(tempdir)
    if fail_count > 0:
        sys.exit(1) # Exiting with a non-zero value