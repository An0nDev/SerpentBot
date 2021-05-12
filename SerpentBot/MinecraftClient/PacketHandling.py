from .DataTypes.VarInt import VarInt
import io
import zlib

class PacketHandling:
    @staticmethod
    def read_one_packet (client, *, compressed):
        if compressed:
            packet_length, packet_length_length = VarInt.decode (client)
            data_length, data_length_length = VarInt.decode (client)
            print (f"length of data length + compressed length of (packet ID + data): {packet_length}, length of uncompressed packet ID + data: {data_length}, compressed length of (packet ID + data): {packet_length - data_length_length}")
            if data_length == 0: # Packet is uncompressed
                print ("Compression enabled but data length is 0 so receiving uncompressed packet")
                packet_id, packet_id_length = VarInt.decode (client)
                packet_data = client.recv (packet_length - data_length_length - packet_id_length)
                print (f"Received uncompressed packet with length {len (packet_data)}")
            else: # Packet is compressed
                print ("Compression enabled and data length is non-zero")
                compressed_packet_id_and_data = client.recv (packet_length - data_length_length)
                print (f"Received {packet_length - data_length_length} bytes of compressed data")
                packet_id_and_data = zlib.decompress (compressed_packet_id_and_data)
                assert len (packet_id_and_data) == data_length, f"Decompressed packet size {len (packet_id_and_data)} is different than reported size {data_length}"
                print (f"Used zlib to decompress into {len (packet_id_and_data)} bytes of data")
                packet_id_buffer = io.BytesIO (packet_id_and_data)
                packet_id_buffer.recv = packet_id_buffer.read
                packet_id, packet_id_length = VarInt.decode (packet_id_buffer)
                print (f"Read packet ID {packet_id} (ID length {packet_id_length}), now have {len (packet_id_and_data) - packet_id_length} bytes of packet data")
                packet_data = packet_id_and_data [packet_id_length:]
        else:
            packet_length, packet_length_length = VarInt.decode (client)
            packet_id, packet_id_length = VarInt.decode (client)
            packet_data = client.recv (packet_length - packet_id_length)
        print (f"Received packet with ID {packet_id} and length {len (packet_data)} (compressed {compressed})")
        return packet_id, packet_data
    @staticmethod
    def decode_fields (packet, field_spec):
        fields = {}
        offset = 0
        this_uses_last_as_length = False
        last_length = None
        for field_info in field_spec:
            field_name = field_info [0]
            field_type = field_info [1]
            field_data_buffer = io.BytesIO (packet [offset:])
            field_data_buffer.recv = field_data_buffer.read
            decode_args = [field_data_buffer]
            if this_uses_last_as_length:
                decode_args.append (last_length)
                this_uses_last_as_length = False
                last_length = None
            field_data, field_length = field_type.decode (*decode_args)
            fields [field_name] = field_data
            next_uses_this_length = len (field_info) > 2 and field_info [2]
            offset += field_length
            if offset == len (packet): break
            if next_uses_this_length:
                this_uses_last_as_length = True
                last_length = field_data
        return fields
    @staticmethod
    def receive_specific_packet (client, *, packet_id, field_spec, compressed = False):
        incoming_packet_id, incoming_packet_data = PacketHandling.read_one_packet (client, compressed = compressed)
        assert incoming_packet_id == packet_id, f"Received wrong packet! Want {packet_id}, have {incoming_packet_id} (repr {PacketHandling.repr_packet (incoming_packet_data)})"
        return PacketHandling.decode_fields (incoming_packet_data, field_spec)
    @staticmethod
    def make_packet (*, packet_id, fields, compressed = False):
        packet_data = b""
        for field in fields: packet_data += field
        packed_packet_id = VarInt.encode (packet_id)
        packed_packet_length = VarInt.encode (len (packed_packet_id) + len (packet_data))
        return packed_packet_length + packed_packet_id + packet_data
    @staticmethod
    def repr_packet (packet):
        return " ".join (bin (_byte) for _byte in packet)
