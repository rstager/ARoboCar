import h5py
import pickle
import numpy as np
import sys
from keras.models import load_model

model=load_model("model_1_v1.h5")
print(model.summary())

print("Connecting to server")
fstate=open("../../roboserver.state","rb")
fcmd=open("../../roboserver.cmd","wb")
print("Connection opened")

config = pickle.load(fstate)
pickle.dump(config,fcmd)
fcmd.flush()


while True:
    state=pickle.load(fstate)
    img=state["frontcamera"]
    img=np.reshape(img,(1,img.shape[0],img.shape[1],img.shape[2]))
    steering=model.predict(img)[0,0]
    print("steering {:5.3f} pathdistance {:7f} offset {:5f} PID {:5.3f} {:5.3f} dt={:5.4f}".format(steering,state["pathdistance"], state["offset"], state["PIDthrottle"], state["PIDsteering"],state["delta_time"]))
    pickle.dump({"steering":steering,'throttle':state["PIDthrottle"]},fcmd)
    fcmd.flush()