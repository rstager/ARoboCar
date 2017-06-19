import h5py
import pickle
import numpy as np
import sys
import simulator

# This controller just follows the PID recommendations
def hook(config):
    print(config)
    return config

sim=simulator.Simulator()
sim.connect(hook)


while True:
    state=sim.get_state()
    print("pathdistance {:7f} offset {:5f} distance {:7f} angle {:5.3f} dt={:5.4f}".format(state["pathdistance"], state["offset"], state["PIDthrottle"], state["PIDsteering"],state["delta_time"]))
    sim.send_cmd({"steering":state["PIDsteering"],'throttle':state["PIDthrottle"]})
