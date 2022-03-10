FROM python:3

# Install OS dependencies
RUN apt-get -qq update && \
    apt-get -qq install netcat

# Install Python dependencies
WORKDIR /usr/app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy in Python source
COPY main.py listener.py constants.py emitter.py psycopg_wrapper.py __init__.py entrypoint.sh ./
COPY tasks ./tasks/

# Set runtime environment configuration
ENV RABBITMQ_EXCHANGE=""
ENV RABBITMQ_URI="amqp://guest:guest@localhost:5672/%2f"
ENV RABBITMQ_QUEUENAME="ExampleTask"

# Wait for RabbitMQ, then start the application
CMD ["./entrypoint.sh"]
