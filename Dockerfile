# Use the Python 3.8 base image
FROM python:3.8

# Set the working directory
WORKDIR /code

# Copy the requirements file
COPY requirements.txt /code/

# Install project dependencies
RUN pip install -r requirements.txt

# Copy the rest of the project files
COPY . /code/
