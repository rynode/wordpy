import json
import asyncio
import websockets

from wordpy.constants import *

class Root():
    def __init__(self):
        self.websocket = None

        self.uri = URI

        self.nick = NICK
        self.password = PASSWORD
        self.channel = CHANNEL

    async def run(self):
        async for websocket in websockets.connect(self.uri):
            try:
                print("[info]", "[base]", "connection opened, dispatching . . .")
                self.websocket = websocket
                await self._on_connect()
                async for raw_message in self.websocket:
                    message = json.loads(raw_message)
                    if message["cmd"] == "chat": # and not message["nick"] == self.nick:
                        #print("[info", "[base]", " chat received")
                        await self.on_text(message["text"], message["nick"])
                    elif message["cmd"] == "info" and message.get("type") == "whisper" and message.get("from", None):
                        #print("[info", "[base]", " whisper received")
                        await self.on_whisper(message["text"], message["from"])
                    elif message["cmd"] == "onlineSet":
                        #print("[info", "[base]", " joined channel")
                        await self.on_login(message["nicks"])
                    elif message["cmd"] == "onlineAdd":
                        #print("[info", "[base]", " user joined")
                        await self.on_join(message["nick"])
                    elif message["cmd"] == "onlineRemove":
                        #print("[info", "[base]", " user left")
                        await self.on_leave(message["nick"])
                    elif message["cmd"] == "warn":
                        #print("[info", "[base]", " warning received")
                        await self.on_warn(message["text"])
                    elif message["cmd"] == "info":
                        #print("[info", "[base]", " information received")
                        await self.on_info(message["text"])
                    else:
                        print("[info", "[base]", " unhandled message received")
                        print(message) # for debugging purposes
            except BaseException as e:
                raise e

    async def _on_connect(self):
        #print("ON_CONNECT")
        await self.login()

    async def on_text(self, text, nick):
        #print("ON_TEXT")
        #print(text)
        #print(nick)
        pass

    async def on_whisper(self, text, nick):
        #print("ON_WHISPER")
        #print(text)
        #print(nick)
        pass

    async def on_login(self, nicks):
        #print("ON_LOGIN")
        #print(nicks)
        pass

    async def on_join(self, nick):
        #print("ON_JOIN")
        #print(nick)
        pass

    async def on_leave(self, nick):
        #print("ON_LEAVE")
        #print(nick)
        pass

    async def on_warn(self, text):
        #print("ON_WARN")
        #print(text)
        pass

    async def on_info(self, text):
        #print("ON_INFO")
        #print(text)
        pass

    async def login(self):
        await self._send_packet({
            "cmd": "join",
            "channel": self.channel,
            "password": self.password,
            "nick": self.nick})

    async def say(self, text):
        await self._send_packet({
            "cmd": "chat",
            "text": text})

    async def whisper(self, nick, text):
        await self._send_packet({
            "cmd": "whisper",
            "nick": nick,
            "text": text})

    async def kick(self, nick):
        await self._send_packet({
            "cmd": "kick",
            "nick": nick})

    async def move(self, new_channel):
        self.channel = new_channel
        await self._send_packet({
            "cmd": "move",
            "channel": new_channel})

    async def rename(self, new_nick):
        self.nick = new_nick
        await self._send_packet({
            "cmd": "changenick",
            "nick": new_nick})

    async def _send_packet(self, packet):
        encoded = json.dumps(packet)
        await self.websocket.send(encoded)
