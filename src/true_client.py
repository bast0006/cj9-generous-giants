import asyncio
import threading
import time
import traceback
# import sys
from collections import deque

import pygame
import websockets

import game
from character import Character
from maps import MapGen, MapSprite

black = (0, 0, 0)
white = (255, 255, 255)
grey = (155, 155, 155)

options_dict = {
    1: "See rooms",
    2: "Create Room",
    3: "Help",
    4: "Leave Room",
    5: "Leave game",
    6: "Exit Game",
}


class Player:
    """Handle asynchronous player creation, input and communication with server"""

    def __init__(self):
        self.game = None
        self.name = "Missing"
        # self.websocket = websocket
        self._pid_ = None
        self.rid = "0"
        self.running = True
        self.game_rect = None
        self.texts = deque()
        self.text_buffer = []
        self.shift_active = False
        self.menu_rects = []
        self.updated_rects = []
        self.font = pygame.font.SysFont('Arial', 16)
        self.text_edi_rect = None
        self.comm_text = None
        self.in_game = False
        self.character = None

        # Init chat tracking

        self.chat_w_start = 900
        self.chat_h_start = 450

    def attach(self, game: game.Game):
        """Attach this client to a game instance."""
        self.game = game
        self.screen = game.screen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        self.texts = deque(self.texts, maxlen=(self.height - self.chat_h_start - 80)//20)
        self.make_screen()

    def make_screen(self):
        """Set up the initial ui."""
        self.screen.fill((255, 255, 255))
        player.game_panel()
        player.menu_panel()
        player.chat_panel()
        pygame.display.update()

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

    def game_panel(self):
        """Draw the main game panel border."""
        self.game_rect = pygame.draw.rect(self.screen, black, [0, 0, 895, self.height], width=5)

    def menu_panel(self):
        """Draw the menu panel."""
        menu_w_start = 1050
        for i, j in zip(range(20, 260, 35), options_dict.values()):
            text = self.font.render(j, True, black)
            rect = pygame.draw.rect(self.screen, black, rect=pygame.Rect((menu_w_start, i, 110, 30)), width=1)
            self.screen.blit(text, (menu_w_start + 10, i + 5))
            self.menu_rects.append((rect, j))

    def chat_panel(self):
        """Draw the chat panel and messages."""
        self.server_rects = []
        self.chat_bars = []

        text = self.font.render("Server messages", True, black)

        self.screen.fill(white, (self.chat_w_start+5, 235, self.width, self.height))

        chat_rect = pygame.Rect((self.chat_w_start,
                                 self.chat_h_start,
                                 self.width-(self.chat_w_start+10),
                                 self.height-(self.chat_h_start+10)))

        pygame.draw.rect(self.screen, black, rect=chat_rect, width=2)

        self.screen.blit(text, (self.chat_w_start+5, 235))

        for i in range(260, self.chat_h_start - 60, 20):
            self.server_rects.append(pygame.Rect((self.chat_w_start+5, i, self.width-(self.chat_w_start+18), 20)))

        text = self.font.render(f"Chat room (You are {self.name})", True, black)
        self.screen.blit(text, (self.chat_w_start+5, self.chat_h_start-20))

        self.text_edi_rect = pygame.Rect(self.chat_w_start+1, self.chat_h_start+1, 289, 30)
        pygame.draw.rect(self.screen, black, self.text_edi_rect, width=1)

        for i in range(self.chat_h_start + 40, self.height - 40, 20):
            self.chat_bars.append(pygame.Rect((self.chat_w_start+5, i, self.width-(self.chat_w_start+18), 20)))

        for rect in self.server_rects:
            pygame.draw.rect(self.screen, black, rect, width=1)

        for rect in self.chat_bars:
            pygame.draw.rect(self.screen, black, rect, width=1)

    def print_buffer(self):
        """Turn the text buffer into manipulable text."""
        temp_buffer = []
        shift_on = False
        counter = 0
        for i in self.text_buffer:
            if i.endswith("start"):
                shift_on = True
                continue
            elif i.endswith("end"):
                shift_on = False
                continue
            elif i == "back":
                temp_buffer.pop()
                continue

            counter += len(i)
            if counter > 20:
                temp_buffer.append("\n")
                counter = 0

            if shift_on:
                temp_buffer.append(i.upper())
            else:
                temp_buffer.append(i)

        return "".join(temp_buffer)

    def handle_command(self):
        """Process a command that starts with /."""
        command = self.comm_text

        if command.startswith("/nick"):
            self.name = command.removeprefix("/nick")
            # Re-render chat panel
            self.chat_panel()
        elif command.startswith("/list"):
            self.comm_text = "List Players"
        elif command.startswith("/start"):
            print("Starting game")
            self.in_game = True

            width = 895//16
            height = self.height // 16 - 1
            mapGenerator = MapGen((width, height))
            mapGenerator.generate_noise()
            self.seed = mapGenerator.seed
            mapGenerator.convert()
            map = MapSprite(x=5, y=5)
            map.register_from_string(mapGenerator.export_to_string())
            self.game.add_sprite(-3, map)
            self.comm_text = "Start Game"
            self.character = Character(
                spawn_position=(50 * self.pid, 50)
            )
            self.game.add_sprite(3, self.character)
            self.game.add_handler(self.character.input, pygame.KEYUP, pygame.KEYDOWN)

        elif command.startswith("/join"):
            self.comm_text = "Join Room"
            self.rid = command.removeprefix("/join")

    def start_game_client(self, seed: str):
        """Start the game and draw all players in."""
        print("Starting game")
        self.in_game = True

        width = 895 // 16
        height = self.height // 16 - 1
        mapGenerator = MapGen((width, height), seed=int(seed))
        mapGenerator.generate_noise()
        mapGenerator.convert()
        map = MapSprite(x=5, y=5)
        map.register_from_string(mapGenerator.export_to_string())
        self.game.add_sprite(-3, map)
        self.character = Character(
            spawn_position=(50, 50)
        )
        self.game.add_sprite(3, self.character)
        self.game.add_handler(self.character.input, pygame.KEYUP, pygame.KEYDOWN)

    def frame_ui(self, screen: pygame.Surface) -> list[pygame.Rect]:
        """Renders the ui that's updated each frame."""
        for rect, text in zip(self.server_rects, self.server_rects):
            # pygame.draw.rect(self.screen, white, rect)
            pygame.draw.rect(screen, black, rect, width=1)
            self.updated_rects.append(rect)
            # text = self.font.render(str(text), True, black)
            # self.screen.blit(text, (rect.x + 2, rect.y))

        for rect, text in zip(self.chat_bars, reversed(self.texts)):
            pygame.draw.rect(screen, white, rect)
            pygame.draw.rect(screen, black, rect, width=1)
            text = self.font.render(str(text), True, black)
            text_updated = screen.blit(text, (rect.x + 2, rect.y))
            self.updated_rects.append(rect)
            self.updated_rects.append(text_updated)

        new_rects = self.updated_rects
        self.updated_rects = [self.screen.get_rect()]
        return new_rects

    def update(self, screen: pygame.Surface, dt: float) -> list[pygame.Rect]:
        """Called each frame by the Game."""
        return self.frame_ui(screen)

    def on_event(self, event):
        """Handle incoming window events."""
        print("EVT", event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect, text in self.menu_rects:
                if rect.collidepoint(event.pos):
                    self.comm_text = text

            if self.text_edi_rect.collidepoint(event.pos):
                self.shift_active = True
                pygame.draw.rect(self.screen, grey, rect=self.text_edi_rect)

        if self.shift_active and not self.in_game:
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                    self.text_buffer.append(pygame.key.name(event.key) + "end")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.shift_active = False
                    self.comm_text = self.print_buffer()
                    if self.comm_text.startswith("/"):
                        self.handle_command()
                    self.text_buffer.clear()

                elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                    self.text_buffer.append(pygame.key.name(event.key) + "start")
                elif event.key == pygame.K_BACKSPACE:
                    self.text_buffer.append('back')
                elif event.key == pygame.K_SPACE:
                    self.text_buffer.append(" ")
                else:
                    self.text_buffer.append(pygame.key.name(event.key))

            if self.shift_active:
                pygame.draw.rect(self.screen, grey, rect=self.text_edi_rect)
            else:
                pygame.draw.rect(self.screen, white, rect=self.text_edi_rect)
            pygame.draw.rect(self.screen, black, self.text_edi_rect, width=1)
            text = self.font.render(self.print_buffer()[-40:], True, black)
            self.screen.blit(text, (self.text_edi_rect.x + 5, self.text_edi_rect.y + 2))
            self.updated_rects.append(self.screen.get_rect())

    async def estab_comms(self):
        """Establish asynchronous communication with server, handle game loop"""
        async with websockets.connect(uri='ws://localhost:8001') as websocket:
            while self.running:
                try:
                    if self.pid is None:
                        await websocket.send('Get ID')      # first message to server like a pseudo-handshake
                        received_message = await websocket.recv()
                        print(received_message)
                        pid = int(received_message.split("###")[-1])
                        self.pid = pid

                    else:
                        special_commands = ["Join Room", "List Players"]
                        if self.comm_text is None:
                            continue

                        if self.comm_text in options_dict.values() \
                                or self.comm_text in special_commands:
                            if self.comm_text == "Exit Game":
                                self.running = False
                                self.game.running = False
                                await websocket.send(f"PID###{self.pid}: {self.name}: {self.comm_text}")
                                raise KeyboardInterrupt()
                            await websocket.send(f"{self.comm_text}")
                        else:
                            await websocket.send(f"PID###{self.pid}: {self.name}: {self.comm_text}")

                        self.comm_text = None
                        while self.running:
                            # Handle when server wants a response from us
                            try:
                                received_message = await asyncio.wait_for(websocket.recv(), 0.5)
                            except asyncio.TimeoutError:
                                break

                            match received_message:
                                case 'Enter Player ID':
                                    print("Replying with player ID:", self.pid)
                                    await websocket.send(str(self.pid))

                                case 'Enter Room ID':
                                    print("Replying with room ID:", str(self.rid))
                                    await websocket.send(str(self.rid))

                                case 'Enter World Seed':
                                    await websocket.send(str(self.seed))
                                case 'Start Game':
                                    seed = await websocket.recv()
                                    self.start_game_client(seed)
                                case 'Tell Nick':
                                    await websocket.send(self.name)
                                case _:
                                    self.texts += received_message.split("\n")
                                    break

                except Exception as _e:  # noqa: F841
                    # handle abrupt termination as well 'Leave game' option

                    await websocket.send(options_dict[5])
                    received_message = await websocket.recv()
                    self.texts.append(received_message)

                    await websocket.send(str(self.pid))
                    # print('Player ID sent')
                    received_message = await websocket.recv()
                    # self.texts.append(received_message)

                    self.texts.append('Bye, Game closed')
                    pygame.quit()
                    break


async def main():
    """Main asyncio function to start connection"""
    await player.estab_comms()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    ws_thread = threading.Thread(target=loop.run_forever)
    game = game.Game()
    player = Player()

    try:
        ws_thread.start()
        asyncio.run_coroutine_threadsafe(main(), loop)

        print("Connecting...")
        while player.pid is None:
            time.sleep(0.25)
        print("Starting client")

        player.attach(game)
        game.add_sprite(-1, player)
        game.add_handler(player.on_event, pygame.KEYUP, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)

        game.start()
    except KeyboardInterrupt:
        player.running = False
        game.running = False
        loop.call_soon_threadsafe(loop.stop)
        ws_thread.join(1)
        if ws_thread.is_alive():
            exit(2)
        exit(0)
    except Exception as _e:  # noqa: F841
        print("Out:", traceback.format_exc())
        player.running = False
        game.running = False
        loop.call_soon_threadsafe(loop.stop)
        ws_thread.join(1)
        if ws_thread.is_alive():
            exit(2)
        exit(1)
