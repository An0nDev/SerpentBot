# SerpentBot

Minecraft chatbot + Discord bot for the Serpent guild.

Uses Python modules:
- requests: https://github.com/psf/requests/ (HTTP client, for easy use of Mojang's Yggdrasil auth system)
- varint (modified, not through pip/PyPI): https://github.com/fmoo/python-varint (for encoding + decoding VarInts, a staple in the Minecraft protocol)

Anything else (Minecraft client, etc) is from scratch with https://wiki.vg as a heavy reference.

To start the client, you need a file called `credentials.json` with the contents following this format:

```json
{
    "username": "foo@gmail.com",
    "password": "secure123"
}
```

The file will be populated with other necessary authentication data (client + access token) on first run. After the first run, the username and password can be removed, but may be needed again in the future in case the access token becomes invalid.

After installing dependencies, just run `python3 main.py` from the root directory. (W probably work with 3.x but untested on <3.8.5)
