FROM ubuntu:16.04

RUN apt update && apt upgrade -y

RUN apt install -y python

RUN python --version
