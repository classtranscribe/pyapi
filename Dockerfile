FROM python:3-slim

# Install OS dependencies
RUN apt-get -qq update && \
    apt-get -qq install --no-install-recommends netcat curl git wget ffmpeg build-essential libsm6 libxext6 libxrender-dev automake libtool pkg-config libsdl-pango-dev libicu-dev libcairo2-dev bc libleptonica-dev && \
    apt-get -qq clean autoclean && \
    apt-get -qq autoremove && \
    rm -rf /var/lib/apt/lists/*

# Build stuff for tesseract
# Based on https://medium.com/quantrium-tech/installing-tesseract-4-on-ubuntu-18-04-b6fcd0cbd78f
RUN curl -L https://github.com/tesseract-ocr/tesseract/archive/refs/tags/4.1.1.tar.gz | tar xvz

ARG MAX_THREADS=""

WORKDIR /tesseract-4.1.1
RUN ./autogen.sh && ./configure && make -j ${MAX_THREADS} && make -j ${MAX_THREADS} install && ldconfig
# Slow! The above line takes 435 seconds on my laptop
RUN make -j ${MAX_THREADS} training && make -j ${MAX_THREADS} training-install
# The above line takes 59 seconds on my laptop

RUN curl -L -o tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
RUN curl -L -o tessdata/osd.traineddata https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata

ENV TESSDATA_PREFIX=/tesseract-4.1.1/tessdata
#Disable multi-threading
ENV OMP_THREAD_LIMIT=1

# Install Python dependencies
WORKDIR /usr/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Additional dependencies for brown corpus/stopwords
RUN python -m nltk.downloader brown stopwords

# Copy in Python source
COPY . .

# Set runtime environment configuration
ENV RABBITMQ_EXCHANGE=""
ENV RABBITMQ_URI="amqp://guest:guest@localhost:5672/%2f"
ENV RABBITMQ_QUEUENAME="ExampleTask"

# Wait for RabbitMQ, then start the application
CMD ["python", "./agent.py"]

