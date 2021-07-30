FROM logstash:7.13.3
USER root
COPY logstash-output-pravega-0.9.0.gem /opt/
RUN /usr/share/logstash/bin/logstash-plugin install /opt/logstash-output-pravega-0.9.0.gem
RUN /usr/share/logstash/bin/logstash-plugin install logstash-filter-date_formatter
ADD . /opt/work
ENTRYPOINT ["logstash", "-f", "/opt/work/logstash.conf"]
