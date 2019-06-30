#!/bin/bash

for d in 0.0 0.25 0.50 0.75 0.90; do
	for b in 512 1024 2048 4096; do
		poetry run mlflow run experiments/MNIST/DenseCNN --experiment-name MNIST -P batch_size=$b -P dropout_rate=$d -P epochs=100 -P architecture=DenseCNN
	done
done
