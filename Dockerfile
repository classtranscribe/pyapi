FROM --platform=linux/amd64 python:3.11-slim-bookworm
# Decord is not available on ARM64 (=OSX), so we are forced to build amd64
# Future todo: The decord source build instructions here are insufficient and outdated
# https://github.com/dmlc/decord#installation


# Install OS dependencies
RUN apt-get -qq update && \
    apt-get -qq install --no-install-recommends vim-tiny  netcat-openbsd curl git wget ffmpeg build-essential libsm6 libxext6 libxrender-dev automake libtool pkg-config libsdl-pango-dev libicu-dev libcairo2-dev bc libleptonica-dev && \
    apt-get -qq clean autoclean && \
    apt-get -qq autoremove && \
    rm -rf /var/lib/apt/lists/*

# Build stuff for tesseract
# Based on https://medium.com/quantrium-tech/installing-tesseract-4-on-ubuntu-18-04-b6fcd0cbd78f
RUN curl -L https://github.com/tesseract-ocr/tesseract/archive/refs/tags/4.1.3.tar.gz | tar xvz

#RUN curl -L https://github.com/tesseract-ocr/tesseract/archive/refs/tags/4.1.1.tar.gz | tar xvz
# Max threads 2 required for cross platform build on M1 Macs :-( otherwise a build all fails even with 6GB RAM +3GB swap for Docker machine
ARG MAX_THREADS="2"

WORKDIR /tesseract-4.1.3
RUN ./autogen.sh && ./configure && make -j ${MAX_THREADS} && make -j ${MAX_THREADS} install && ldconfig
# Slow! The above line takes 435 seconds on my laptop (1590.8s on a M1 cross compiling to amd64)
RUN make -j ${MAX_THREADS} training && make -j ${MAX_THREADS} training-install
# The above line takes 59 seconds on my laptop. 127.3s on my M1 laptop cross compiling

RUN curl -L -o tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
RUN curl -L -o tessdata/osd.traineddata https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata

ENV TESSDATA_PREFIX=/tesseract-4.1.3/tessdata
#Disable multi-threading
ENV OMP_THREAD_LIMIT=1

# Install Python dependencies
WORKDIR /usr/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Slow. The above line took 5055.6s on my M1 16GB laptop (cross compiling, 6GB Ram+8cores for docker VM; maybe it was swapping...)

# Additional dependencies for brown corpus/stopwords, wordnet
RUN python -m nltk.downloader brown stopwords wordnet omw-1.4

# Copy in Python source
COPY . .

# Set runtime environment configuration
ENV RABBITMQ_EXCHANGE=""
ENV RABBITMQ_URI="amqp://guest:guest@localhost:5672/%2f"
ENV RABBITMQ_QUEUENAME="ExampleTask"

# Wait for RabbitMQ, then start the application
CMD ["python", "./agent.py"]

