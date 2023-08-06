"""open cv function for camera on"""

import cv2
import os
from sanic.log import logger

import time

filename = 'video.avi'
frames_per_second = 10
res = '720p'


def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)


# Standard Video Dimensions Sizes
STD_DIMENSIONS = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}


# grab resolution dimensions and set video capture to it.
def get_dims(cap, res='1080p'):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width, height = STD_DIMENSIONS[res]
    ## change the current caputre device
    ## to the resulting resolution
    change_res(cap, width, height)
    return width, height


# Video Encoding, might require additional installs
# Types of Codes: http://www.fourcc.org/codecs.php
VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    # 'mp4': cv2.VideoWriter_fourcc(*'H264'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}

palm_cascade = cv2.CascadeClassifier('palm.xml')


# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#
#
#
def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
        return VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']


#
GREEN = (0, 255, 0)
fonts = cv2.FONT_HERSHEY_COMPLEX


def camera_on_cv():
    """function for open camera in system and can end by pressing ' q ' key"""
    cap = cv2.VideoCapture(0)
    if not (cap.isOpened()):
        logger.error("camera is not opened")

    logger.info("camera is working well")
    out = cv2.VideoWriter(filename, get_video_type(filename), frames_per_second, get_dims(cap, res))
    prev = time.time()

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        palm = palm_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        for (x, y, w, h) in palm:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            out.write(frame)

        cv2.putText(
            frame, f"Please show Your Palm", (30, 35),
            fonts, 0.6, GREEN, 2)

        cv2.imshow('frame', frame)
        cur = time.time()
        if cur - prev >= 30:
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            logger.info("camera is closed")
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            break


def stop_camera():
    """function for stop camera"""
    cap = cv2.VideoCapture(0)
    out = cv2.VideoWriter(filename, get_video_type(filename), frames_per_second, get_dims(cap, res))
    logger.info("camera is closed")
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    del cap
