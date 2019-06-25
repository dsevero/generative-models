.DELETE_ON_ERROR:

README.md: tex/README.tex tex/README.bib
	docker run \
		--volume "`pwd`:/data" \
		--user `id -u`:`id -g` \
		pandoc/latex \
		--output README.md \
		tex/README.tex
	cat README.md

README.pdf: tex/README.tex tex/README.bib
	docker run \
		--volume "`pwd`:/data" \
		--user `id -u`:`id -g` \
		pandoc/latex \
		--verbose \
		--output README.pdf \
		tex/README.tex
	xdg-open README.pdf
