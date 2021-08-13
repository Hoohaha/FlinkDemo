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
        message STRING
    )
    with (
        'connector' = 'jdbc',
        'url' = 'jdbc:mysql://mysql:3306/demo',
        'username' = 'test',
        'password' = '123456',
        'table-name' = 'keyErrorLog'
    )
"""
        # 'connector.write.flush.interval' = '5s',
        # 'connector.write.flush.max-rows' = '1'
#         # 'connector.driver' = 'com.mysql.cj.jdbc.Driver' ,
print(create_table())
t_env.execute_sql(create_table())
t_env.execute_sql(mysqlSink)

filter_sql = """SELECT task_id, task_hash, log_type, ContainError(message), message
  FROM source_table
 GROUP BY task_id, task_hash, message, log_type, TUMBLE(event_time, INTERVAL '10' SECOND) HAVING ContainError(message) > 0.7
"""

t_env.sql_query(filter_sql).execute_insert("mysqlsink").wait()

# ds = t_env.to_append_stream(
#     results, Types.ROW_NAMED(
#         ["task_id", "task_hash", "log_type", 'rate', 'message'],
#         [ Types.LONG(), Types.LONG(), Types.STRING(), Types.FLOAT(), Types.STRING()]))

# t_env.from_data_stream(ds).execute_insert("mysqlsink")
# table_result = table.execute_insert("my_sink")

# sink = t_env.from_path('mysqlsink')

# print(results)
# ds.add_sink()

# output_path ='/tmp/DemoOut'
# file_sink = StreamingFileSink.for_row_format(output_path, SimpleStringEncoder()).build()
# ds.add_sink(mysqlSink)

env.execute('Flink-Demo')
