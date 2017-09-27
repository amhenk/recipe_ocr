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


def main():

    cap = cv2.VideoCapture(video)
    frame_id = 1 

    recipe_name = video[:video.rfind('.')]
    file_name = '{}{}_output.csv'.format(RECIPE_DIRECTORY, recipe_name)

    recipe = open(file_name, 'w')

    print 'TODAY ON HORRIBLE RECIPES, WE\'RE COOKING UP A DELICIOUS', recipe_name
    print 'THIS IS DEFINITELY SOMETHING YOU\'RE GONNA WANT TO TRY'
    print '--'*14
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame is None:
            print '----- End Video -----'
            break

        # Probably not a good idea for SSDs but tesseract seems to do
        # better with actual images rather than arrays
        frame_image_name = '{}{}_Frame_{}.jpeg'.format(FRAME_DIRECTORY, recipe_name, frame_id)
        cv2.imwrite(frame_image_name, frame)
        text = is_unicode(pytesseract.image_to_string(Image.open(frame_image_name)))
        if text:
            line = 'Frame_{}\t{}'.format(frame_id, text.strip())
            print line
            recipe.write(line+'\n')
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
