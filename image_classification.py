

import tensorflow as tf

from tensorflow.keras.preprocessing.image import ImageDataGenerator

import os
import numpy as np
import matplotlib.pyplot as plt

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import RMSprop

"""## Loading Data"""

!rm -rf data && mkdir data && wget http://info.iut-bm.univ-fcomte.fr/staff/couturie/images.zip  && unzip images.zip -d data/
!ls data

TRAIN_DIR = 'data/train'
VALIDATION_DIR = 'data/validation'

train_men_dir = 'data/train/men'  # directory with our training men pictures
train_women_dir = 'data/train/women'  # directory with our training women pictures
validation_men_dir = 'data/validation/men'  # directory with our validation men pictures
validation_women_dir = 'data/validation/women'  # directory with our validation women pictures

num_men_tr = len(os.listdir(train_men_dir))
num_women_tr = len(os.listdir(train_women_dir))

num_men_val = len(os.listdir(validation_men_dir))
num_women_val = len(os.listdir(validation_women_dir))

total_train = num_men_tr + num_women_tr
total_val = num_men_val + num_women_val

"""## Data Summary"""

print('Total training men images:', num_men_tr)
print('Total training women images:', num_women_tr)

print('Total validation men images:', num_men_val)
print('Total validation women images:', num_women_val)
print("---------------------")
print("Total training images:", total_train)
print("Total validation images:", total_val)

"""## Setting Model Parameters"""

BATCH_SIZE = 32
IMG_SHAPE  = 150

"""## Data Flow & Data Augmentation"""

data_augmentation = True

if not data_augmentation:
  print('Not using data augmentation.')
  train_datagen = ImageDataGenerator(rescale=1./255)
else:
  print('Using real-time data augmentation.')
  # train_datagen = ImageDataGenerator(
  #       rescale=1./255,
  #       rotation_range=40,
  #       width_shift_range=0.2,
  #       height_shift_range=0.2,
  #       shear_range=0.2,
  #       zoom_range=0.2,
  #       horizontal_flip=True,
  #       fill_mode='nearest')
  train_datagen = ImageDataGenerator(
          featurewise_center=False,  # set input mean to 0 over the dataset
          samplewise_center=False,  # set each sample mean to 0
          featurewise_std_normalization=False,  # divide inputs by std of the dataset
          samplewise_std_normalization=False,  # divide each input by its std
          zca_whitening=False,  # apply ZCA whitening
          zca_epsilon=1e-06,  # epsilon for ZCA whitening
          rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
          # randomly shift images horizontally (fraction of total width)
          width_shift_range=0.1,
          # randomly shift images vertically (fraction of total height)
          height_shift_range=0.1,
          shear_range=0.,  # set range for random shear
          zoom_range=0.,  # set range for random zoom
          channel_shift_range=0.,  # set range for random channel shifts
          # set mode for filling points outside the input boundaries
          fill_mode='nearest',
          cval=0.,  # value used for fill_mode = "constant"
          horizontal_flip=True,  # randomly flip images
          vertical_flip=False,  # randomly flip images
          # set rescaling factor (applied before any other transformation)
          rescale=1./255,
          # set function that will be applied on each input
          preprocessing_function=None,
          # image data format, either "channels_first" or "channels_last"
          data_format=None,
          # fraction of images reserved for validation (strictly between 0 and 1)
          validation_split=0.0)


# train_generator = train_datagen.flow_from_directory(batch_size=BATCH_SIZE,
#                                                     directory=TRAIN_DIR,
#                                                     shuffle=True,
#                                                     target_size=(IMG_SHAPE,IMG_SHAPE),
#                                                     class_mode='binary')

train_generator = train_datagen.flow_from_directory(batch_size=BATCH_SIZE,
                                                    directory=TRAIN_DIR,
                                                    target_size=(IMG_SHAPE,IMG_SHAPE),
                                                    class_mode='binary')

val_datagen = ImageDataGenerator(rescale=1./255)

val_generator = val_datagen.flow_from_directory(batch_size=BATCH_SIZE,
                                                  directory=VALIDATION_DIR,
                                                  target_size=(IMG_SHAPE, IMG_SHAPE),
                                                  class_mode='binary')

"""## Simple Convolutional Neural Network"""

import keras
from keras.layers import Dense, Dropout, Activation, Flatten, Input
from keras.models import Model
from keras.layers import Input

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(150, 150, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),

    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),

    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),

    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),

    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(2)
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

model.summary()

"""### Result With No Data Augmentation (Shows Overfitting)"""

callback = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', patience=10, restore_best_weights=True)
epochs=30
history = model.fit(
    train_generator,
    epochs=epochs,
    callbacks=[callback],
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

"""### Result With Data Augmentation

"""

callback = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', patience=10, restore_best_weights=True)
epochs=30
history = model.fit(
    train_generator,
    epochs=epochs,
    callbacks=[callback],
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

"""## Densenet121

### Train All Layers
"""

from tensorflow.keras.applications import DenseNet121

net= DenseNet121(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:]:
    layer.trainable = True

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# This callback will stop the training when there is no improvement in
# the validation loss for three consecutive epochs.
callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, mode='min')

# train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=20
history = model.fit(
    train_generator,
    epochs=epochs,
    callbacks=[callback],
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

"""### Freeze All Layers

"""

from tensorflow.keras.applications import DenseNet121

net= DenseNet121(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:]:
    layer.trainable = False

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# This callback will stop the training when there is no improvement in
# the validation loss for three consecutive epochs.
callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)

# train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=20
history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

"""### Freeze All Layers Except Last X Layers

"""

from tensorflow.keras.applications import DenseNet121

net= DenseNet121(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:-5]:
    layer.trainable = False

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=10
history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

"""## Xception (Our Highest Accuracy Model)"""

from tensorflow.keras.applications import Xception

net= Xception(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:]:
    layer.trainable = True

x = net.output
x = Flatten()(x)
x = Dropout(0.3)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# Let's train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=50
callback = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', patience=10, restore_best_weights=True)

history = model.fit(
    train_generator,
    epochs=epochs,
    callbacks = [callback],
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

"""## MobileNetV2 

"""

from tensorflow.keras.applications import MobileNetV2

net= MobileNetV2(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:-5]:
    layer.trainable = False

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# Train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=10

history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

"""## NASNetLarge"""

from tensorflow.keras.applications import NASNetLarge

net= NASNetLarge(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:]:
    layer.trainable = True

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# Let's train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=50

callback = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', patience=40, restore_best_weights='True')

history = model.fit(
    train_generator,
    epochs=epochs,
    callbacks=[callback],
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

"""## InceptionResNetV2

"""

from tensorflow.keras.applications import InceptionResNetV2

net= InceptionResNetV2(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:-7]:
    layer.trainable = False

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# Train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=50
callback = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', patience=40, restore_best_weights='True')

history = model.fit(
    train_generator,
    epochs=epochs,
    callbacks=[callback],
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

"""## VGG16"""

from tensorflow.keras.applications import VGG16

net= VGG16(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:-5]:
    layer.trainable = False

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# Train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=10

history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

"""## VGG19

"""

from tensorflow.keras.applications import VGG19

net= VGG19(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:-5]:
    layer.trainable = False

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# Train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=10

history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

"""## InceptionV3 """

from tensorflow.keras.applications import InceptionV3

net= InceptionV3(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:-5]:
    layer.trainable = False

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# Train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=10
callback = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', patience=40, restore_best_weights='True')

history = model.fit(
    train_generator,
    epochs=epochs,
    callbacks=[callback],
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

"""## ResNet101V2 

"""

from tensorflow.keras.applications import ResNet101V2

net= ResNet101V2(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:-5]:
    layer.trainable = False

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# Train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=10

history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

"""## ResNet152V2 """

from tensorflow.keras.applications import ResNet152V2

net= ResNet152V2(include_top=False, weights='imagenet', input_tensor=Input(shape=(150,150,3))) 

for layer in net.layers[:-5]:
    layer.trainable = False

x = net.output
x = Flatten()(x)
x = Dropout(0.5)(x)
output_layer = Dense(1, activation='sigmoid', name='sigmoid')(x)
model = Model(inputs=net.input, outputs=output_layer)

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)

# Train the model using RMSprop
model.compile(loss='binary_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

epochs=10

history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=val_generator,
    workers=4
)

score = model.evaluate(val_generator,verbose=2)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()
