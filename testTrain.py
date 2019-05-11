from darkflow.net.build import TFNet

options = {"model": "cfg/test.cfg", 
           "load": "bin/yolov2.weights",
           "batch": 8,
           "epoch": 100,
           "gpu": 1.0,
           "train": True,
           "annotation": "../annotations/",
           "dataset": "../images/"}
           
tfnet = TFNet(options)

tfnet.train()