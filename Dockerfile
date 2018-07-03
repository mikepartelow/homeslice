FROM resin/rpi-raspbian

RUN apt-get update -yq
RUN apt-get install -yq python python-dev build-essential

RUN curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python

RUN pip install gevent

ADD requirements.txt /tmp/requirements.txt
RUN cd /tmp && pip install -r requirements.txt

WORKDIR /mnt/homeslice
CMD bash