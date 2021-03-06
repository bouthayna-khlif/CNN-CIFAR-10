# -*- coding: utf-8 -*-
"""CNN_cifar-10.ipynb""""

import tensorflow as tf
from tensorflow.keras.datasets import cifar10
from tensorflow.keras import layers, models
import keras.models
from keras.models import Sequential
#from keras.layers.normalization import BatchNormalization
from tensorflow.keras.layers import Conv2D, MaxPooling2D,BatchNormalization, Activation
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.optimizers import Adam

def visualize_data(images, categories, class_names):
    fig = plt.figure(figsize=(14, 6))
    fig.patch.set_facecolor('white')
    for i in range(3 * 7):
        plt.subplot(3, 7, i+1)
        plt.xticks([])
        plt.yticks([])
        plt.imshow(images[i])
        class_index = categories[i].argmax()
        plt.xlabel(class_names[class_index])
    plt.show()

class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
num_classes = len(class_names)

 #split the data into test, validation and train 
 
(x_train, y_train), (x_test, y_test) = cifar10.load_data()

X= np.concatenate((x_train,x_test))
Y= np.concatenate((y_train,y_test))

x_train, x_test, y_train, y_test = train_test_split( X, Y, test_size=0.2, random_state=1)
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.2, random_state=1)



x_train = x_train / 255.0
y_train = to_categorical(y_train, num_classes)

x_val = x_val / 255.0
y_val = to_categorical(y_val, num_classes)

x_test = x_test / 255.0
y_test = to_categorical(y_test, num_classes)

#visualize_data(x_train, y_train, class_names)

print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')
print(x_val.shape[0], 'validation samples')

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


nsamples = 38400
nclasses=10
features = np.array( [ x_train[i][0].flatten() for i in range(nsamples)] )
labels   = np.array( [ x_train[i][1] for i in range(nsamples)])

# plt.hist(y_train,[0,1,2,3,4,5,6,7,8,9])



def create_model():
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(32, 32, 3)))
    model.add(BatchNormalization())
    model.add(layers.Conv2D(32, (3, 3), activation='relu', padding='same'))
    model.add(BatchNormalization())
    model.add(layers.MaxPool2D((2,2)))

    model.add(layers.Conv2D(64, (3, 3), activation='relu', padding='same',))
    model.add(BatchNormalization())
    model.add(layers.Conv2D(64, (3, 3), activation='relu', padding='same',))
    model.add(BatchNormalization())
    model.add(layers.MaxPool2D((2,2)))

    model.add(layers.Conv2D(128, (3, 3), activation='relu', padding='same',))
    model.add(BatchNormalization())
    model.add(layers.Conv2D(128, (3, 3), activation='relu', padding='same',))
    model.add(BatchNormalization())
    model.add(layers.MaxPool2D((2,2)))
   
   
    model.add(layers.Flatten())
  
    model.add(layers.Dropout(0.2))
    
    model.add(layers.Dense(128, activation='relu'))
    # model.add(layers.Dropout(0.2))
    model.add(layers.Dense(10, activation='softmax'))
    
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    return model

m_no_aug = create_model()
m_no_aug.summary()

from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
from keras.callbacks import ReduceLROnPlateau
from keras.callbacks import Callback
import math

# from google.colab import drive
# drive.mount('/content/drive')

initial_learning_rate = 0.001
def lr_step_decay(epoch, lr):
    drop_rate = 0.2
    epochs_drop = 20
    return initial_learning_rate * math.pow(drop_rate, math.floor(epoch/epochs_drop))

batch_size = 16
epochs = 1500

# earlyStopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, verbose=1, mode='auto',min_delta=0.01)
# mcp_save = tf.keras.callbacks.ModelCheckpoint('/content/drive/MyDrive/archive/mod/minff-{epoch:02d}-{val_loss:.2f}.h5', save_best_only=True, monitor='val_loss', mode='min',verbose=1,save_weights_only=False)
# reduce_lr_loss =tf.keras.callbacks.LearningRateScheduler(lr_step_decay, verbose=1)

reduce_lr_loss =tf.keras.callbacks.LearningRateScheduler(lr_step_decay, verbose=1)

# def scheduler(epoch, lr):
#     if epoch < 10:
#        return lr
#     else:
#        return lr * 0.2

# rs=tf.keras.callbacks.LearningRateScheduler(scheduler, verbose=1)

es = EarlyStopping(monitor='val_accuracy', mode='max', min_delta=0.001,verbose=1, patience=20)

mc = ModelCheckpoint('best_model.h5', monitor='val_accuracy', mode='max', verbose=1,save_best_only=True)

# reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, verbose=1,
#                               patience=5,  min_delta=0.0001,  cooldown=0 ,min_lr=0, mode='min')

# from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# keras_callbacks   = [
#       EarlyStopping(monitor='val_loss', patience=30, mode='min', min_delta=0.0001, verbose=1),
#       ModelCheckpoint(checkpoint_path, monitor='val_loss', save_best_only=True, mode='min',verbose=1)
# ]

batch_size = 32

history_no_aug = m_no_aug.fit(
    x_train, y_train,
    epochs=2000, batch_size=batch_size,
    validation_data=(x_val, y_val),
    verbose=1,  
    callbacks=[es, mc,reduce_lr_loss] )

# load a saved model
from keras.models import load_model
saved_model = load_model('best_model.h5')

# m_no_aug.save('modelcnn.h5')

_, train_acc = m_no_aug.evaluate(x_train, y_train, verbose=0)
_, test_acc = m_no_aug.evaluate(x_test, y_test, verbose=0)
print('Train: %.3f, Test: %.3f' % (train_acc, test_acc))

loss_no_aug, acc_no_aug = m_no_aug.evaluate(x_test,  y_test)

print(f"Testing on {len(x_test)} images, the results are\n Accuracy: {acc_no_aug } | Loss: {loss_no_aug}")

loss_no_aug_sav, acc_no_aug_sav = saved_model.evaluate(x_test,  y_test)

print(f"Testing on {len(x_test)} images, the results are\n Accuracy: {acc_no_aug } | Loss: {loss_no_aug}")

fig = plt.figure()
fig.patch.set_facecolor('white')
plt.plot(history_no_aug.history['accuracy'],
         label='train accuracy',
         c='dodgerblue', ls='-')
plt.plot(history_no_aug.history['val_accuracy'],
         label='validation accuracy',
         c='dodgerblue', ls='--')

plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.show()





fig = plt.figure()
fig.patch.set_facecolor('white')
plt.plot(history_no_aug.history['loss'],
         label='train loss',
         c='dodgerblue', ls='-')
plt.plot(history_no_aug.history['val_loss'],
         label='validation loss',
         c='dodgerblue', ls='--')

plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')
plt.show()

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def make_confusion_matrix(cf,
                          group_names=None,
                          categories='auto',
                          count=True,
                          percent=True,
                          cbar=True,
                          xyticks=True,
                          xyplotlabels=True,
                          sum_stats=True,
                          figsize=(15,15),
                          cmap='Blues',
                          title=None):
    '''
    This function will make a pretty plot of an sklearn Confusion Matrix cm using a Seaborn heatmap visualization.
    Arguments
    ---------
    cf:            confusion matrix to be passed in
    group_names:   List of strings that represent the labels row by row to be shown in each square.
    categories:    List of strings containing the categories to be displayed on the x,y axis. Default is 'auto'
    count:         If True, show the raw number in the confusion matrix. Default is True.
    normalize:     If True, show the proportions for each category. Default is True.
    cbar:          If True, show the color bar. The cbar values are based off the values in the confusion matrix.
                   Default is True.
    xyticks:       If True, show x and y ticks. Default is True.
    xyplotlabels:  If True, show 'True Label' and 'Predicted Label' on the figure. Default is True.
    sum_stats:     If True, display summary statistics below the figure. Default is True.
    figsize:       Tuple representing the figure size. Default will be the matplotlib rcParams value.
    cmap:          Colormap of the values displayed from matplotlib.pyplot.cm. Default is 'Blues'
                   See http://matplotlib.org/examples/color/colormaps_reference.html
                   
    title:         Title for the heatmap. Default is None.
    '''


    # CODE TO GENERATE TEXT INSIDE EACH SQUARE
    blanks = ['' for i in range(cf.size)]

    if group_names and len(group_names)==cf.size:
        group_labels = ["{}\n".format(value*10) for value in group_names]
    else:
        group_labels = blanks

    if count:
        group_counts = ["{0:0.0f}\n".format(value*10) for value in cf.flatten()]
    else:
        group_counts = blanks

    if percent:
        group_percentages = ["{0:.3}".format(value*10*100) for value in cf.flatten()/np.sum(cf)]
    else:
        group_percentages = blanks

    box_labels = [f"{v1}{v2}{v3}".strip() for v1, v2, v3 in zip(group_labels,group_counts,group_percentages)]
    box_labels = np.asarray(box_labels).reshape(cf.shape[0],cf.shape[1])


    # CODE TO GENERATE SUMMARY STATISTICS & TEXT FOR SUMMARY STATS
    if sum_stats:
        #Accuracy is sum of diagonal divided by total observations
        accuracy  = np.trace(cf) / float(np.sum(cf))

        #if it is a binary confusion matrix, show some more stats
        if len(cf)==4:
            #Metrics for Binary Confusion Matrices
            precision = cf[1,1] / sum(cf[:,1])
            recall    = cf[1,1] / sum(cf[1,:])
            f1_score  = 2*precision*recall / (precision + recall)
            stats_text = "\n\nAccuracy={:0.4f}\nPrecision={:0.4f}\nRecall={:0.4f}\nF1 Score={:0.4f}".format(
                accuracy,precision,recall,f1_score)
        else:
            stats_text = "\n\nAccuracy={:0.4f}".format(accuracy)
    else:
        stats_text = ""


    # SET FIGURE PARAMETERS ACCORDING TO OTHER ARGUMENTS
    if figsize==None:
        #Get default figure size if not set
        figsize = plt.rcParams.get('figure.figsize')

    if xyticks==False:
        #Do not show categories if xyticks is False
        categories=False




    ax = plt.figure()

    label_font = {'size':'20'}
    # MAKE THE HEATMAP VISUALIZATION
    plt.figure(figsize=figsize)
    sns.set(font_scale=1.5)
    sns.heatmap(cf,annot=box_labels,fmt="",cmap=cmap,cbar=cbar,xticklabels=categories,yticklabels=categories)

    if xyplotlabels:
        plt.ylabel('Predicted label' , fontdict=label_font);
        plt.xlabel('True label', fontdict=label_font);
        # plt.ylabel('True label')
        # plt.xlabel('Predicted label' + stats_text)
    else:
        plt.xlabel(stats_text)
    
    if title:
        plt.title(title)

model1= m_no_aug
y_pred = model1.predict(x_test) 
import numpy as np
Y_pred = np.argmax(y_pred, 1) 
Y_test = np.argmax(y_test, 1)

import sklearn
mat = sklearn.metrics.confusion_matrix(Y_test, Y_pred) # Confusion matrix
lab=['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

make_confusion_matrix(mat,
                          group_names=None,
                          categories=lab,
                          count=False,
                          percent=True,
                          cbar=True,
                          xyticks=True,
                          xyplotlabels=True,
                          sum_stats=True,
                          figsize=(14,14),
                          cmap='Blues',
                          title=None)



width_shift = 3/32
height_shift = 3/32
flip = True

datagen = ImageDataGenerator(
    horizontal_flip=flip,
    
    width_shift_range=width_shift,
    height_shift_range=height_shift,
    )
datagen.fit(x_train)

it = datagen.flow(x_train, y_train, shuffle=False)
batch_images, batch_labels = next(it)
visualize_data(batch_images, batch_labels, class_names)

mc1 = ModelCheckpoint('best_model_augmented.h5', 'val_accuracy', mode='max', verbose=1,save_best_only=True)

m_aug = create_model()
datagen.fit(x_train)

history_aug = m_aug.fit(
    datagen.flow(x_train, y_train, batch_size=batch_size),
    epochs=2500,
    validation_data=(x_val, y_val),
    verbose=1,  
    callbacks=[es, mc1,reduce_lr_loss])

loss_aug, acc_aug = m_aug.evaluate(x_test,y_test)

print(f"Testing on {len(x_test)} images, the results are\n Accuracy: {acc_aug } | Loss: {loss_aug}")

# load a saved model
from keras.models import load_model
saved_model_aug = load_model('/content/best_model_augmented.h5')

loss_aug, acc_aug = saved_model_aug.evaluate(x_test,y_test)

print(f"Testing on {len(x_test)} images, the results are\n Accuracy: {acc_aug } | Loss: {loss_aug}")

fig = plt.figure()
fig.patch.set_facecolor('white')

plt.plot(history_aug.history['accuracy'],
         label='train accuracy augmented',
         c='dodgerblue', ls='-')
plt.plot(history_aug.history['val_accuracy'],
         label='validation accuracy augmented',
         c='orange',ls='--')

plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.show()

fig = plt.figure()
fig.patch.set_facecolor('white')
plt.plot(history_no_aug.history['accuracy'],
         label='train accuracy',
         c='dodgerblue', ls='-')
plt.plot(history_no_aug.history['val_accuracy'],
         label='validation accuracy',
         c='orange', ls='--')

plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.show()



fig = plt.figure()
fig.patch.set_facecolor('white')


plt.plot(history_aug.history['loss'],
         label='train loss augmented',
         c='dodgerblue', ls='-')
plt.plot(history_aug.history['val_loss'],
         label='validation loss augmented',
         c='orange',ls='--')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')
plt.show()


fig = plt.figure()
fig.patch.set_facecolor('white')
plt.plot(history_no_aug.history['loss'],
         label='train loss',
         c='dodgerblue', ls='-')
plt.plot(history_no_aug.history['val_loss'],
         label='validation loss',
         c='orange', ls='--')

plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')
plt.show()

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def make_confusion_matrix(cf,
                          group_names=None,
                          categories='auto',
                          count=True,
                          percent=True,
                          cbar=True,
                          xyticks=True,
                          xyplotlabels=True,
                          sum_stats=True,
                          figsize=(15,15),
                          cmap='Blues',
                          title=None):
    '''
    This function will make a pretty plot of an sklearn Confusion Matrix cm using a Seaborn heatmap visualization.
    Arguments
    ---------
    cf:            confusion matrix to be passed in
    group_names:   List of strings that represent the labels row by row to be shown in each square.
    categories:    List of strings containing the categories to be displayed on the x,y axis. Default is 'auto'
    count:         If True, show the raw number in the confusion matrix. Default is True.
    normalize:     If True, show the proportions for each category. Default is True.
    cbar:          If True, show the color bar. The cbar values are based off the values in the confusion matrix.
                   Default is True.
    xyticks:       If True, show x and y ticks. Default is True.
    xyplotlabels:  If True, show 'True Label' and 'Predicted Label' on the figure. Default is True.
    sum_stats:     If True, display summary statistics below the figure. Default is True.
    figsize:       Tuple representing the figure size. Default will be the matplotlib rcParams value.
    cmap:          Colormap of the values displayed from matplotlib.pyplot.cm. Default is 'Blues'
                   See http://matplotlib.org/examples/color/colormaps_reference.html
                   
    title:         Title for the heatmap. Default is None.
    '''


    # CODE TO GENERATE TEXT INSIDE EACH SQUARE
    blanks = ['' for i in range(cf.size)]

    if group_names and len(group_names)==cf.size:
        group_labels = ["{}\n".format(value*10) for value in group_names]
    else:
        group_labels = blanks

    if count:
        group_counts = ["{0:0.0f}\n".format(value*10) for value in cf.flatten()]
    else:
        group_counts = blanks

    if percent:
        group_percentages = ["{0:.3}".format(value*10*100) for value in cf.flatten()/np.sum(cf)]
    else:
        group_percentages = blanks

    box_labels = [f"{v1}{v2}{v3}".strip() for v1, v2, v3 in zip(group_labels,group_counts,group_percentages)]
    box_labels = np.asarray(box_labels).reshape(cf.shape[0],cf.shape[1])


    # CODE TO GENERATE SUMMARY STATISTICS & TEXT FOR SUMMARY STATS
    if sum_stats:
        #Accuracy is sum of diagonal divided by total observations
        accuracy  = np.trace(cf) / float(np.sum(cf))

        #if it is a binary confusion matrix, show some more stats
        if len(cf)==4:
            #Metrics for Binary Confusion Matrices
            precision = cf[1,1] / sum(cf[:,1])
            recall    = cf[1,1] / sum(cf[1,:])
            f1_score  = 2*precision*recall / (precision + recall)
            stats_text = "\n\nAccuracy={:0.4f}\nPrecision={:0.4f}\nRecall={:0.4f}\nF1 Score={:0.4f}".format(
                accuracy,precision,recall,f1_score)
        else:
            stats_text = "\n\nAccuracy={:0.4f}".format(accuracy)
    else:
        stats_text = ""


    # SET FIGURE PARAMETERS ACCORDING TO OTHER ARGUMENTS
    if figsize==None:
        #Get default figure size if not set
        figsize = plt.rcParams.get('figure.figsize')

    if xyticks==False:
        #Do not show categories if xyticks is False
        categories=False




    ax = plt.figure()

    label_font = {'size':'20'}
    # MAKE THE HEATMAP VISUALIZATION
    plt.figure(figsize=figsize)
    sns.set(font_scale=1.5)
    sns.heatmap(cf,annot=box_labels,fmt="",cmap=cmap,cbar=cbar,xticklabels=categories,yticklabels=categories)

    if xyplotlabels:
        plt.ylabel('Predicted label' , fontdict=label_font);
        plt.xlabel('True label', fontdict=label_font);
        # plt.ylabel('True label')
        # plt.xlabel('Predicted label' + stats_text)
    else:
        plt.xlabel(stats_text)
    
    if title:
        plt.title(title)

model=m_aug
y_pred = model.predict(x_test) 
import numpy as np
Y_pred = np.argmax(y_pred, 1) 
Y_test = np.argmax(y_test, 1)

mat = sklearn.metrics.confusion_matrix(Y_test, Y_pred) # Confusion matrix
lab=['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

make_confusion_matrix(mat,
                          group_names=None,
                          categories=lab,
                          count=False,
                          percent=True,
                          cbar=True,
                          xyticks=True,
                          xyplotlabels=True,
                          sum_stats=True,
                          figsize=(14,14),
                          cmap='Blues',
                          title=None)

from keras.preprocessing import image

import random
from tensorflow.keras.preprocessing.image import img_to_array, load_img

# Get list of layers from model
layer_outputs = [layer.output for layer in m_aug.layers[1:]]

# Create a visualization model
import tensorflow
visualize_model = tensorflow.keras.models.Model(inputs = m_aug.input, outputs = layer_outputs)

# Load image for prediction
img=load_img(r'/content/dog1.jpg',target_size=(32,32))

# Convert image to array
x = img_to_array(img)

# Reshape image for passing it to prediction
x=x.reshape((1,32,32,3))
print(x.shape)
# Rescale the image
x = x /255

# Get all layers feature maps for image
feature_maps=visualize_model.predict(x)
print(len(feature_maps))

# Show names of layers available in model
layer_names = [layer.name for layer in model.layers]
print(layer_names)

# Commented out IPython magic to ensure Python compatibility.

# import required libraries
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

# Plotting the graph
for layer_names, feature_maps in zip(layer_names,feature_maps):
  print(feature_maps.shape)
  if len(feature_maps.shape) == 4 :
    channels = feature_maps.shape[-1]
    size = feature_maps.shape[1]
    display_grid = np.zeros((size, size * channels))
    for i in range(channels):
      x = feature_maps[0, :, :, i]
      x -= x.mean()
      x /= x.std()
      x *= 64
      x += 128
      x = np.clip(x, 0, 255).astype('uint8')
      # We'll tile each filter into this big horizontal grid
      display_grid[:, i * size : (i + 1) * size] = x

    scale = 20. / channels
    plt.figure(figsize=(scale * channels, scale))
    plt.title(layer_names)
    plt.grid(False)
    plt.imshow(display_grid, aspect='auto', cmap='viridis')

# afficher les cannaux 
img_path = r'/content/dog1.jpg'

# We preprocess the image into a 4D tensor
from keras.preprocessing import image
import numpy as np

img = image.load_img(img_path, target_size=(32, 32))
img_tensor = image.img_to_array(img)
img_tensor = np.expand_dims(img_tensor, axis=0)
# Remember that the model was trained on inputs
# that were preprocessed in the following way:
img_tensor /= 255.

# Its shape is (1, 150, 150, 3)
print(img_tensor.shape)


from keras import models

# Extracts the outputs of the top 8 layers:
layer_outputs = [layer.output for layer in model.layers[:15]]
# Creates a model that will return these outputs, given the model input:
activation_model = models.Model(inputs=model.input, outputs=layer_outputs)


# one array per layer activation
activations = activation_model.predict(img_tensor)
   


second_layer_activation = activations[13]
print(second_layer_activation.shape)

import matplotlib.pyplot as plt

plt.matshow(second_layer_activation[0, :, :,10], cmap='viridis')
plt.show()

first_layer_activation = activations[1]
print(second_layer_activation.shape)

import matplotlib.pyplot as plt

plt.matshow(first_layer_activation[0, :, :,2], cmap='viridis')
plt.show()

model.save("projet_complet.h5")

from keras.models import load_model
model = load_model("projet_complet.h5")

import keras

# These are the names of the layers, so can have them as part of our plot
layer_names = []
for layer in model.layers[:15]:
    layer_names.append(layer.name)

images_per_row = 16

# Now let's display our feature maps
for layer_name, layer_activation in zip(layer_names, activations):
    # This is the number of features in the feature map
    n_features = layer_activation.shape[-1]

    # The feature map has shape (1, size, size, n_features)
    size = layer_activation.shape[1]

    # We will tile the activation channels in this matrix
    n_cols = n_features // images_per_row
    display_grid = np.zeros((size * n_cols, images_per_row * size))

    # We'll tile each filter into this big horizontal grid
    for col in range(n_cols):
        for row in range(images_per_row):
            channel_image = layer_activation[0,
                                             :, :,
                                             col * images_per_row + row]
            # Post-process the feature to make it visually palatable
            channel_image -= channel_image.mean()
            channel_image /= channel_image.std()
            channel_image *= 64
            channel_image += 128
            channel_image = np.clip(channel_image, 0, 255).astype('uint8')
            display_grid[col * size : (col + 1) * size,
                         row * size : (row + 1) * size] = channel_image

    # Display the grid
    scale = 1. / size
    plt.figure(figsize=(scale * display_grid.shape[1],scale * display_grid.shape[0]))
    plt.title(layer_name)
    plt.grid(False)
    plt.imshow(display_grid, aspect='auto', cmap='viridis')
    
plt.show()
