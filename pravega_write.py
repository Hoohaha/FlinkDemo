import json
import pravega_client
# assuming Pravega controller is listening at 127.0.0.1:9090
stream_manager = pravega_client.StreamManager("localhost:9090", False, False)

print("create scope")
scope_result = stream_manager.create_scope("demo")

print(scope_result)
stream_result = stream_manager.create_stream("demo", "myStream", 1) # initially stream contains 1 segment

print(stream_result)

print("create scope")
writer = stream_manager.create_writer("demo","myStream")
message = {
    "msg": "123123",
    "level": "INFO"
}
m = json.dumps(message)
print("start write: %s" % m)
writer.write_event(m)
