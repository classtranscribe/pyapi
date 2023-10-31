FROM classtranscribe/ct-python-platform:staging
#Tofix: no 'latest' tag; only staging tag exists at the moment

# Install Python dependencies
WORKDIR /usr/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy in Python source
COPY . .

# Set runtime environment configuration
ENV RABBITMQ_EXCHANGE=""
ENV RABBITMQ_URI="amqp://guest:guest@localhost:5672/%2f"
ENV RABBITMQ_QUEUENAME="ExampleTask"

# Wait for RabbitMQ, then start the application
CMD ["python", "./agent.py"]

