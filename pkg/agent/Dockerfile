FROM python:3

# Install PYthon dependencies
WORKDIR /usr/app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy in Python source
COPY main.py listener.py constants.py  __init__.py ./
COPY tasks ./tasks/

# Set runtime environment configuration
ENV RABBITMQ_QUEUENAME="ExampleTask"
ENV RABBITMQ_EXCHANGE=""
ENV RABBITMQ_URI="amqp://guest:guest@localhost:5672/%2f"

CMD ["python", "./main.py"]

