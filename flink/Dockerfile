FROM flink:1.12.4-scala_2.12-java11

RUN echo "Acquire::http::proxy \"${http_proxy}\";\nAcquire::https::proxy \"${https_proxy}\";" > /etc/apt/apt.conf
RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install cmake && pip3 install apache-flink==1.12.4 && pip3 install nltk

COPY mysql-connector-java-5.1.49.jar /opt/flink/lib/mysql-connector-java-8.0.19.jar
COPY pravega-connectors-flink-1.12_2.12-0.10.0.jar /opt/flink/lib/pravega-connectors-flink-1.12_2.12-0.10.0.jar
COPY flink-connector-jdbc_2.11-1.12.3.jar /opt/flink/lib/flink-connector-jdbc_2.11-1.12.3.jar
RUN ln -s /usr/bin/python3 /usr/bin/python
