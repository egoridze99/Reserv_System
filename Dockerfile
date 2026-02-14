# use python container image
FROM python:3.12-slim

# set the working directory of the image filesystem
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY . .

EXPOSE 5000

# start the uWSGI
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:configure_application()"]