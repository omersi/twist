FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install retry

COPY . ./

RUN mkdir ~/.aws
RUN python3 -m unittest test_get_credntials_from_dynamo_db.py

RUN apt-get update
RUN apt-get install less

CMD [ "python", "./get_credentials_from_dynamo_db.py" ]
