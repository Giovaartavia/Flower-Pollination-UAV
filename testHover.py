#File to test if Bebop's smart sleep is required for recognition
#or if it's performed in real time

"""
Demo of the Bebop ffmpeg based vision code (basically flies around and saves out photos as it flies)

Author: Amy McGovern
"""
from pyparrot.Bebop import Bebop
from pyparrot.DroneVision import DroneVision
import threading
import cv2
import time

from darkflow.net.build import TFNet

options = {"model": "cfg/sunflower.cfg", "load": -1, "threshold": 0.12, "gpu": 1.0}
tfnet = TFNet(options)

found = False
isAlive = False

def rescale_frame(frame, percent=50):
    width = int(frame.shape[1] * percent / 100)
    height = int(frame.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)




class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        img = self.vision.get_latest_valid_picture()
        cv2.imwrite("image.jpg", img)

        imgcv2 = cv2.imread("image.jpg")
        rescaled = rescale_frame(imgcv2, percent=50)
        result = tfnet.return_predict(rescaled)
        print (result)

        # Sunflower detected:
        if (len(result) > 0):   
            print("Found Sunflower")
            bebop.safe_land(10)
            bebopVision.close_video()
            found = True



###------------------###
#Start main:

# make my bebop object
bebop = Bebop()

# connect to the bebop
success = bebop.connect(5)

if (success):
    # start up the video
    bebopVision = DroneVision(bebop, is_bebop=True)

    userVision = UserVision(bebopVision)
    bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
    success = bebopVision.open_video()

    if (success):        
        print("Vision successfully started!")

        print("sleeping")
        bebop.smart_sleep(2)

        bebop.ask_for_state_update()
        bebop.safe_takeoff(10)
        bebop.smart_sleep(2)
        
        bebop.safe_land(10)
        print("Stopping vision")
        bebopVision.close_video()

    # disconnect nicely so we don't need a reboot
    bebop.disconnect()
else:
    print("Error connecting to bebop.  Retry")

# End main
###------------------###