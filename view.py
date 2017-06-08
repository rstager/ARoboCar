# display a frame saved from AIAgent.py
import pickle
import numpy as np
import matplotlib.pyplot as plt

img=pickle.load( open( "viewport.data", "rb" ) )
#data=np.array(pixels).reshape((790,1394,4)).astype(np.uint8)
#print(data.shape)
#img=data[:,:,0:3]
print(img.shape)
plt.imshow(img)
plt.show()
