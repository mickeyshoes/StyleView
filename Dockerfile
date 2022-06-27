FROM ubuntu:18.04

USER root

RUN apt-get update \
    apt-get upgrade \
    apt-get install git -y \
    apt-get install wget -y \
    apt-get install chromium-browser \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    dpkg -i google-chrome-stable_current_amd64.deb

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - \
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list \
    apt-get install google-chrome-stable 

RUN apt-get install -y python3 python3-pip \
    apt-get install -y mysql-server libmysqlclient-dev \
    sudo systemctl start mysql

ENV DJANGO_KEY='$=4rec%xf2cpzhknc)1k*n=-a34)d3he$-z-p!3i4m%(li%aai' \
    MYSQL_USER='root' \
    MYSQL_PWD='qwerty' \
    MYSQL_DB='StyleView' \
    INSTA_ID='test' \
    INSTA_PWD='1234'

RUN mkdir /workspace/StyleView_Server \
    git clone https://github.com/mickeyshoes/StyleView.git /workspace/StyleView_Server \
    cd /workspace/StyleView_Server/StyleView \
    pip3 install -r requirements.txt \
    python3 manage.py runserver 0.0.0.0:80