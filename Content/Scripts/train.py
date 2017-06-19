import keras
from keras.layers import Conv2D,Dropout,MaxPooling2D,Dense,Flatten,BatchNormalization
from keras.models import Sequential
from keras.losses import mean_absolute_error,mean_squared_error
from keras.constraints import maxnorm
from keras.optimizers import Adam
from keras.utils.io_utils import HDF5Matrix
from keras.preprocessing import *
from keras.callbacks import ModelCheckpoint
import numpy as np
import matplotlib.pyplot as plt
import h5py

filename="../../robocar.hdf5"
input = h5py.File(filename, 'r')
imagesin=input['frontcamera']
controlsin=input['steering.throttle']

nsamples=imagesin.shape[0]
ntrain=int(nsamples*0.9)
nval=nsamples-ntrain


#imagesin = HDF5Matrix(filename, 'frontcamera',start=0,end=1000)
#controlsin = HDF5Matrix(filename, 'steering.throttle',start=0,end=1000)

width=160 #should add these to h5 parameters
height=90
print(imagesin.shape,controlsin.shape)

print(np.mean(imagesin[0:100]))
print(np.std(imagesin[0:100]))
print(np.mean(controlsin[0,0:100]))

#datagen = ImageDataGenerator(
#    featurewise_center=True,
#    featurewise_std_normalization=True)


def createCNNModel():
    # Create the model
    model = Sequential()
    model.add(Conv2D(32,(3, 3), input_shape=(height,width, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(32,(3, 3), padding='same', activation='relu'))
    model.add(Conv2D(32,(3, 3),  padding='same', activation='relu'))
    model.add(Conv2D(32,(3, 3),  padding='same', activation='relu'))
    model.add(MaxPooling2D((2,2)))
    model.add(Dropout(0.2))
    model.add(Conv2D(32,(3, 3), padding='same', activation='relu'))
    model.add(Conv2D(32,(3, 3),  padding='same', activation='relu'))
    model.add(Conv2D(32,(3, 3),  padding='same', activation='relu'))
    model.add(Conv2D(32,(3, 3),  padding='same', activation='relu'))
    model.add(MaxPooling2D((2,2)))
    model.add(Dropout(0.2))
    model.add(Conv2D(32,(3, 3), padding='same', activation='relu'))
    model.add(Conv2D(32,(3, 3),  padding='same', activation='relu'))
    model.add(Conv2D(64,(3, 3),  padding='same', activation='relu'))
    model.add(MaxPooling2D((2,2)))
    model.add(Dropout(0.2))
    model.add(Conv2D(64,(3, 3),  padding='same', activation='relu'))
    model.add(Conv2D(64,(3, 3),  padding='same', activation='relu'))
    model.add(Conv2D(64,(3, 3),  padding='same', activation='relu'))
    model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='linear'))
    # Compile model
    opt = Adam(lr=0.00001)
    model.compile(loss='mean_squared_error', optimizer=opt)
    print(model.summary())
    return model

def generator(Xh5,yh5):
    m=Xh5.shape[0]
    s=0
    while 1:
        e=s+32
        X=Xh5[s:e]
        y=yh5[s:e,0]
        yield (X,y)
        s +=32
        if s+32 > m:
            s = 0

# create our CNN model
model = createCNNModel()
print("CNN Model created.")
print(np.mean(imagesin[100:120]),np.std(imagesin[100:120]))
model.fit_generator(generator(imagesin[:ntrain],controlsin[:ntrain]), steps_per_epoch=100 ,verbose=1,
                    validation_data=generator(imagesin[ntrain:],controlsin[ntrain:]),validation_steps=10,
                    epochs=1000,callbacks=[ModelCheckpoint("model_1e.h5")])
print("evaluate")
print(model.evaluate_generator(generator(imagesin[ntrain:],controlsin[ntrain:]), 1))
print("Predict")
print(model.predict_generator(generator(imagesin[ntrain:],controlsin[ntrain:]), 10))
model.save("model_1.h5")

