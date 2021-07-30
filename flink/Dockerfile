FROM flink:1.12.4-scala_2.12-java11

RUN echo "Acquire::http::proxy \"${http_proxy}\";\nAcquire::https::proxy \"${https_proxy}\";" > /etc/apt/apt.conf
RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install cmake && pip3 install apache-flink==1.12.4 && pip3 install nltk
RUN ln -s /usr/bin/python3 /usr/bin/python
