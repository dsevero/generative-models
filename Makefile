.DELETE_ON_ERROR:
.PHONY: toc README.md

bin/gh-md-toc:
	mkdir -p bin
	wget https://raw.githubusercontent.com/ekalinin/github-markdown-toc/master/gh-md-toc
	chmod a+x gh-md-toc
	mv gh-md-toc bin/

README.md: tex/README.tex tex/references.bib
	docker run \
		--volume "`pwd`:/data" \
		--user `id -u`:`id -g` \
		pandoc/latex \
		--atx-headers \
		--webtex=https://latex.codecogs.com/png.latex? \
		--standalone \
		--to gfm \
		--toc \
		--output README.md \
		tex/README.tex

build/README.pdf: tex/README.tex tex/references.bib
	mkdir -p build/
	docker run \
		--volume "`pwd`:/data" \
		--user `id -u`:`id -g` \
		pandoc/latex \
		--to latex \
		--toc \
		--output build/README.pdf \
		tex/README.tex
