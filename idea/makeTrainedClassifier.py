import tensorflow as tf
from tensorflow.keras import layers
import tifffile
from skimage import io
import numpy as np
images=io.imread('data/analysis/PunctaScan/findNumCells_Part1_1/findNumCells_Part1_NDTiffStack.tif')
classification=[0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 1, 0, 0, 0, 0,1, 0, 1, 1, 0, 1, 1, 1,0, 0, 1, 0, 0, 1, 0, 1,1, 0, 1, 1, 0, 0, 1, 0,1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1,0, 0, 0, 0, 0, 0, 0, 1]
x_train=[0]*64
x_train=[]
y_train=[]
data_augmentation = tf.keras.Sequential([
  layers.RandomFlip("horizontal_and_vertical"),
  layers.RandomRotation(0.2),
])
for i in range(64):
    x_train.append(np.array([images[i, :, :]]).reshape([512, 512, 1]).tolist())
    y_train.append(classification[i])
    for j in range(2):
        x_train.append(np.array(data_augmentation([images[i,:,:]])).reshape([512,512,1]).astype('int').tolist())
        y_train.append(classification[i])

classification=[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0,0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1,1, 1]
images=io.imread('data/analysis/PunctaSearch/firstSearch/exampleMileStone1_Part1_NDTiffStack.tif')
for i in range(64):
    x_train.append(np.array([images[i, :, :]]).reshape([512, 512, 1]).tolist())
    y_train.append(classification[i])
    for j in range(2):
        x_train.append(np.array(data_augmentation([images[i,:,:]])).reshape([512,512,1]).tolist())
        y_train.append(classification[i])


model = tf.keras.applications.ResNet50(weights=None,input_shape=(512,512,1),classes=2)

loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
model.compile(optimizer="adam", loss=loss_fn, metrics=["accuracy"])
for i in range(1000):
    #model.load_weights('data/mlmodels/puctaclassifier')
    model.fit(x_train, y_train, epochs=5, batch_size=64, validation_split=0.1)
    model.save('data/mlmodels/puctaclassifier2')