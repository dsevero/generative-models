.DELETE_ON_ERROR:

README.md: tex/README.tex tex/README.bib build-image
	docker run \
		--volume "`pwd`:/data" \
		--user `id -u`:`id -g` \
		dsevero/generative-models \
		--verbose \
		--bibliography=tex/README.bib \
		--atx-headers \
		--webtex=https://latex.codecogs.com/png.latex? \
		--standalone \
		--to gfm \
		--toc \
		--output README.md \
		tex/README.tex
	cat README.md

README.pdf: tex/README.tex tex/README.bib build-image
	mkdir -p build/
	docker run \
		--volume "`pwd`:/data" \
		--user `id -u`:`id -g` \
		dsevero/generative-models \
		--verbose \
		--bibliography=tex/README.bib \
		--to latex \
		--toc \
		--output README.pdf \
		tex/README.tex
	xdg-open README.pdf

build-image: Dockerfile
	docker build -t dsevero/generative-models .
	touch build-image
