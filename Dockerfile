FROM python:3

# Install OS dependencies
RUN apt-get -qq update && \
    apt-get -qq install netcat curl git wget python3 python3-pip python3-dev vim nano ffmpeg gcc g++ make libsm6 libxext6 libxrender-dev

# Build stuff for tesseract
# Based on https://medium.com/quantrium-tech/installing-tesseract-4-on-ubuntu-18-04-b6fcd0cbd78f
RUN apt-get install -y automake pkg-config libsdl-pango-dev libicu-dev libcairo2-dev bc libleptonica-dev
RUN  curl -L  https://github.com/tesseract-ocr/tesseract/archive/refs/tags/4.1.1.tar.gz  | tar xvz

WORKDIR /tesseract-4.1.1
RUN ./autogen.sh && ./configure && make -j && make install && ldconfig
# Slow! The above line takes 435 seconds on my laptop
RUN make training && make training-install
# The above line takes 59 seconds on my laptop

RUN curl -L -o tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
RUN curl -L -o tessdata/osd.traineddata https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata

ENV TESSDATA_PREFIX=/tesseract-4.1.1/tessdata
#Disable multi-threading
ENV OMP_THREAD_LIMIT=1

# Install Python dependencies
WORKDIR /usr/app
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN python -m nltk.downloader brown stopwords

# Copy in Python source
COPY . .

# Set runtime environment configuration
ENV RABBITMQ_EXCHANGE=""
ENV RABBITMQ_URI="amqp://guest:guest@localhost:5672/%2f"
ENV RABBITMQ_QUEUENAME="ExampleTask"

# Wait for RabbitMQ, then start the application
CMD ["./entrypoint.sh"]

