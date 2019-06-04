FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install retry

COPY . ./

RUN mkdir ~/.aws

RUN apt-get update
RUN apt-get install less

CMD [ "python", "./get_credentials_from_dynamo_db.py" ]
