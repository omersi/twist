FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

RUN mkdir ~/.aws

RUN alias la="ls -la --color"
RUN apt-get update
RUN apt-get install less

CMD [ "python", "./get_credentials_from_dynamo_db.py" ]
