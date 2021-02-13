from .MinecraftClient.MinecraftClient import MinecraftClient

class SerpentBot:
    def __init__ (self):
        print ("bruh starting serpent bot")
        self.minecraft_client = MinecraftClient (ip = "mc.hypixel.net")
