# Docker file for multipass ChRIS plugin app
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build -t local/pl-multipass .
#
# In the case of a proxy (located at say http://proxy.tch.harvard.edu:3128), do:
#
#   PROXY=http://proxy.tch.harvard.edu:3128
#   docker build --build-arg http_proxy=${PROXY} --build-arg UID=$UID -t local/pl-multipass .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --entrypoint /bin/bash local/pl-multipass
#
# To pass an env var HOST_IP to container, do:
#
#   docker run -ti -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/pl-multipass
#

FROM python:3.9.1-slim-buster
LABEL maintainer="FNNDSC/ArushiVyas <dev@babyMRI.org>"

WORKDIR /usr/local/src

COPY requirements.txt .
COPY "FreeSurferColorLUT.txt" /usr/src
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

WORKDIR /usr/local/bin
CMD ["multipass", "--help"]
