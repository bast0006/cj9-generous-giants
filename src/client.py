import asyncio

import websockets

options_dict = {
    1: "See rooms",
    2: "Create Room",
    3: "Join Room",
    4: "Leave Room",
    5: "Leave game"
}


class Player:
    """Handle asynchronous player creation, input and communication with server"""

    def __init__(self):
        # self.name = None
        # self.websocket = websocket
        self._pid_ = None

    @property
    def pid(self):
        """Getter for player ID"""
        return self._pid_

    @pid.setter
    def pid(self, player_id):
        """Setter for player ID"""
        self._pid_ = player_id

    @staticmethod
    def print_options():
        """Print global options dictionary"""
        print("\n Options:")
        for key, value in options_dict.items():
            print(f"{key}: {value}")

    async def estab_comms(self):
        """Establish asynchronous communication with server, handle game loop"""
        async with websockets.connect(uri='ws://localhost:8001') as websocket:
            while True:
                try:
                    if self.pid is None:
                        await websocket.send('Get ID')      # first message to server like a pseudo-handshake
                        received_message = await websocket.recv()
                        print(received_message)
                        pid = int(received_message.split("###")[-1])
                        self.pid = pid

                    else:
                        Player.print_options()
                        choice = int(input("Select an option: "))

                        if choice == 5:
                            # Quit Game
                            raise KeyboardInterrupt

                        else:
                            await websocket.send(options_dict[choice])
                            # send selected option message to server

                            while True:
                                received_message = await websocket.recv()
                                match received_message:

                                    case 'Enter Player ID':
                                        await websocket.send(str(self.pid))

                                    case 'Enter Room ID':
                                        rid = input("Enter Room ID: ")
                                        await websocket.send(rid)

                                    case _:
                                        print(received_message)
                                        break

                    await asyncio.sleep(1)

                except KeyboardInterrupt:
                    # handle abrupt termination as well 'Leave game' option

                    await websocket.send(options_dict[5])
                    received_message = await websocket.recv()
                    print(received_message)

                    await websocket.send(str(self.pid))
                    print('Player ID sent')
                    received_message = await websocket.recv()
                    print(received_message)

                    print('\nBye, Game closed')
                    break


async def main():
    """Main asyncio function to start connection"""
    player = Player()
    await player.estab_comms()


if __name__ == "__main__":
    asyncio.run(main())
