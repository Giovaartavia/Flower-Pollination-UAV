
from pyparrot.Bebop import Bebop

isAlive = False


# make my bebop object
bebop = Bebop()

# connect to the bebop
success = bebop.connect(5)

if (success):
      
    bebop.safe_land(10)
    bebop.disconnect()
else:
    print("Error connecting to bebop.  Retry")

# End main
###------------------###