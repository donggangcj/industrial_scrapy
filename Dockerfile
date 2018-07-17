FROM python:3.6.0

RUN apt-get update && apt-get -y install vim && rm -rf /var/lib/apt/lists/*

WORKDIR /home/app

ENV PYTHONPATH=/home/app MYSQL_HOST="10.8.1.159" \
    MYSQL_DBNAME="jobsystem" MYSQL_USER="root" \
    MYSQL_PASSWD="1234" MYSQL_PORT="3306"


COPY . /home/app/

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

CMD ["python3", "data.py"]