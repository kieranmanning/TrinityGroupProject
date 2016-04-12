FROM centos:7
MAINTAINER Kieran Manning "kmanning@renre.com"  

RUN yum install -y haproxy epel-release

RUN yum install -y supervisor

ADD haproxy.cfg /etc/haproxy/haproxy.cfg

ADD haproxy.ini /etc/supervisord.d/haproxy.ini

CMD supervisord -c /etc/supervisord.conf -n 