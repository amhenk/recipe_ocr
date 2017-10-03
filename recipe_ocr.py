try:
    import Image
except ImportError:
    from PIL import Image

import os
import unicodedata
import pytesseract
import numpy as np
import argparse as ap
import cv2


def is_unicode(s):
    if isinstance(s, unicode):
        return unicodedata.normalize('NFKD', s).encode('UTF-8')
    return s


def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate


# Probably not a good idea to do all of these writes for an SSD.
# However, Tesseract seems to do better with actual images rather than 
# images from arrays
def process_frame(frame_data, image_name):
    cv2.blur(frame_data, (5, 5))
    cv2.imwrite(image_name, frame_data)

    text = is_unicode(pytesseract.image_to_string(Image.open(image_name)))
    if text:
        # TODO: might be good to do some preprocessing if some text is found.
        # Then we can rerun it through tesseract and see if that helps
        return text
    return None


# Check string similarity
def is_similar(a, b, threshold):
    trim_a = a.strip()
    trim_b = b.strip()
    if trim_a == trim_b or trim_a in trim_b:
        return True
    elif len(trim_a) != len(trim_b):
        return False
    pass


def main():

    cap = cv2.VideoCapture(video)
    frame_id = 1

    video_name = video
    if '/' in video:
        video_name = video.split('/')[-1]
    recipe_name = video_name[:video_name.rfind('.')]
    file_name = '{}{}_output.csv'.format(RECIPE_DIRECTORY, recipe_name)
    original_text = ''

    recipe = open(file_name, 'w')

    print 'TODAY ON HORRIBLE RECIPES, WE\'RE COOKING UP A DELICIOUS', recipe_name
    print 'THIS IS DEFINITELY SOMETHING YOU\'RE GONNA WANT TO TRY'
    print '--'*14
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame is None:
            print '----- End Video -----'
            break

        frame_image_name = '{}{}_Frame_{}.jpeg'.format(FRAME_DIRECTORY,
                                                       recipe_name, frame_id)

        # Feel like this function is getting a little TOO incharge
        text = process_frame(frame, frame_image_name)
        if text != None and not is_similar(text, original_text, .8):
            print text
            original_text = text
        else:
            # remove non-text images so we don't fill up the HDD
            os.remove(frame_image_name)

        frame_id += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close recipe file
    recipe.close()


if __name__ == '__main__':
    cwd = os.getcwd()
    FRAME_DIRECTORY = '{}/captured_frames/'.format(cwd)
    RECIPE_DIRECTORY = '{}/recipes/'.format(cwd)

    # Make sure the direcotry exists
    if not os.path.exists(FRAME_DIRECTORY):
        os.makedirs(FRAME_DIRECTORY)
    # Make sure the direcotry exists
    if not os.path.exists(RECIPE_DIRECTORY):
        os.makedirs(RECIPE_DIRECTORY)

    parser = ap.ArgumentParser()
    parser.add_argument('-v', '--video',
                        help='Video to run tesseract over',
                        required=True)

    args = vars(parser.parse_args())
    video = args['video']

    main()
