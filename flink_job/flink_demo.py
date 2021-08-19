import os
import pyflink
from pyflink import version
import logging

from pyflink.common.typeinfo import Types
from pyflink.table.table_environment import StreamTableEnvironment
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table.window import Tumble
from pyflink.common.serialization import Encoder, SimpleStringEncoder
from pyflink.table.expressions import lit
from pyflink.table.udf import udf
from pyflink.table import ScalarFunction, DataTypes
from pyflink.table.expressions import col
from pyflink.datastream.connectors import StreamingFileSink, OutputFileConfig
from log_analyzer.analyzer import Analyzer
from log_analyzer.cluster import refactor_string

print(version.__version__)

class ClassifyCl(ScalarFunction):
    def __init__(self):
        self.analyzer = Analyzer()
    def eval(self, input):

        if input is None:
            return False

        rate = self.analyzer.inspect_text(input).prob(True)
        logging.info("%s    %s", rate, input)
        return rate

class SimplifyStringCl(ScalarFunction):

    def eval(self, input):
        return refactor_string(input)

print("start demo")
env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(stream_execution_environment=env)

Classify = udf(ClassifyCl(), [DataTypes.STRING()], result_type=DataTypes.FLOAT())
SimplifyString = udf(SimplifyStringCl(), [DataTypes.STRING()], result_type=DataTypes.STRING())

t_env.create_temporary_function("Classify", Classify)
t_env.create_temporary_function("SimplifyString", SimplifyString)

# write all the data to one file
t_env.get_config().get_configuration().set_string("pipeline.jars", "file:///opt/flink/lib/pravega-connectors-flink-1.12_2.12-0.10.0.jar")

t_env.set_python_requirements(
    requirements_file_path="/opt/flink/job/requirements.txt",
    requirements_cache_dir="/opt/cached")

URI = "tcp://pravega:9090"

def create_table():
    return f"""CREATE TABLE source_table (
    task_id BIGINT,
    task_hash BIGINT,
    log_type STRING,
    message STRING,
    level STRING,
    event_time TIMESTAMP(3),
    WATERMARK FOR event_time AS event_time - INTERVAL '1' SECOND
) WITH (
    'connector' = 'pravega',
    'controller-uri' = '{URI}',
    'scope' = 'demo',
    'scan.execution.type' = 'streaming',
    'scan.streams' = 'myStream',
    'format' = 'json'
)"""

mysqlSink = """
    CREATE TABLE mysqlsink (
        task_id BIGINT,
        task_hash BIGINT,
        log_type STRING,
        rate FLOAT,
        message STRING,
        short_description STRING
    )
    with (
        'connector' = 'jdbc',
        'url' = 'jdbc:mysql://mysql:3306/demo',
        'username' = 'test',
        'password' = '123456',
        'table-name' = 'keyErrorLog'
    )
"""

print(create_table())
t_env.execute_sql(create_table())
t_env.execute_sql(mysqlSink)

filter_sql = """SELECT task_id, task_hash, log_type, MAX(Classify(message)), message, SimplifyString(message)
  FROM source_table
 GROUP BY task_id, task_hash, message, log_type, TUMBLE(event_time, INTERVAL '10' SECOND) HAVING Classify(message) > 0.75
"""

t_env.sql_query(filter_sql).execute_insert("mysqlsink")
