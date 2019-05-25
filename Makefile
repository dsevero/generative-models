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
		-s \
		-t gfm \
		--toc \
		-o README.md \
		tex/README.tex

README.pdf: tex/README.tex tex/references.bib
	docker run \
		--volume "`pwd`:/data" \
		--user `id -u`:`id -g` \
		pandoc/latex tex/README.tex \
		-o README.pdf -t latex
