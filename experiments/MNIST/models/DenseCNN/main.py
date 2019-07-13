from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    MaxPooling2D,
    Dense,
    Activation,
    Flatten,
    BatchNormalization,
    Dropout,
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from IPython.display import display
from mlflow.keras import log_model
from contextlib import redirect_stdout
from pathlib import Path
import mlflow
import matplotlib.pyplot as plt
import pandas as pd
import click
import numpy as np
import kaggle

EXPERIMENT = 'MNIST'

def reshape_channel_first(*images):
    return (i.reshape(-1, 1, 28, 28) for i in images)


def save_model_summary(model, filename="summary.txt"):
    with open(filename, "w") as f:
        with redirect_stdout(f):
            model.summary()


def get_model(input_shape, **kwargs):
    if kwargs["architecture"] == "DenseCNN":
        return Sequential(
            [
                Conv2D(
                    filters=kwargs["conv2d_filters"],
                    kernel_size=(5, 5),
                    activation="relu",
                    data_format="channels_first",
                    input_shape=input_shape,
                    padding="same",
                ),
                MaxPooling2D(pool_size=(2, 2), padding="same"),
                Dropout(kwargs["dropout_rate"]),
                Conv2D(
                    filters=kwargs["conv2d_filters"],
                    kernel_size=(5, 5),
                    activation="relu",
                    data_format="channels_first",
                    input_shape=input_shape,
                    padding="same",
                ),
                MaxPooling2D(pool_size=(2, 2), padding="same"),
                Dropout(kwargs["dropout_rate"]),
                Flatten(),
                Dense(kwargs["dense_units"], activation="relu"),
                Dropout(kwargs["dropout_rate"]),
                BatchNormalization(),
                Dense(10, activation="softmax"),
            ]
        )
    else:
        raise NotImplementedError()


def load_data(**kwargs):
    validation_size = kwargs['validation_size']
    EXPERIMENT_ROOT = Path(__file__).resolve().parents[2]
    data = pd.read_csv(EXPERIMENT_ROOT / "data/train.csv")
    test = pd.read_csv(EXPERIMENT_ROOT / "data/test.csv")
    y = data.pop("label").values
    x = data.values

    y_valid, y_train = np.split(y, [validation_size])
    x_valid, x_train = np.split(x, [validation_size])

    x_train, x_valid, x_test = reshape_channel_first(
        x_train / 255.0, x_valid / 255.0, test.values / 255.0
    )
    del data
    del test
    return (x_train, y_train), (x_valid, y_valid), (x_test, None)


def data_augmentation():
    datagen = ImageDataGenerator(
        data_format="channels_first",
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=10,  # randomly rotate images in the range (degrees, 0 to 180)
        zoom_range=0.1,  # Randomly zoom image
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=False,  # randomly flip images
        vertical_flip=False,
    )  # randomly flip images

    return datagen


@click.command()
@click.option("--batch-size", type=int)
@click.option("--epochs", type=int)
@click.option("--dropout-rate", type=float)
@click.option("--architecture", type=str)
@click.option("--submit", type=str)
@click.option("--conv2d_filters", type=int)
@click.option("--dense_units", type=int)
@click.option("--validation_size", type=int)
def main(**kwargs):

    # The data, split between train and test sets:
    (x_train, y_train), (x_valid, y_valid), (x_test, _) = load_data(**kwargs)
    input_shape = x_train[0].shape

    print("type\t\t", x_train.dtype)
    print("x_train.shape\t", x_train.shape)
    print("x_valid.shape\t", x_valid.shape)
    print("y_train.shape\t", y_train.shape)
    print("y_valid.shape\t", y_valid.shape)

    datagen = data_augmentation()
    datagen.fit(x_train)

    model = get_model(input_shape, **kwargs)

    model.compile(
        optimizer="rmsprop",
        # like categorical_crossentropy but for
        # integer labels instead of one-hot encoded
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    save_model_summary(model)

    history = model.fit_generator(
        datagen.flow(x_train, y_train, batch_size=kwargs["batch_size"]),
        validation_data=(x_valid, y_valid),
        steps_per_epoch=x_train.shape[0] // kwargs["batch_size"],
        epochs=kwargs["epochs"],
        verbose=1,
    )

    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run() as run:
        mlflow.log_artifact("summary.txt", "model")
        metrics = history.history
        metrics["emp_gen_loss"] = np.array(metrics["val_loss"]) - np.array(metrics["loss"])
        for metric, values in metrics.items():
            for epoch, value in enumerate(values):
                mlflow.log_metric(metric, value, epoch)

        if kwargs["submit"] == "yes":
            results = model.predict(x_test)
            results = np.argmax(results, axis=1)
            results = pd.Series(results, name="Label")
            submission = pd.concat([pd.Series(range(1, 28001), name="ImageId"), results], axis=1)
            submission.to_csv("MNIST-DenseCNN.csv", index=False)
            mlflow.log_artifact("MNIST-DenseCNN.csv", "kaggle")
            message = f"mlflow.run_id: {run.info.run_id}"
            submission_data = kaggle.api.competition_submit(
                file_name="MNIST-DenseCNN.csv", message=message, competition="digit-recognizer"
            )


if __name__ == "__main__":
    main()
