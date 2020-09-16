# use python container image
FROM python:3.7.2-stretch

# set the working directory of the image filesystem
WORKDIR /backend

# copy current directory to the working directory
ADD . /backend

# Install the python dependencies
RUN pip install -r requirements.txt

# start the uWSGI
CMD ["uwsgi", "app.ini"]