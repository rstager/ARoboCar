import h5py
import pickle
import numpy as np
import sys
from keras.models import load_model

model=load_model("model_1_save.h5")
print(model.summary())

fstate=open("../../roboserver.state","rb")
fcmd=open("../../roboserver.cmd","wb")
print("Connection opened")

width,height = pickle.load(fstate)
print(width,height)

while True:
    img= pickle.load(fstate)
    state=pickle.load(fstate)
    img=np.reshape(img,(1,img.shape[0],img.shape[1],img.shape[2]))
    steering=model.predict(img)[0]
    print(" reward {:7f} offset {:5f} distance {:7f} angle {:5.3f} dt={:5.4f}".format(state["reward"], state["offset"], state["PIDthrottle"], state["PIDsteering"],state["delta_time"]))
    pickle.dump({"steering":steering,'throttle':state["PIDthrottle"]},fcmd)
    fcmd.flush()