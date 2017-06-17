import h5py
import pickle
import numpy as np
import sys


log=open("2h5.log",'w')
log.write("Launcing 2h5")
output = h5py.File("robocar.hdf5", 'w')
input=sys.stdin.buffer
batchsz,width,height = pickle.load(input)
maxidx=0
images = output.create_dataset('frontcamera', (maxidx, height, width, 3), 'i1',
                                         maxshape=(None, height, width, 3))
images.attrs['description'] = "simple test"
controls = output.create_dataset('steering.throttle', (maxidx, 2), maxshape=(None, 2))

s=0
while True:
    imgs = pickle.load(input)
    ctrls=pickle.load(input)

    e=s+batchsz
    maxidx+=batchsz

    images.resize((maxidx, height, width, 3))
    controls.resize((maxidx, 2))
    images[s:e]=imgs
    controls[s:e]=ctrls
    output.flush()

    log.write("imgs {},ctrl {}, s {},sum {} {}\n".format(imgs.shape,ctrls.shape,s,np.sum(imgs),np.sum(images)))
    log.flush()

    s+=batchsz


