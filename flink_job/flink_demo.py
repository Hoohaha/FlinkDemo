import pyflink
import os
from pyflink import version
print(version.__version__)

print(os.path.abspath(os.path.dirname(pyflink.__file__)))
if os.environ.get('https_proxy'):
    del os.environ['https_proxy']
if os.environ.get('http_proxy'):
    del os.environ['http_proxy']

from pyflink.common.typeinfo import Types
from pyflink.table.table_environment import StreamTableEnvironment
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table.window import Tumble
from pyflink.table.expressions import lit
from pyflink.table.udf import udf
from pyflink.table import ScalarFunction, DataTypes
from log_analyzer.analyzer import Analyzer


# option 1: extending the base class `ScalarFunction`
class Add(ScalarFunction):
  def eval(self, i, j):
    return i + j



class ContainsErrorCl(ScalarFunction):
    def __init__(self):
        self.analyzer = Analyzer()
    def eval(self, input):
        import logging
        if input is None:
            return False

        rate = self.analyzer.inspect_text(input).prob(True)
        print(rate)
        logging.info(rate)
        return rate

print("start demo")
env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(stream_execution_environment=env)

add = udf(Add(), result_type=DataTypes.BIGINT())
ContainError = udf(ContainsErrorCl(), [DataTypes.STRING()], result_type=DataTypes.FLOAT())

t_env.create_temporary_function("ContainError", ContainError)
t_env.create_temporary_function("add", add)

# write all the data to one file
t_env.get_config().get_configuration().set_string("pipeline.jars", "file:///opt/pravega-connectors-flink-1.11_2.12-0.9.1.jar")

t_env.set_python_requirements(
    requirements_file_path="/opt/flink_job/requirements.txt",
    requirements_cache_dir="/opt/flink_job/cached")

URI = "tcp://pravega:9090"

def create_table():
    return f"""CREATE TABLE source_table (
    level STRING,
    msg STRING,
    event_time TIMESTAMP(3),
    WATERMARK FOR event_time AS event_time - INTERVAL '10' SECONDS
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

filter_sql = """SELECT msg FROM source_table
WHERE add() > 0
GROUP BY
    msg,
    TUMBLE(event_time, INTERVAL '10' SECOND)
"""

results = t_env.sql_query(filter_sql)

t_env.to_append_stream(
    results, Types.ROW_NAMED(['msg'], [Types.STRING()])).print()
env.execute('Flink-Demo')
