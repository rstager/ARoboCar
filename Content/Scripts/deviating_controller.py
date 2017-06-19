import h5py
import pickle
import numpy as np
import sys
import random

# This controller just follows the PID recommendations most of the time but deviates to capture off-policy state
# this controller also records state

#runtime configuration parameters
filename="robocar.hdf5" # or None
steering_noise=.15      #amount of noise to add to steering
noise_probability=0.01  #how often to deviate - set to zero to drive correctly
deviation_duration=20   # duration of deviation

# first connect to the simulator
fstate=open("../../roboserver.state","rb")
fcmd=open("../../roboserver.cmd","wb")
print("Connection opened")

# get the configuration data
config = pickle.load(fstate)
print("config=",config)
height=config["cameraheight"]
width=config["camerawidth"]

#sending back config data with possible changes
pickle.dump(config,fcmd)
fcmd.flush()



#now open the h5 file
maxidx=32
output = h5py.File(filename, 'w')
images = output.create_dataset('frontcamera', (maxidx, height, width, 3), 'i1',
                                         maxshape=(None, height, width, 3))
images.attrs['description'] = "simple test"
controls = output.create_dataset('steering.throttle', (maxidx, 2), maxshape=(None, 2))

#parameters for deviating
deviating_cnt=0
h5idx=0
while True:
    # get images and state from simulator
    # record images and steering,throttle
    images[h5idx] = pickle.load(fstate)
    state=pickle.load(fstate)
    controls[h5idx]= [state["PIDsteering"],state["PIDthrottle"]]
    h5idx += 1
    if(h5idx>=maxidx):
        maxidx += 32
        images.resize((maxidx, height, width, 3))
        controls.resize((maxidx, 2))
        output.flush()
        print("Flushing h5")

    #print("pathdistance {:7f} offset {:5f} PID {:7f}  {:5.3f} dt={:5.4f}".format(state["pathdistance"], state["offset"], state["PIDthrottle"], state["PIDsteering"],state["delta_time"]))
    #use the PID values by default
    steering=state["PIDsteering"]
    throttle=state["PIDthrottle"]
    offset=state["offset"] #distance from center of road

    if deviating_cnt > 0 and abs(offset) > 75:  # stop deviating if we ran off the road
        deviating_cnt = 0
        print("Abort deviation")

    if deviating_cnt>0: # while deviation
        steering = deviation_angle
        deviating_cnt -= 1
        if (deviating_cnt == 0):
            print("End deviation")

    #decide when to start another deviation
    if deviating_cnt == 0 and random.random() < noise_probability:
        deviating_cnt = deviation_duration
        deviation_angle = steering + random.random() * steering_noise - (steering_noise / 2)
        print("** Begin Steering deviation {}".format(deviation_angle))


    pickle.dump({"steering":steering,'throttle':throttle},fcmd)
    fcmd.flush()