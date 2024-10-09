FROM python:3.8

RUN mkdir /app

WORKDIR /app

ADD . /app/detector

RUN pip install -r ./detector/requirements.txt

RUN pip install ./detector/ --upgrade

EXPOSE 10002

CMD ["api_detector"]