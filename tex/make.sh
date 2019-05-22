#!/bin/bash
docker run \
  --rm \
  -it \
  --mount type=bind,source=$PWD,target=/latex \
  --workdir /latex \
  aergus/latex \
  latexmk -lualatex readables.tex
