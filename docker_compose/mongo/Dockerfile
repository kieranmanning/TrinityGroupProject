FROM centos:7
MAINTAINER Kieran Manning "kmanning@renre.com"  

ADD mongodb.repo /etc/yum.repos.d/mongodb.repo

RUN yum install -y mongodb-org epel-release

RUN yum install -y supervisor

ADD mongo.ini /etc/supervisord.d/mongo.ini

ADD mongo.conf /etc/mongod.conf

CMD supervisord -c /etc/supervisord.conf -n 