FROM ubuntu:18.04

ENV FLASK_APP main.py
ENV FLASK_CONFIG production
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

COPY requirements.txt requirements.txt

ENV TZ=Europe/Prague
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y default-mysql-server python3-mysqldb python3-dateutil \
                                         python3-editor libatlas3-base default-jre curl python3-dev gcc

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install -r requirements.txt

COPY app app
COPY migrations migrations
COPY main.py config.py boot.sh DB_CONFIG ./

# run-time configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
