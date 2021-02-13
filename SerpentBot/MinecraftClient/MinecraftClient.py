import socket
from .PacketHandling import PacketHandling
from .Yggdrasil import Yggdrasil
from .DataTypes.VarInt import VarInt
from .DataTypes.String import String
from .DataTypes.Generics import Generics
from .DataTypes.ByteArray import ByteArray
import struct

class MinecraftClient:
    protocol_number = 754
    def __init__ (self, *, ip, ipv6 = False, port = 25565, packet_handler = None, credential_file = "credentials.json"):
        access_token = Yggdrasil.prepare (credential_file)
        self.network_socket = socket.socket (family = socket.AF_INET6 if ipv6 else socket.AF_INET)
        self.network_socket.connect ((ip, port))
        # login sequence
        self.network_socket.send (PacketHandling.make_packet (
            packet_id = 0x00, fields = [
            VarInt.encode (self.protocol_number), # Protocol version
            String.encode ("localhost"), # Server address
            Generics.UShort.encode (25565), # Server port
            VarInt.encode (0x02) # Next state (1 for status, 2 for login)
        ])) # Handshaking: Handshake
        self.network_socket.send (PacketHandling.make_packet (
            packet_id = 0x00, fields = [
            String.encode ("Dabberoni69420") # Name
        ])) # Login: Login Start
        encryption_request_packet = PacketHandling.receive_specific_packet (self.network_socket,
            packet_id = 0x01, field_spec = [
            ("Server ID", String), # Appears to be empty.
            ("Public Key Length", VarInt, True), # Length of Public Key (is length for next = True)
            ("Public Key", ByteArray),
            ("Verify Token Length", VarInt, True), # Length of Verify Token. Always 4 for Notchian servers. (is length for next = True)
            ("Verify Token", ByteArray)
        ])
        print (f"fields in encryption request packet: {encryption_request_packet}")
        while True:
            packet_id, packet_data = PacketHandling.read_one_packet (self.network_socket)
