# Use the Python 3.8 base image
FROM python:3.8

# Set the working directory
WORKDIR /code

# Copy the entire project directory
COPY . /code

# Install project dependencies
RUN pip install -r code/requirements.txt
