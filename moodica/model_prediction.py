import numpy as np
from PIL import Image
from keras.models import load_model
import image_formatting
import spotify_recommendation_system


SAVED_MODEL_DIR = "trained_model.h5"
MODEL_LABELS = {0: "angry", 1: "fearful", 2: "happy", 3: "neutral", 4: "sad", 5: "surprised"}
IMG_SIZE = 48


def prepare_image_for_prediction(img_path):
    """
    This function modifies the image so the model can use it.
    :param img_path: The image's path to process
    :return: A reshaped 48x48 matrix that contains the image's data.
    :rtype: numpy array.
    """
    img = Image.open(img_path)
    mtx = np.array(img)  # Converting the image to a 48x48 numpy array (matrix).
    mtx = mtx.reshape(-1, IMG_SIZE, IMG_SIZE, 1)  # Reshaping the matrix so the model can read it.
    return mtx


def decode_prediction(prediction_result):
    decoded_prediction = np.argmax(prediction_result, axis=1)  # Deserializing prediction result.
    mood_predicted = MODEL_LABELS[int(decoded_prediction)]
    return mood_predicted


def predict(img_path):
    """
    This function sends the given image path to the trained model
    so it returns the predicted user's mood.
    From there it processes the prediction and sends it
    to the Spotify recommendation system, which returns the playlist
    that is being sent to the client.
    :param img_path: The image path to predict from.
    :return: A Spotify playlist that matches the predicted mood.
    :rtype: str
    """
    model = load_model(SAVED_MODEL_DIR)  # Loading the trained model.

    try:
        image_formatting.img_format_modify_grayscale(img_path, IMG_SIZE, IMG_SIZE)  # Altering the image to match the dataset's format (48x48, grayscale).

    except:
        print("Error: Could not process image")

    try:
        mtx_to_predict = prepare_image_for_prediction(img_path[:img_path.find('.')] + "_modified" + img_path[img_path.find('.'):])  # Sending the modified image's path.

    except FileNotFoundError:  # If there is no file in this path (no face detected in image).
        exit()

    else:
        prediction_result = model.predict(mtx_to_predict)  # Predicting the mood displayed in the picture.
        decoded_prediction = decode_prediction(prediction_result)

        try:
            client_answer = spotify_recommendation_system.activator(decoded_prediction)

        except:
            print("Error: Could not launch Spotify")

        else:
            return client_answer
