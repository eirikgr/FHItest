#FROM python:latest
#FROM fedora:latest
#FROM alpine:latest
FROM python:2

WORKDIR CWD

CMD echo "hei"

WORKDIR /usr/src/app

RUN pip install pandas
RUN pip install matplotlib
RUN pip install openpyxl

COPY . .

COPY doANA.py .
COPY 26975.csv .
COPY county.csv .

ENV PYTHONUNBUFFERED=0

CMD ["python", "doANA.py"]