###################################################
# Lightweight Hippocampe container
###################################################

# Build the base from J8 Alpine
FROM openjdk:8-jre-alpine

RUN apk add --update --no-cache python \
    python-dev \
    py-pip \
    git \
    curl \
    nodejs \
    nodejs-npm

RUN npm install -g bower
RUN pip install --upgrade pip && \
    pip install apscheduler \
	Configparser \
	elasticsearch==5.5.3 \
	flask \
	python-dateutil \
	requests \
	urllib3==1.23

COPY ./core /opt/hippocampe/core
COPY docker-entrypoint.sh /

RUN adduser hippo -D
RUN chown -R hippo:hippo /opt/hippocampe /docker-entrypoint.sh

USER hippo

RUN cd /opt/hippocampe/core/static && bower install

ENTRYPOINT /docker-entrypoint.sh
