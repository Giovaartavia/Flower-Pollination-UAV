from pyparrot.Bebop import Bebop
from pyparrot.DroneVision import DroneVision
import threading
import cv2
import time

from darkflow.net.build import TFNet

options = {"model": "cfg/sunflower.cfg", "load": -1, "threshold": 0.15, "gpu": 1.0}
tfnet = TFNet(options)
# isSunflower = False

isAlive = False
globalPause = False

###------------------###
#Start movement functions
def moveLightDirection(direction):
    if (direction == "right"):
        roll = 20
        yaw = 2
    else:
        roll = -20
        yaw = -2
    bebop.fly_direct(roll=roll, pitch=0, yaw=0, vertical_movement=0, duration=(0.5)) 

def moveDirection(direction, time, repetitions):
    counter = 0
    if (direction == "right"):
        roll = 20
    else:
        roll = -20

    while (counter < repetitions):
        bebop.fly_direct(roll=roll, pitch=0, yaw=0, vertical_movement=0, duration=(time/4))
        bebop.smart_sleep(3)
        counter = counter + 1 

def goForward():
    bebop.fly_direct(roll=0, pitch=20, yaw=0, vertical_movement=0, duration=2)
    bebop.smart_sleep(2)
###------------------###
#End movement functions

def getHighestConfidence(result):
    topConfidence = 0
    for i in range(0, len(result)):
        if(result[i]["confidence"] > topConfidence):
            topConfidence = result[i]["confidence"]
            topLeftX = result[i]["topleft"]["x"]
            topLeftY = result[i]["topleft"]["y"]
            bottomRightX = result[i]["bottomright"]["x"]
            bottomRightY = result[i]["bottomright"]["y"]
    return((topConfidence, topLeftX, topLeftY, bottomRightX, bottomRightY))

def rescale_frame(frame, percent=50):
    width = int(frame.shape[1] * percent / 100)
    height = int(frame.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

def checkWait():
    while(globalPause == True):
        # Wait
        pass
        # bebop.smart_sleep(60)

        

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
            
            # Use the sunflower with the highest confidence
            (topConfidence, topLeftX, _, _, _) = getHighestConfidence(result)
            print(topLeftX, topConfidence)
            inMiddle = False
            
            global globalPause
            globalPause = True
            # tempCount = 1
            print("Flying down")
            bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=-4, duration=4)
            bebop.smart_sleep(5)

            while (inMiddle == False):
                if(int(topLeftX) < 300):
                    print("Moving Left")
                    moveDirection("left", 3, 1)
                    bebop.smart_sleep(4)
                elif(int(topLeftX) > 350):
                    print("Moving Right")
                    moveDirection("right", 3, 1)
                    bebop.smart_sleep(4)
                else:
                    inMiddle = True
                    print("Sunflower Centered!")
                
                img = self.vision.get_latest_valid_picture()
                cv2.imwrite("image.jpg", img)

                imgcv2 = cv2.imread("image.jpg")
                rescaled = rescale_frame(imgcv2, percent=50)
                result = tfnet.return_predict(rescaled)

                # (topConfidence, topLeftX, _, _, _) = getHighestConfidence(result)
                # Function is not called as it can give code execution order error
                # TODO: Fix this
                topConfidence = 0
                bebop.smart_sleep(2)
                print ("Command:")
                for i in range(0, len(result)):
                    if(result[i]["confidence"] > topConfidence):
                        topConfidence = result[i]["confidence"]
                        topLeftX = result[i]["topleft"]["x"]
                        print(topLeftX, topConfidence)

            done = False
            if (inMiddle == True):
                while(done == False):
                    print("Flying forward")
                    bebop.fly_direct(roll=0, pitch=10, yaw=0, vertical_movement=0, duration=3)
                    bebop.smart_sleep(5)
                    bebop.fly_direct(roll=0, pitch=10, yaw=0, vertical_movement=0, duration=3)
                    bebop.smart_sleep(5)
                
                    # print("Flying back")
                    # bebop.fly_direct(roll=0, pitch=-10, yaw=0, vertical_movement=0, duration=2)
                    # bebop.smart_sleep(

                    print("Flying up")
                    bebop.fly_direct(roll=0, pitch=-0, yaw=0, vertical_movement=4, duration=4)
                    bebop.smart_sleep(5)

                    done = True
                globalPause = False
                

            
            # while(inMiddle == False or tempCount > 5):
            #     tempCount = tempCount + 1

            #     img = self.vision.get_latest_valid_picture()
            #     cv2.imwrite("image.jpg", img)

            #     imgcv2 = cv2.imread("image.jpg")
            #     rescaled = rescale_frame(imgcv2, percent=50)
            #     result = tfnet.return_predict(rescaled)
            #     (_, topLeftX, _, _, _) = getHighestConfidence(result)
            #     print (topLeftX)
                
            #     if(int(topLeftX) < 200):
            #         print("Moving Right")
            #         moveDirection("right", 1/tempCount, 1)
            #         bebop.smart_sleep(4)
            #     elif(int(topLeftX) > 300):
            #         print("Moving Left")
            #         moveDirection("left", 1/tempCount, 1)
            #         bebop.smart_sleep(4)
            #     else:
            #         inMiddle = True
            #         globalPause = False

            # print(topConfidence, topLeftX, topLeftY, bottomRightX, bottomRightY)
            # bebop.pan_tilt_camera_velocity(pan_velocity=0, tilt_velocity=6, duration=4)
            # bebop.safe_land(10)
            # bebopVision.close_video()
            # isSunflower = True



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

        print("Moving the camera using velocity")
        # bebop.pan_tilt_camera_velocity(pan_velocity=0, tilt_velocity=-6, duration=4)
        
        total = 2 #Number of times grid searching is done
        globalCounter = 0 #Temporary counter
        amount = 8 #Number of seconds we fly total per direction
        repetitions = 4

        while (globalCounter < total):
            checkWait()
            moveDirection("right", amount, repetitions)

            checkWait()
            goForward()

            checkWait()
            moveDirection("left", amount, repetitions)

            checkWait()
            goForward()

            globalCounter = globalCounter + 1

        # while(globalCounter < total):
        #     checkWait()
        #     bebop.smart_sleep(3)

        
        bebop.smart_sleep(180)
        
        bebop.safe_land(10)
        print("Stopping vision")
        bebopVision.close_video()
        # bebop.pan_tilt_camera_velocity(pan_velocity=0, tilt_velocity=6, duration=4)

    # disconnect nicely so we don't need a reboot
    bebop.disconnect()
else:
    print("Error connecting to bebop.  Retry")

# End main
###------------------###