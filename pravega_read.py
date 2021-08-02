import asyncio
import pravega_client


async def main():
    # assuming Pravega controller is listening at 127.0.0.1:9090
    stream_manager = pravega_client.StreamManager("localhost:9090", False, False)

    reader_group = stream_manager.create_reader_group("re", "demo", "myStream")

    reader = reader_group.create_reader("sss");

    # acquire a segment slice to read
    slice = await reader.get_segment_slice_async()
    for event in slice:
        print(event.data())

    # after calling release segment, data in this segment slice will not be read again by
    # readers in the same reader group.
    reader.release_segment(slice)

    # remember to mark the finished reader as offline.
    reader.reader_offline()

asyncio.run(main())