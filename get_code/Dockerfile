FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./

RUN mkdir ~/.aws

CMD [ "python", "./get_credentials_from_dynamo_db.py" ]
