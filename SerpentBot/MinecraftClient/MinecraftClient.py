import cryptography.hazmat.primitives.serialization
import cryptography.hazmat.primitives.asymmetric.padding
import socket
import struct
import secrets
from .PacketHandling import PacketHandling
from .Yggdrasil import Yggdrasil
from .DataTypes.VarInt import VarInt
from .DataTypes.String import String
from .DataTypes.Generics import Generics
from .DataTypes.ByteArray import ByteArray
from .EncryptedSocket import EncryptedSocket
import zlib
import traceback

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
        server_key = cryptography.hazmat.primitives.serialization.load_der_public_key (encryption_request_packet ["Public Key"])
        shared_secret = secrets.token_bytes (16) # "generate a random 16-byte secret"
        padding_method = cryptography.hazmat.primitives.asymmetric.padding.PKCS1v15 () # "with the server's public key (PKCS#1 v1.5 padded)"
        encrypted_secret = server_key.encrypt (shared_secret,
            padding = padding_method
        ) # "encrypts it with the server's public key"
        encrypted_verify_token = server_key.encrypt (
            encryption_request_packet ["Verify Token"],
            padding = padding_method
        ) # "encrypts the verify token... in the same way"
        Yggdrasil.join_session (credential_file,
            server_id_string = encryption_request_packet ["Server ID"],
            shared_secret = shared_secret,
            server_public_key = encryption_request_packet ["Public Key"]
        )
        self.network_socket.send (PacketHandling.make_packet (
            packet_id = 0x01, fields = [
            VarInt.encode (len (encrypted_secret)), # Length of Shared Secret.
            ByteArray.encode (encrypted_secret), # Shared Secret value, encrypted with the server's public key.
            VarInt.encode (len (encrypted_verify_token)), # Length of Verify Token.
            ByteArray.encode (encrypted_verify_token) # Verify Token value, encrypted with the same public key as the shared secret.
        ])) # Login: Encryption Response
        self.encrypted_network_socket = EncryptedSocket (self.network_socket, iv = shared_secret, key = shared_secret)
        print ("Enabled two way encryption on network socket")
        set_compression_packet = PacketHandling.receive_specific_packet (self.encrypted_network_socket,
            packet_id = 0x03, field_spec = [
            ("Threshold", VarInt) # Maximum size of a packet before it is compressed.
        ])
        print (f"Received set compression packet with threshold {set_compression_packet ['Threshold']}")
        while True:
            packet_id, packet_data = PacketHandling.read_one_packet (self.encrypted_network_socket, compressed = True)
