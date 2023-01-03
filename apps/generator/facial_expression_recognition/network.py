from tensorflow.keras.layers import (Activation, Conv2D, Dense, Dropout,
                                     Flatten, MaxPooling2D)
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import RMSprop

from ..config import Config


def network():
    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding="same", input_shape=Config.input_size))
    model.add(Activation("relu"))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding="same"))
    model.add(Activation("relu"))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation("relu"))
    model.add(Dropout(0.25))
    model.add(Dense(3))
    model.add(Activation("softmax"))

    opt = RMSprop(learning_rate=0.0001)

    model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])

    model = load_model(Config.emotion_model_path)
    return model
