import struct

class Generics:
    class Generic:
        @classmethod
        def encode (self, orig): return struct.pack (self._format, orig)
        @classmethod
        def decode (self, stream): return struct.unpack (self._format, stream.recv (struct.calcsize (self._format)))
    class UShort (Generic):  _format = "!H"
    class Long (Generic):    _format = "!q"
    class UUID (Generic):    _format = "!qq"
    class Boolean (Generic): _format = "?"
