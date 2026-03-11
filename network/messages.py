import struct
import msgpack

def encode_message(msg_dict: dict) -> bytes:
    payload = msgpack.packb(msg_dict, use_bin_type=True)
    length = len(payload)
    header = struct.pack(">I", length)
    return header + payload

async def decode_message(reader) -> dict:
    header = await reader.readexactly(4)
    length = struct.unpack(">I", header)[0]
    payload = await reader.readexactly(length)
    return msgpack.unpackb(payload, raw=False)
