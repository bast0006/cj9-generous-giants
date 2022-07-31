# Generous Giants

# A multiplayer game named " "

We've developed a multiplayer game where you can walk around and explore randomly generated maps together. We'd intended to add combat and weaponry but unfortunately ran out of time.

## Setup:
1. Create a virtual environment with `python -m venv env`
2. Activate it (`source ./env/bin/activate` or your platform's equivalent.)
3. Install dependencies `pip install -r requirements.txt`
4. Ensure you have the server running (`python src/server.py`)
5. Run clients! `python main.py [optional ws url]`. The default url is `ws://localhost:8001`.
6. Create a room. You can join a room specifically with `/join room-name`. Type `/help` for other commands, and `/start` to start the game!
7. Move with WASD, and press R to regenerate the map!
8. Press number keys to trigger some custom sounds we've made!

Bugs that are features:
You can change your nick at any time, to anyone's for fun!
Characters can walk off the map over your ui!
Characters can go up off the screen to show up on the bottom!
You can join games in progress just like regular games
Anyone can trigger a map refresh
Characters "glitch" when leaving "Safe" areas on the map


Sprites thanks to https://kenney.nl/, under the CC0 license.

## Screenshots!

![Where you start](/screenshots/rooms.png "The starting interface")
![Playing together](/screenshots/say-hi.png "A map, and a friend")
1[Around the UI we go](/screenshots/bugs.png)
