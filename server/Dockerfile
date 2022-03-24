FROM ubuntu:20.04

RUN sudo apt update && \
    sudo apt install python3 python3-dev python3-pip build-essential

RUN mkdir /app
ADD requirements.txt /app

WORKDIR /app
RUN pip install -r requirements.txt

ADD *.py /app

CMD ["ryu-manager", "controller.py"]
