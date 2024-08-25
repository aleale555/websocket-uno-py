from player import Player
from game import GameController
import asyncio
from websockets.server import serve

#(Player) is called extension
class WebsocketPlayer(Player): 
    def __init__(self, name: str, client):
        super().__init__(name)
        self.client = client
    async def announce(self, message):
        #async for waiting/await
            await self.client.send(message)

class WebsocketServer:
    def __init__(self, player_count):
        self.players = []
        self.game = None
        self.player_count = player_count
    async def announce_all(self, message):
        for p in self.players:
            await p.announce(message)
    async def run(self, websocket): ##REPRESENTS A SINGLE CONNECTION TO THE SERVER
        player = None
        async for message in websocket:
            if player is None:
                player = WebsocketPlayer(message, websocket)
                player_count = len(self.players)
                if (len(self.players) == 0):
                    await player.announce("You're the first to join!")
                else:
                    await player.announce(
                        f"You're joining a game with {', '.join(map(str, self.players))}")
                await self.announce_all(f'{player} joined the game!')
                self.players.append(player)
                if player_count + 1 == self.player_count:
                    await self.announce_all(f'The room is filled!')
                    await self.announce_all('The game has started.')
                    self.game = GameController(self.players)
                    await self.game.start_game()
            elif self.game is not None:
                await self.game.on_player_input(player, message)
                
async def main():
    print('Running!')
    server = WebsocketServer(2)
    async with serve(server.run, "localhost", 8765):
        await asyncio.Future()  # run forever
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit()
