#!/bin/bash

for u in 50 100 200 500; do
	for f in 8 32 128 256; do
		time poetry run mlflow run experiments/MNIST/models/DenseCNN --experiment-name MNIST -P batch_size=8192 -P dropout_rate=0.4 -P epochs=200 -P dense_units=$u -P conv2d_filters=$f
	done
done
