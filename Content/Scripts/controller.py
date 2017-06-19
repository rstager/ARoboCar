import h5py
import pickle
import numpy as np
import sys

# This controller just follows the PID recommendations

print("Connecting to server")
fstate=open("../../roboserver.state","rb")
fcmd=open("../../roboserver.cmd","wb")
print("Connection opened")
config = pickle.load(fstate)
pickle.dump(config,fcmd)
fcmd.flush()

while True:
    state=pickle.load(fstate)
    print("pathdistance {:7f} offset {:5f} distance {:7f} angle {:5.3f} dt={:5.4f}".format(state["pathdistance"], state["offset"], state["PIDthrottle"], state["PIDsteering"],state["delta_time"]))
    pickle.dump({"steering":state["PIDsteering"],'throttle':state["PIDthrottle"]},fcmd)
    fcmd.flush()
