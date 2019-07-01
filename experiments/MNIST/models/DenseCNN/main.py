from keras.models import Sequential
from keras.layers import (
    Conv2D,
    MaxPooling2D,
    Dense,
    Activation,
    Flatten,
    BatchNormalization,
    Dropout,
)
from keras.datasets import mnist
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
                    filters=32,
                    kernel_size=(3, 3),
                    activation="relu",
                    data_format="channels_first",
                    input_shape=input_shape,
                ),
                MaxPooling2D(pool_size=(2, 2)),
                Conv2D(
                    filters=32,
                    kernel_size=(3, 3),
                    activation="relu",
                    data_format="channels_first",
                    input_shape=input_shape,
                ),
                MaxPooling2D(pool_size=(2, 2)),
                Flatten(),
                Dense(256, activation="relu"),
                Dropout(kwargs["dropout_rate"]),
                BatchNormalization(),
                Dense(10, activation="softmax"),
            ]
        )
    else:
        raise NotImplementedError()


def load_data(validation_size=10000):
    EXPERIMENT_ROOT = Path(__file__).resolve().parents[2]
    data = pd.read_csv(EXPERIMENT_ROOT / "data/train.csv")
    test = pd.read_csv(EXPERIMENT_ROOT / "data/test.csv")
    y = data.pop("label").values
    x = data.values

    y_train, y_valid = np.split(y, [validation_size])
    x_train, x_valid = np.split(x, [validation_size])

    x_train, x_valid, x_test = reshape_channel_first(
        x_train / 255.0, x_valid / 255.0, test.values / 255.0
    )
    del data
    del test
    return (x_train, y_train), (x_valid, y_valid), (x_test, None)


@click.command()
@click.option("--batch-size", type=int)
@click.option("--epochs", type=int)
@click.option("--dropout-rate", type=float)
@click.option("--architecture", type=str)
@click.option("--submit", type=str, default="no")
def main(**kwargs):

    # The data, split between train and test sets:
    (x_train, y_train), (x_valid, y_valid), (x_test, _) = load_data()
    input_shape = x_train[0].shape

    print("type\t\t", x_train.dtype)
    print("x_train.shape\t", x_train.shape)
    print("x_valid.shape\t", x_valid.shape)
    print("y_train.shape\t", y_train.shape)
    print("y_valid.shape\t", y_valid.shape)

    model = get_model(input_shape, **kwargs)

    model.compile(
        optimizer="adam",
        # like categorical_crossentropy but for
        # integer labels instead of one-hot encoded
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    save_model_summary(model)

    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_valid, y_valid),
        batch_size=kwargs["batch_size"],
        epochs=kwargs["epochs"],
        verbose=1,
    )

    with mlflow.start_run() as run:
        mlflow.log_artifact("summary.txt", "model")
        for metric, values in history.history.items():
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
