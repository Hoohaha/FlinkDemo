import os
import pyflink
from pyflink import version


from pyflink.common.typeinfo import Types
from pyflink.table.table_environment import StreamTableEnvironment
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table.window import Tumble
from pyflink.common.serialization import Encoder, SimpleStringEncoder
from pyflink.table.expressions import lit
from pyflink.table.udf import udf
from pyflink.table import ScalarFunction, DataTypes
from log_analyzer.analyzer import Analyzer
from pyflink.table.expressions import col
from pyflink.datastream.connectors import StreamingFileSink, OutputFileConfig


print(version.__version__)

class ContainsErrorCl(ScalarFunction):
    def __init__(self):
        self.analyzer = Analyzer()
    def eval(self, input):
        import logging
        if input is None:
            return False

        rate = self.analyzer.inspect_text(input).prob(True)
        logging.info("%s    %s", rate, input)
        return rate

print("start demo")
env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(stream_execution_environment=env)

ContainError = udf(ContainsErrorCl(), [DataTypes.STRING()], result_type=DataTypes.FLOAT())
t_env.create_temporary_function("ContainError", ContainError)

# write all the data to one file
t_env.get_config().get_configuration().set_string("pipeline.jars", "file:///opt/flink_job/pravega-connectors-flink-1.12_2.12-0.10.0.jar")

t_env.set_python_requirements(
    requirements_file_path="/opt/flink_job/requirements.txt",
    requirements_cache_dir="/opt/cached")

URI = "tcp://pravega:9090"

def create_table():
    return f"""CREATE TABLE source_table (
    task_id INTEGER,
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

print(create_table())
t_env.execute_sql(create_table())


filter_sql = """SELECT task_id, task_hash, log_type, ContainError(message), message
  FROM source_table
 GROUP BY task_id, task_hash, message, log_type, TUMBLE(event_time, INTERVAL '10' SECOND) HAVING ContainError(message) > 0.6
"""

results = t_env.sql_query(filter_sql)

ds = t_env.to_append_stream(
    results, Types.ROW_NAMED(
        ["task_id", "task_hash", "log_type", 'rate', 'message'],
        [ Types.INT(), Types.LONG(), Types.STRING(), Types.FLOAT(), Types.STRING()]))

output_path ='/tmp/DemoOut'
file_sink = StreamingFileSink.for_row_format(output_path, SimpleStringEncoder()).build()
ds.add_sink(file_sink)

env.execute('Flink-Demo')
