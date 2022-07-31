<<<<<<< HEAD
import asyncio
from collections import deque

import pygame
import websockets

black = (0, 0, 0)
white = (255, 255, 255)

options_dict = {
    1: "See rooms",
    2: "Create room",
    3: "Join room",
    4: "Leave room",
    5: "Leave game"
}


class Player:
    """Handle asynchronous player creation, input and communication with server"""

    def __init__(self, width: int = 1200, height: int = 800):
        # self.name = None
        # self.websocket = websocket
        pygame.init()
        self._pid_ = None
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill((255, 255, 255))
        self.game_rect = None
        self.texts = deque()
        self.serv_texts = deque()
        self.text_buffer = []
        self.shift_active = False
        self.chat_bars = []
        self.menu_rects = []
        self.font = pygame.font.SysFont('Calibri', 16, bold=True)
        self.text_edi_rect = None
        self.comm_text = None
        self.server_rects = []

    @property
    def pid(self):
        """Getter for player ID"""
        return self._pid_

    @pid.setter
    def pid(self, player_id):
        """Setter for player ID"""
        self._pid_ = player_id

    def game_panel(self):
        """Draw game panel"""
        self.game_rect = pygame.draw.rect(self.screen, black, [0, 0, 895, self.height], width=5)

    def menu_panel(self):
        """Draw menu panel"""
        menu_w_start = 950
        for start_height, text in zip(range(20, 220, 40), options_dict.values()):
            rect = pygame.draw.rect(self.screen,
                                    (66, 155, 245),
                                    rect=pygame.Rect((menu_w_start, start_height, 150, 30)),
                                    width=5)
            text_d = self.font.render(text, True, black)
            self.screen.blit(text_d, (menu_w_start + 30, start_height + 5))
            self.menu_rects.append((rect, text))

    def chat_panel(self):
        """Draw chat panel"""
        chat_w_start = 900
        chat_h_start = 450

        # Server message panel
        text = self.font.render("Server messages", True, black)
        self.screen.blit(text, (chat_w_start+5, 235))

        self.serv_texts = deque(maxlen=(chat_h_start - 260 - 40)//20)
        for i in range(260, chat_h_start - 60, 20):
            self.server_rects.append(pygame.Rect((chat_w_start+5, i, self.width-(chat_w_start+18), 20)))

        for rect in self.server_rects:
            pygame.draw.rect(self.screen, black, rect, width=2, border_radius=3)

        # Player message rectangle
        chat_rect = pygame.Rect((chat_w_start,
                                 chat_h_start,
                                 self.width-(chat_w_start+10),
                                 self.height-(chat_h_start+10)))

        pygame.draw.rect(self.screen, black, rect=chat_rect, width=2)

        text = self.font.render("Chat room", True, black)
        self.screen.blit(text, (chat_w_start+5, chat_h_start-20))

        # Text input pane
        self.text_edi_rect = pygame.Rect(chat_w_start+1, chat_h_start+1, 289, 30)
        pygame.draw.rect(self.screen, (66, 155, 245), self.text_edi_rect, width=3)

        # Player message panel
        self.texts = deque(self.texts, maxlen=(self.height - chat_h_start - 60)//20)

        for i in range(chat_h_start + 40, self.height - 40, 20):
            self.chat_bars.append(pygame.Rect((chat_w_start+5, i, self.width-(chat_w_start+18), 20)))

        for rect in self.chat_bars:
            pygame.draw.rect(self.screen, black, rect, width=2, border_radius=3)

    def print_buffer(self, buffer=None):
        """Moderate and print text buffer"""
        temp_buffer = []
        shift_on = False
        counter = 0
        for i in (self.text_buffer if buffer is None else buffer):
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
            if i == "\n" or counter > 40:
                temp_buffer.append("\n")
                counter = 0
            elif i != "\n":
                if shift_on:
                    temp_buffer.append(i.upper())
                else:
                    temp_buffer.append(i)

        return "".join(temp_buffer)

    async def estab_comms(self):
        """Establish asynchronous communication with server, handle game loop"""
        self.game_panel()   # init game panel
        self.menu_panel()   # init menu panel
        self.chat_panel()   # init chat panel
        pygame.display.flip()

        counter = 0         # for custom cursor

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
                        flag = False
                        for rect, text in zip(self.server_rects, self.serv_texts):
                            # draw server message rectanges and print texts
                            pygame.draw.rect(self.screen, white, rect)
                            pygame.draw.rect(self.screen, black, rect, width=2, border_radius=3)
                            text = self.font.render(str(text), True, black)
                            self.screen.blit(text, (rect.x + 2, rect.y))

                        for rect, text in zip(self.chat_bars, self.texts):
                            # draw player message rectanges and print texts
                            pygame.draw.rect(self.screen, white, rect)
                            pygame.draw.rect(self.screen, black, rect, width=2, border_radius=3)
                            text = self.font.render(str(text), True, black)
                            self.screen.blit(text, (rect.x + 2, rect.y))

                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                # if mouse key is pressed
                                for rect, text in self.menu_rects:
                                    if rect.collidepoint(pygame.mouse.get_pos()):
                                        # if mouse is over option button/menu rectangles
                                        self.comm_text = text
                                        flag = True
                                        break

                                if self.text_edi_rect.collidepoint(pygame.mouse.get_pos()):
                                    # if mouse is over text input rectangle
                                    self.shift_active = True

                            if flag is False and self.shift_active:
                                if event.type == pygame.KEYUP:
                                    # for handling shift key capitalizaton
                                    if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                                        self.text_buffer.append(pygame.key.name(event.key) + "end")

                                if event.type == pygame.KEYDOWN:
                                    # look for key presses
                                    if event.key == pygame.K_RETURN:
                                        # to finish taking input
                                        self.shift_active = False       # end capitalization
                                        pygame.draw.rect(self.screen, white, rect=self.text_edi_rect)
                                        pygame.draw.rect(self.screen, (66, 155, 245), self.text_edi_rect, width=3)
                                        self.comm_text = self.print_buffer()    # this will be chat message
                                        self.text_buffer.clear()

                                    elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                                        # to figure out shift key start
                                        self.text_buffer.append(pygame.key.name(event.key) + "start")
                                    elif event.key == pygame.K_BACKSPACE:
                                        # to handle backspace
                                        self.text_buffer.append('back')
                                    elif event.key == pygame.K_SPACE:
                                        # to handle space
                                        self.text_buffer.append(" ")
                                    else:
                                        self.text_buffer.append(pygame.key.name(event.key))

                                pygame.draw.rect(self.screen, white, rect=self.text_edi_rect)
                                pygame.draw.rect(self.screen, (66, 155, 245), self.text_edi_rect, width=3)
                                text = self.font.render(self.print_buffer()[-39:] + ("|" if counter % 2 else ""),
                                                        True,
                                                        black)
                                # ("|" if counter % 2 else "") is for custom cursor to create blinking effect

                                self.screen.blit(text, (self.text_edi_rect.x + 5, self.text_edi_rect.y + 4))
                                counter += 1

                            if event.type == pygame.QUIT:
                                raise KeyboardInterrupt

                        pygame.display.update()

                        if self.comm_text is None:
                            continue

                        if self.comm_text == "Leave game":
                            raise KeyboardInterrupt

                        elif self.comm_text in options_dict.values():
                            await websocket.send(self.comm_text)

                        else:
                            await websocket.send(f"PID###{self.pid}: {self.comm_text}")

                        self.comm_text = None
                        while True:

                            received_message = await websocket.recv()
                            match received_message:
                                case 'Enter Player ID':
                                    await websocket.send(str(self.pid))
                                case _:
                                    if received_message.startswith("ServM:"):
                                        # separate server messages for server panel
                                        self.serv_texts.append(received_message.split("ServM:")[-1])
                                        maxlen = self.serv_texts.maxlen
                                        self.serv_texts = deque(
                                            self.print_buffer("\n".join(self.serv_texts)).split("\n"), maxlen=maxlen
                                        )
                                    elif received_message == "":
                                        pass
                                    else:
                                        # separate player messages for chat panel
                                        self.texts.append(received_message)
                                        maxlen = self.texts.maxlen
                                        self.texts = deque(
                                            self.print_buffer("\n".join(self.texts)).split("\n"), maxlen=maxlen
                                        )
                                    break

                            for rect, text in zip(self.server_rects, self.serv_texts):
                                # draw server message rectanges and print texts
                                pygame.draw.rect(self.screen, white, rect)
                                pygame.draw.rect(self.screen, black, rect, width=2, border_radius=3)
                                text = self.font.render(str(text), True, black)
                                self.screen.blit(text, (rect.x + 2, rect.y))

                            for rect, text in zip(self.chat_bars, self.texts):
                                # draw player message rectanges and print texts
                                pygame.draw.rect(self.screen, white, rect)
                                pygame.draw.rect(self.screen, black, rect, width=2, border_radius=3)
                                text = self.font.render(str(text), True, black)
                                self.screen.blit(text, (rect.x + 2, rect.y))

                except KeyboardInterrupt:
                    # handle abrupt termination as well 'Leave game' option

                    await websocket.send("Leave game")
                    _ = await websocket.recv()

                    await websocket.send(str(self.pid))
                    _ = await websocket.recv()

                    self.texts.append('Bye, Game closed')

                    # to display final messages
                    for rect, text in zip(self.chat_bars, self.texts):
                        pygame.draw.rect(self.screen, white, rect)
                        pygame.draw.rect(self.screen, black, rect, width=2, border_radius=3)
                        text = self.font.render(str(text), True, black)
                        self.screen.blit(text, (rect.x + 2, rect.y))

                    pygame.display.update()
                    pygame.time.wait(30)
                    pygame.quit()
                    break


async def main():
    """Main asyncio function to start connection"""
    player = Player()
    await player.estab_comms()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (Exception, KeyboardInterrupt):
        print("Error, restart game")
=======
import asyncio
# import sys
from collections import deque

import pygame
import websockets

black = (0, 0, 0)
white = (255, 255, 255)

options_dict = {
    1: "See rooms",
    2: "Create Room",
    3: "Join Room",
    4: "Leave Room",
    5: "Leave game"
}


class Player:
    """Handle asynchronous player creation, input and communication with server"""

    def __init__(self, width: int = 1200, height: int = 800):
        # self.name = None
        # self.websocket = websocket
        pygame.init()
        self._pid_ = None
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill((255, 255, 255))
        self.game_rect = None
        self.texts = deque()
        self.text_buffer = []
        self.shift_active = False
        self.chat_bars = []
        self.menu_rects = []
        self.font = pygame.font.SysFont('Arial', 16)
        #self.chatbox = pygame.draw.rect(self.screen, black, (480, 230, 160, 40), width=2)
        self.text_edi_rect = None
        self.comm_text = None
        self.server_rects = []

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
        self.game_rect = pygame.draw.rect(self.screen, black, [0, 0, 895, self.height], width=5)
    # y = pygame.Rect(0, 0, 470, height)

    def menu_panel(self):
        menu_w_start = 1050
        for i, j in zip(range(20, 220, 40), options_dict.values()):
            text = self.font.render(j, True, black)
            rect = pygame.draw.rect(self.screen, black, rect=pygame.Rect((menu_w_start, i, 100, 30)), width=1)
            self.screen.blit(text, (menu_w_start + 10, i + 5))
            self.menu_rects.append((rect, j))

    def chat_panel(self):
        chat_w_start = 900
        chat_h_start = 450
        text = self.font.render("Server messages", True, black)
        self.screen.blit(text, (chat_w_start+5, 235))

        for i in range(260, chat_h_start - 60, 20):
            self.server_rects.append(pygame.Rect((chat_w_start+5, i, self.width-(chat_w_start+18), 20)))

        chat_rect = pygame.Rect((chat_w_start,
                                 chat_h_start,
                                 self.width-(chat_w_start+10),
                                 self.height-(chat_h_start+10)))

        pygame.draw.rect(self.screen, black, rect=chat_rect, width=2)

        text = self.font.render("Chat room", True, black)
        self.screen.blit(text, (chat_w_start+5, chat_h_start-20))

        self.text_edi_rect = pygame.Rect(chat_w_start+1, chat_h_start+1, 289, 30)
        pygame.draw.rect(self.screen, black, self.text_edi_rect, width=1)

        self.texts = deque(self.texts, maxlen=(self.height - chat_h_start - 80)//20)

        for i in range(chat_h_start + 40, self.height - 40, 20):
            self.chat_bars.append(pygame.Rect((chat_w_start+5, i, self.width-(chat_w_start+18), 20)))

        for rect in self.server_rects:
            pygame.draw.rect(self.screen, black, rect, width=1)

        for rect in self.chat_bars:
            pygame.draw.rect(self.screen, black, rect, width=1)

    def print_buffer(self):
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

    async def estab_comms(self):
        """Establish asynchronous communication with server, handle game loop"""

        self.game_panel()
        self.menu_panel()
        self.chat_panel()
        pygame.display.flip()

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
                        for rect, text in zip(self.server_rects, self.server_rects):
                            #pygame.draw.rect(self.screen, white, rect)
                            pygame.draw.rect(self.screen, black, rect, width=1)
                            #text = self.font.render(str(text), True, black)
                            #self.screen.blit(text, (rect.x + 2, rect.y))

                        for rect, text in zip(self.chat_bars, self.texts):
                            pygame.draw.rect(self.screen, white, rect)
                            pygame.draw.rect(self.screen, black, rect, width=1)
                            text = self.font.render(str(text), True, black)
                            self.screen.blit(text, (rect.x + 2, rect.y))

                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                for rect, text in self.menu_rects:
                                    if rect.collidepoint(pygame.mouse.get_pos()):
                                        self.comm_text = text

                                if self.text_edi_rect.collidepoint(pygame.mouse.get_pos()):
                                    self.shift_active = True

                            if self.shift_active:
                                if event.type == pygame.KEYUP:
                                    if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                                        self.text_buffer.append(pygame.key.name(event.key) + "end")

                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_RETURN:
                                        self.shift_active = False
                                        pygame.draw.rect(self.screen, white, rect=self.text_edi_rect)
                                        self.comm_text = self.print_buffer()
                                        self.text_buffer.clear()

                                    elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                                        self.text_buffer.append(pygame.key.name(event.key) + "start")
                                    elif event.key == pygame.K_BACKSPACE:
                                        self.text_buffer.append('back')
                                    elif event.key == pygame.K_SPACE:
                                        self.text_buffer.append(" ")
                                    else:
                                        self.text_buffer.append(pygame.key.name(event.key))

                                pygame.draw.rect(self.screen, white, rect=self.text_edi_rect)
                                pygame.draw.rect(self.screen, black, self.text_edi_rect, width=1)
                                text = self.font.render(self.print_buffer()[-40:], True, black)
                                self.screen.blit(text, (self.text_edi_rect.x + 5, self.text_edi_rect.y + 2))

                            if event.type == pygame.QUIT:
                                raise KeyboardInterrupt

                        pygame.display.update()

                        if self.comm_text is None:
                            continue

                        if self.comm_text in options_dict.values():
                            await websocket.send(self.comm_text)
                        else:
                            await websocket.send(f"PID###{self.pid}: {self.comm_text}")

                        self.comm_text = None
                        while True:
                            received_message = await websocket.recv()
                            match received_message:

                                case 'Enter Player ID':
                                    await websocket.send(str(self.pid))

                                case 'Enter Room ID':
                                    rid = input("Enter Room ID: ")
                                    await websocket.send(rid)

                                case _:
                                    self.texts += received_message.split("\n")
                                    break

                    #await asyncio.sleep(1)

                except Exception as e:
                    # handle abrupt termination as well 'Leave game' option

                    await websocket.send(options_dict[5])
                    received_message = await websocket.recv()
                    self.texts.append(received_message)

                    await websocket.send(str(self.pid))
                    # print('Player ID sent')
                    received_message = await websocket.recv()
                    #self.texts.append(received_message)

                    self.texts.append('Bye, Game closed')
                    pygame.quit()
                    break


async def main():
    """Main asyncio function to start connection"""

    player = Player()
    await player.estab_comms()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (Exception, KeyboardInterrupt) as e:
        print("Out")
>>>>>>> origin/mirror_server
