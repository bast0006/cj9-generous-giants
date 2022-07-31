import asyncio
import sys
import threading
import time
import traceback

import pygame

from src.game import Game
from src.true_client import Player


async def main():
    """Main asyncio function to start connection"""
    await player.estab_comms()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    ws_thread = threading.Thread(target=loop.run_forever)
    game = Game()

    if len(sys.argv) > 1:
        websocket_url = sys.argv[1]
    else:
        websocket_url = 'ws://localhost:8001'  # Default to localhost

    player = Player(websocket_url)

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
