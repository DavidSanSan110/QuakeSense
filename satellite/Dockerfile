FROM python:3.8

RUN mkdir /app

WORKDIR /app

ADD . /app/satellite

RUN pip install -r ./satellite/requirements.txt

RUN pip install ./satellite/ --upgrade

EXPOSE 10000

CMD ["api_satellite"]