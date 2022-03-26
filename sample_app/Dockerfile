FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
ENV PORT 8080

# Copy local code to the container image.
COPY . /src
WORKDIR /src

RUN apt-get update -y
RUN apt-get -y install  python3-dev default-libmysqlclient-dev build-essential

RUN python3.9 -m pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel
RUN python3.9 -m pip install --no-cache-dir \
    -r requirements.txt
# Install Python Requirements
RUN pip install -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:"create_app()"

# To run locally after installation of Docker Desktop
# docker run -p 3000:8080 --rm -it $(docker build -q .)
