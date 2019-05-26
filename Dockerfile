FROM aergus/latex
RUN apt update -y &&\
    apt upgrade -y &&\
    apt install -y pandoc pandoc-citeproc texlive-bibtex-extra
WORKDIR /data
ENTRYPOINT ["pandoc"]
