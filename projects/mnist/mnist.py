from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Activation, Flatten, BatchNormalization, Dropout
from keras.datasets import mnist
from IPython.display import display
from mlflow.keras import log_model
from contextlib import redirect_stdout
import mlflow
import matplotlib.pyplot as plt
import pandas as pd
import click

def reshape_channel_first(*images):
    return (i.reshape(i.shape[0], 1, *i.shape[1:])
            for i in images)

def save_model_summary(model, filename='summary.txt'):
    with open(filename, 'w') as f:
        with redirect_stdout(f):
            model.summary()

def get_model(input_shape, **kwargs):
    if kwargs['architecture'] == 'DenseCNN':
        return Sequential([
            Conv2D(filters=32, 
                   kernel_size=(3, 3), 
                   activation='relu',
                   data_format='channels_first',
                   input_shape=input_shape),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(filters=32, 
                   kernel_size=(3, 3), 
                   activation='relu',
                   data_format='channels_first',
                   input_shape=input_shape),
            MaxPooling2D(pool_size=(2, 2)),
            Flatten(),
            Dense(256, activation='relu'),
            Dropout(kwargs['dropout_rate']),
            BatchNormalization(),
            Dense(10, activation='softmax')
        ])
    else:
        raise NotImplementedError()


@click.command()
@click.option("--batch-size", type=int)
@click.option("--epochs", type=int)
@click.option("--dropout-rate", type=float)
@click.option("--architecture", type=str)
def main(**kwargs):

    # The data, split between train and test sets:
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train, x_test = reshape_channel_first(x_train/ 255.0, x_test/ 255.0)
    input_shape = x_train[0].shape

    print('type\t\t', x_train.dtype)
    print('x_train.shape\t', x_train.shape)
    print('x_test.shape\t', x_test.shape)
    print('y_train.shape\t', y_train.shape)
    print('y_test.shape\t', y_test.shape)


    model = get_model(input_shape, **kwargs)

    model.compile(optimizer='adam',
                  # like categorical_crossentropy but for 
                  # integer labels instead of one-hot encoded
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    save_model_summary(model)

    history = model.fit(x_train, y_train, 
                        validation_data=(x_test, y_test),
                        batch_size=kwargs['batch_size'], 
                        epochs=kwargs['epochs'], 
                        verbose=1);

    with mlflow.start_run() as run:
        log_model(model, "model")
        mlflow.log_artifact("summary.txt", "model")
        for metric, values in history.history.items():
            for epoch, value in enumerate(values):
                mlflow.log_metric(metric, value, epoch)


if __name__ == '__main__':
    main()

