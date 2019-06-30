from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Activation, Flatten
from keras.datasets import mnist
from keras import backend as K
from IPython.display import display
import matplotlib.pyplot as plt
import pandas as pd

K.tensorflow_backend._get_available_gpus()

def reshape_channel_first(*images):
    return (i.reshape(i.shape[0], 1, *i.shape[1:])
            for i in images)

# The data, split between train and test sets:
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = reshape_channel_first(x_train/ 255.0, x_test/ 255.0)

print('type\t\t', x_train.dtype)
print('x_train.shape\t', x_train.shape)
print('x_test.shape\t', x_test.shape)
print('y_train.shape\t', y_train.shape)
print('y_test.shape\t', y_test.shape)


model = Sequential([
    Conv2D(filters=32, 
           kernel_size=(3, 3), 
           activation='relu',
           data_format='channels_first',
           input_shape=x_train[0].shape),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(10, activation='softmax')
])

model.compile(optimizer='adam',
              # like categorical_crossentropy but for 
              # integer labels instead of one-hot encoded
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

model.fit(x_train, y_train, 
          validation_data=(x_test, y_test),
          batch_size=1_000, 
          epochs=5, 
          verbose=1);
