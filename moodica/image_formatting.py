from PIL import Image
import cv2


def img_format_modify_grayscale(img_loc, high, length):
    """
    This function takes an image and returns the path to a new
    copy of it in size 48x48, grayscale.
    :param img_loc: image's file path.
    :param high: height of image in pixels.
    :param length: width of image in pixels.
    :return: A path of the new, processed (48x48 grayscaled) image.
    :rtype: str
    """
    img = cv2.imread(img_loc)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in faces:
        faces = img[y:y + h, x:x + w]
        break

    # Converting the opencv image into a PIL image format.
    try:
        color_converted = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(color_converted)

    except:
        print("Error: No face detected")
        return str("No face detected")

    # Making the image grayscale and in the size of 48x48.
    image = image.resize((high, length))
    greyscale_image = image.convert('L')
    greyscale_image.save(img_loc[:img_loc.find('.')] + "_modified" + img_loc[img_loc.find('.'):])
    return str(img_loc[:img_loc.find('.')] + "_modified" + img_loc[img_loc.find('.'):])
