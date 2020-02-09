FROM blazemeter/taurus:latest

WORKDIR /bzt-configs

RUN pip install statsd --target=/usr/local/lib/python2.7/dist-packages/
COPY ./statsd_reporter.py /usr/local/lib/python2.7/dist-packages/bzt/modules/statsd_reporter.py
COPY ./base-config.yml /bzt-configs/base-config.yml

COPY ./test.yml ./test.yml

ENTRYPOINT ["bzt", "test.yml"]