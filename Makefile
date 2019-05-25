.DELETE_ON_ERROR:
.PHONY: toc README.md build/README.pdf

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
		--bibliography=tex/references.bib \
		--atx-headers \
		--webtex=https://latex.codecogs.com/png.latex? \
		--standalone \
		--to gfm \
		--toc \
		--output README.md \
		tex/README.tex
	cat README.md

build/README.pdf: tex/README.tex tex/references.bib
	mkdir -p build/
	docker run \
		--volume "`pwd`:/data" \
		--user `id -u`:`id -g` \
		pandoc/latex \
		--bibliography=tex/references.bib \
		--to latex \
		--toc \
		--output build/README.pdf \
		tex/README.tex
	xdg-open build/README.pdf
