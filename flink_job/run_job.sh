pip3 install /opt/cached/log_analyzer-0.2.tar.gz
flink run -py ./flink_demo.py -jar /opt/flink_job/pravega-connectors-flink-1.12_2.12-0.10.0.jar -d
