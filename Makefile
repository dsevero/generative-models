.DELETE_ON_ERROR:
.PHONY: README.md jupyter ipython-kernel tensorboard black

bin/gh-md-toc:
	mkdir -p bin
	wget https://raw.githubusercontent.com/ekalinin/github-markdown-toc/master/gh-md-toc
	chmod a+x gh-md-toc
	mv gh-md-toc bin/

README.md: bin/gh-md-toc
	./bin/gh-md-toc --insert README.md
	rm -f README.md.orig.* README.md.toc.*

ipython-kernel:
	poetry run ipython kernel install --user --name=generative-models

jupyter:
	mkdir -p logs/nohup
	nohup poetry run jupyter notebook src/ > logs/nohup/jupyter.log &

tensorboard:
	mkdir -p logs/nohup
	nohup poetry run tensorboard --logdir logs/tensorboard/ > logs/nohup/tensorboard.log &
	sleep 2
	cat logs/nohup/tensorboard.log

black:
	poetry run black projects --line-length 100

install:
	poetry run pip install --upgrade pip
	poetry update -vv
	$(MAKE) ipython-kernel
