# display a frame saved from AIAgent.py
import pickle
import numpy as np
import matplotlib.pyplot as plt
import h5py

input = h5py.File("../../robocar.hdf5", 'r')
imagesin=input['frontcamera']
anglesin=input['steering.throttle']

print(imagesin.shape)
print(anglesin.shape)

plt.ion()
for idx in range(imagesin.shape[0]):
    print(idx,anglesin[idx],imagesin[idx].shape)
    plt.imshow(imagesin[idx]*255)
    plt.pause(0.0001)
