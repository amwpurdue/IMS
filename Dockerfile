FROM python:3.11

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install \
    python3-dev \
    build-essential

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt --src /usr/local/src

COPY . .

EXPOSE 5000
CMD [ "python", "ims_main.py" ]