import asyncio
import traceback

import websockets


class GameRoom:
    """Class for maintaining game rooms"""

    def __init__(self, rid, max_size):
        self.rid = rid              # room id
        self.room_players = {}      # (key-> player_id: int, value-> player_name: str)
        self._room_size_ = 0
        self.max_room_size = max_size

    @property
    def room_size(self):
        """Getter for room size"""
        return self._room_size_

    @room_size.setter
    def room_size(self, value):
        """Setter for room size"""
        if self.room_size == self.max_room_size:
            raise Exception(f'Room {self.rid} is full. Find another room')

        elif value < 0:
            raise Exception(f'Room {self.rid} is empty')

        else:
            self._room_size_ = value

    def add_player_to_room(self, player_id: int):
        """Add player to room"""
        key = self.room_players.get(player_id, None)
        # can be used a bug in case player already exists to overwite existing player

        if key is None:
            try:
                self.room_players[player_id] = f'Player {player_id}'    # just assign string to the player_id
                self.room_size += 1
                print(f'Player {player_id} added to room {self.rid}')
                return f"You're in room {self.rid}"

            except Exception as e_mess:
                print("Error joining:", e_mess)
                return e_mess
        else:
            return "Player already exists"

    def remove_player_from_room(self, player_id):
        """Remove player from room"""
        rid = self.room_players.get(player_id, None)
        if rid is not None:
            try:
                self.room_players.pop(player_id)
                self.room_size -= 1
                return "Bye bye"

            except Exception as e_mess:
                print(e_mess)
                return e_mess
        else:
            return "Player not found"

    def __str__(self):
        return f'Room {self.rid} | Current Size - {self.room_size}'


class GameManager:
    """Main websocket server to handle players and requests"""

    def __init__(self):
        self.players = {}       # (key-> player_id: int, value-> room_id: int)
        self.game = None
        self.max_room_size = 4
        self.rooms = {}         # (key-> room_id: int, value-> room: GameRoom)
        self.player_count = 0
        self.room_count = 0     # active room count
        self.room_seeds = {}

    def create_room(self, pid: int):
        """Create room"""
        rid = self.room_count
        room = GameRoom(rid, self.max_room_size)

        existing_rid, ws = self.players.get(pid, (-1, None))
        # if player is not assigned to any room, existing_rid is None

        if existing_rid is None:
            room.add_player_to_room(pid)
            _, ws = self.players[pid]
            self.players[pid] = (rid, ws)
            self.rooms[rid] = room
            print(f'Server message: Room {rid} created')
            self.room_count += 1
            return f"Welcome to room {rid}"

        else:
            print(f'Server message: Player {pid} already in room {existing_rid}')
            return f"Already in room {existing_rid}. Please leave room before creating new room"

    async def join_room(self, rid: int, pid: int):
        """Join room"""
        existing_rid, _ = self.players.get(pid, (-1, None))
        # if player is not assigned to any room, existing_rid is None

        if existing_rid == -1:
            print(f'Server message: Player {pid} not found')
            return f"Player {pid} not found"

        elif existing_rid is not None:
            print(f'Server message: Player {pid} already in room {existing_rid}')
            return f"Player {pid} already in room {rid}"

        room = self.rooms.get(rid, None)
        # if room does not exist, room is None

        if room is None:
            print(f'Server message: Room {rid} not found')
            return f'Room {rid} does not exist'

        else:
            room.add_player_to_room(pid)
            _, ws = self.players[pid]
            self.players[pid] = (rid, ws)
            message = f'Player {pid} joined room {rid}'
            await self.broadcast_messages(rid, message)
            print(f'Server message: Player {pid} added to room {rid}')
            return f'Player {pid} added to room {rid}'

    async def send_messages_in_chat(self, pid, message: str):
        """Sends a message to the players in a given room."""
        rid, _ = self.players.get(pid, [-1, None])

        if rid == -1:
            print(f'Server message: Player {pid} not found')
            return f"Player {pid} not found"
        elif rid is None:
            if message.lstrip().startswith("/"):
                # / means command, so we ignore it
                return
            print(f'Server message: Player {pid} not in room')
            return f"Player {pid} not in room"
        else:
            await self.broadcast_messages(rid, message)

    async def broadcast_messages(self, rid: int, message: str):
        """Broadcast messages to all players in room"""
        room = self.rooms.get(rid, None)
        # if room does not exist, room is None

        if room is not None:
            all_players = room.room_players.keys()
            for player_id in all_players:
                _, comm_socket = self.players[player_id]
                await comm_socket.send(message)

        else:
            print(f'Server message: Room {rid} not found')
            return f'Room {rid} not found'

    async def leave_room(self, pid: int):
        """Leave room"""
        rid, _ws = self.players.get(pid, [None, None])
        # if player is not assigned to any room, rid is None

        if rid is None:
            print('Server message: Player not in any room')
            return 'Player not in any room'

        else:
            room = self.rooms[rid]
            room.remove_player_from_room(pid)
            message = f'Player {pid} left room {rid}'
            # self.send_messages_in_chat(pid, message)
            await self.broadcast_messages(rid, message)
            _, ws = self.players[pid]
            self.players[pid] = (None, ws)       # reset (key: player_id, value: room_id) mapping

            if room.room_size == 0:
                # delete room if empty
                self.rooms.pop(rid)
                print(f'Server message: Room {rid} deleted')
                del room

            print(f'Server message: Player {pid} out of room {rid}')
            return f'Player {pid} out of room {rid}'

    def add_player(self, websocket: websockets.WebSocketServerProtocol):
        """Add player to game. Assign a new player id"""
        self.players[self.player_count] = (None, websocket)
        # current None assigned to player_id in dictionary indicating no room assigned

        self.player_count += 1
        print(f'Server message: Player {self.player_count} added')
        return f"PID###{self.player_count - 1}"

    async def remove_player(self, player_id: int):
        """Remove player from game"""
        response = await self.leave_room(player_id)   # response for debugging
        print(response)
        rid, _ = self.players.get(player_id, (-1, None))
        # if player doesn't exist, rid will be -1
        # rid is None if player exists without any room

        if rid is None:
            self.players.pop(player_id)
            print(f'Server message: Player {player_id} removed')
            return f"Player {player_id} removed"

        else:
            print(f'Server message: Player {player_id} not found')
            return "Player not found"

    def get_player(self, player_id: int):
        """Get player class. Created for future use when player class is used"""
        return self.players.get(player_id, None)

    def see_all_rooms(self):
        """Print existing rooms"""
        print('Server message: All rooms displayed')
        if not len(self.rooms):
            return "No rooms found"

        else:
            room_info_list = [f"Room {rid}: Space Available - "
                              + f"{self.rooms[rid].max_room_size - self.rooms[rid].room_size}"
                              for rid in self.rooms.keys()]

            return "<" + " >\n<".join(room_info_list) + " >"

    async def start_game(self, websocket):
        """Receive websocket connection from player. Player creation and game start"""
        pid = None
        while True:
            try:
                message = await websocket.recv()    # first message will be 'Get ID'
                if message != 'MoveTo':  # No spam my logs please
                    print(f'Received: {message}')

                match message:
                    case 'Get ID':
                        # assign new player id
                        output = self.add_player(websocket)
                        pid = int(output.split("###")[-1])
                        await websocket.send(output)

                    case 'See rooms':
                        output = self.see_all_rooms()
                        await websocket.send(output)

                    case 'Create Room':
                        await websocket.send('Enter Player ID')
                        pid = await websocket.recv()
                        output = self.create_room(int(pid))
                        await websocket.send(output)

                    case 'Join Room':
                        await websocket.send('Enter Room ID')
                        rid = await websocket.recv()
                        await websocket.send('Enter Player ID')
                        pid = await websocket.recv()
                        try:
                            rid = int(rid)
                        except ValueError:
                            await websocket.send(f"Bad room id: {rid}")
                            continue
                        output = await self.join_room(rid, int(pid))
                        await websocket.send(output)
                        if rid in self.room_seeds:
                            await websocket.send("Start Game")
                            await websocket.send(self.room_seeds[rid])
                    case 'Leave Room':
                        await websocket.send('Enter Player ID')
                        pid = await websocket.recv()
                        output = await self.leave_room(int(pid))
                        await websocket.send(output)

                    case 'Leave Game':
                        await websocket.send('Enter Player ID')
                        pid = await websocket.recv()
                        output = await self.remove_player(int(pid))
                        await websocket.send(output)
                        raise Exception(f'Game over for player {pid}')
                    case 'Help':
                        await websocket.send('Use /nick [name], /join [room], and /start!')
                    case 'Start Game':
                        await websocket.send('Enter Room ID')
                        rid = await websocket.recv()
                        await websocket.send('Enter World Seed')
                        seed = await websocket.recv()
                        self.room_seeds[int(rid)] = seed
                        print("Starting game with room seed of", seed)
                        await self.broadcast_messages(int(rid), "Start Game")
                        await self.broadcast_messages(int(rid), seed)
                    case 'Change Seed':
                        seed = await websocket.recv()
                        await websocket.send('Enter Room ID')
                        rid = await websocket.recv()
                        self.room_seeds[int(rid)] = seed
                        await self.broadcast_messages(int(rid), "Change Seed")
                        print("Broadcasting seed change in room", rid, "to", seed)
                        await self.broadcast_messages(int(rid), seed)
                    case 'List Players':
                        await websocket.send('Enter Room ID')
                        rid = await websocket.recv()
                        await self.list_players(websocket, rid)
                    case 'List PlayersRaw':
                        await websocket.send('Enter Room ID')
                        rid = await websocket.recv()
                        await self.list_players_raw(websocket, rid)
                    case 'MoveTo':
                        target = await websocket.recv()
                        pid = target.split(",", maxsplit=1)[0]
                        await self.send_messages_in_chat(int(pid), message + ": " + target)
                    case 'Room Seed':
                        await websocket.send('Enter Room ID')
                        rid = await websocket.recv()
                        print("Giving in-progress joiner the room seed:", self.room_seeds[int(rid)])
                        await websocket.send(self.room_seeds[int(rid)])
                    case 'Play Sound':
                        sound = await websocket.recv()
                        await websocket.send('Enter Room ID')
                        rid = int(await websocket.recv())
                        await self.broadcast_messages(rid, 'Play Sound')
                        await self.broadcast_messages(rid, sound)
                    case _:
                        if message.startswith("/"):
                            if message.startswith("/nick"):
                                new_nick = message.removeprefix("/nick")
                                await websocket.send('Enter Player ID')
                                pid = int(await websocket.recv())
                                rid, _ws = self.players[pid]
                                if not rid:
                                    continue
                                print("New nick ", self.rooms[rid].room_players[pid], "to", new_nick)
                                self.rooms[rid].room_players[pid] = new_nick
                            continue
                        try:
                            info, remainder_message = message.split(":", maxsplit=1)
                        except ValueError:
                            print("Protocol communication exception, honeybadgering")
                            print("Message was:", message)
                            traceback.print_exc()
                            continue
                        pid = int(info.split("###")[-1])

                        output = await self.send_messages_in_chat(pid, remainder_message)
                        if output:
                            await websocket.send(output)
            except websockets.ConnectionClosed:
                if pid is not None:
                    output = await self.remove_player(int(pid))
                    # await websocket.send(output)
                break

            except Exception as _e_mess:  # noqa: F841
                print(traceback.format_exc())
                break

    async def list_players(self, websocket, rid: str):
        """Handle a player requesting a list of room members."""
        room = self.rooms.get(int(rid), None)
        # if room does not exist, room is None
        players = []
        if room is not None:
            players = room.room_players.values()
        await websocket.send("Players in room: " + ", ".join(players))

    async def list_players_raw(self, websocket, rid: str):
        """Handle a player requesting a list of room members."""
        room = self.rooms.get(int(rid), None)
        # if room does not exist, room is None
        players = []
        if room is not None:
            all_players = room.room_players.keys()
            for player_id in all_players:
                players.append((player_id, room.room_players[player_id]))
        await websocket.send("|".join(f"{p[0]},{p[1]}" for p in players))

    async def main(self):
        """Main asyncio function to start server"""
        async with websockets.serve(self.start_game, '', 8001, ping_interval=None, ping_timeout=None):
            print('Server started')
            await asyncio.Future()


if __name__ == "__main__":
    gm = GameManager()
    try:
        asyncio.run(gm.main())
    except KeyboardInterrupt:
        print('Server closed')
