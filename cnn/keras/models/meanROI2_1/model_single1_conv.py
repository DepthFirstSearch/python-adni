from keras.models import Sequential
from keras.layers.convolutional import Convolution3D
from keras.layers.core import Flatten, Dropout, Dense
from keras.layers.noise import GaussianNoise
from keras.regularizers import l2


def build_model(input_shape=(1, 18, 18, 18)):
	model = Sequential()
        model.add(GaussianNoise(0.001, input_shape=input_shape, name='meanROI2_1_noise1'))
	model.add(Convolution3D(32, 5, 5, 5, activation='relu', W_regularizer=l2(0.0001), name='meanROI2_1_conv1'))
        model.add(Dropout(1.0/12, name='meanROI2_1_dropout1'))
	model.add(Convolution3D(32, 5, 5, 5, activation='relu', W_regularizer=l2(0.0001), name='meanROI2_1_conv2'))
        model.add(Dropout(1.0/12, name='meanROI2_1_dropout2'))
        model.add(Convolution3D(64, 5, 5, 5, activation='relu', W_regularizer=l2(0.0001), name='meanROI2_1_conv3'))
        model.add(Dropout(1.0/12, name='meanROI2_1_dropout3'))
        model.add(Convolution3D(64, 3, 3, 3, activation='relu', W_regularizer=l2(0.0001), name='meanROI2_1_conv4'))
        model.add(Dropout(1.0/12, name='meanROI2_1_dropout4'))
	model.add(Convolution3D(128, 3, 3, 3, activation='relu', W_regularizer=l2(0.0001), name='meanROI2_1_conv5'))
        model.add(Dropout(1.0/12, name='meanROI2_1_dropout5'))
        model.add(Convolution3D(256, 2, 2, 2, activation='relu', W_regularizer=l2(0.0001), name='meanROI2_1_conv6'))
        model.add(Dropout(1.0/12, name='meanROI2_1_dropout6'))
	model.add(Flatten(name='meanROI2_1_flatten1'))
	return model

