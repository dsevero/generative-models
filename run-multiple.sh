#!/bin/bash

for d in 0.0 0.25 0.50 0.75 0.90; do
	for b in 16 32 64 128 256 512 1024 2048 4096; do
		poetry run mlflow run projects/mnist -P batch_size=$b -P dropout_rate=$d -P epochs=20 -P architecture=DenseCNN
	done
done
