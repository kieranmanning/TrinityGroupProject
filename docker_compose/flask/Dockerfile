FROM centos:7
MAINTAINER Kieran Manning "kmanning@renre.com"  

RUN yum install -y epel-release supervisor

RUN yum install -y supervisor

RUN yum install -y python-pip 

RUN pip install flask pymongo

RUN mkdir -p /opt/app/templates

ADD index.html /opt/app/templates/index.html

ADD app.py /opt/app/app.py

ADD app.ini /etc/supervisord.d/app.ini
 
CMD supervisord -c /etc/supervisord.conf -n 