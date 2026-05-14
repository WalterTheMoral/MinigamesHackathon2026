import socket
import threading
import time


in_processing_players = []
running_games = []

class single_game:

    def __init__(self, game_password):
         self.player_count = 0
         self.game_state = "waiting"
         self.player_list = []
         self.game_password = game_password

    def add_player(self, player):
        self.player_count += 1
        self.player_list.append(player)

    def broadcast(self, message):
        for p in self.player_list:
            try:
                p.socket.send(message.encode())
            except:
                pass
    pass

class player:

    def __init__(self, socket, is_host):
        self.socket = socket
        self.host = is_host

    pass

def search_for_games(password):
    for game in running_games:
        if(password == game.game_password):
            print("connected")
            return game
    print("failed")
    return None


def lobby_thread_func():

    while True:
        # 1. Try to accept NEW people without blocking
        try:
            client_conn, addr = server_socket.accept()
            client_conn.setblocking(False)
            client_conn.send(b"Welcome! Type 'HOST' or 'JOIN': ")
            in_processing_players.append({"socket": client_conn, "state": "CHOOSING"})

        except BlockingIOError:
            pass  # No one is trying to connect right now

        # 2. Check on people currently in the "Handshake" phase
        for p_data in in_processing_players[:]:  # Iterate over a copy
            sock = p_data["socket"]
            try:
                data = sock.recv(1024).decode().strip().upper()
                if not data: continue

                if p_data["state"] == "CHOOSING":
                    if data == "HOST":
                        sock.send(b"Enter a password for your game: ")
                        p_data["state"] = "SETTING_PASSWORD"

                    elif data == "JOIN":
                        sock.send(b"Enter Password: ")
                        p_data["state"] = "PASSWORD_CHECK"

                elif p_data["state"] == "SETTING_PASSWORD":
                    new_player = player(sock,True)
                    password = data
                    new_game = single_game(password)
                    new_game.add_player(new_player)
                    running_games.append(new_game)
                    in_processing_players.remove(p_data)

                    p_data["state"] = "HOST_WAITING"
                    p_data["game_ref"] = new_game
                    sock.send(b"Game created. Waiting for players (need at least 3)...\n")

                elif p_data["state"] == "HOST_WAITING":
                    if data == "START":
                        game = p_data["game_ref"]
                        if game.player_count >= 3:
                            game.game_state = "playing"
                            game.broadcast("GAME STARTING NOW!\n")
                        else:
                            sock.send(b"Not enough players yet (need 3+).\n")

                elif p_data["state"] == "PASSWORD_CHECK":
                    target_game = search_for_games(data)
                    if target_game != None:
                        new_player = player(sock)
                        target_game.add_player(new_player)
                        in_processing_players.remove(p_data)
                        # Notify everyone
                        target_game.broadcast(f"New player joined! Total: {target_game.player_count}/5\n")

                        if target_game.player_count >= 3:
                            target_game.broadcast("Host can now type 'START' to begin!\n")

                        in_processing_players.remove(p_data)
                    else:
                        sock.send(b"Wrong! Try again: ")

            except (BlockingIOError, ConnectionResetError):
                continue  # They haven't typed anything yet, move to next person

        time.sleep(0.1)  # Prevent 100% CPU usage


def game_thread_func():
    while True:
        for game in running_games:
            if game.game_state == "playing":
                # 1. Send the first mini-game type to everyone
                game.broadcast("MINIGAME: MOUSE_CLICKER")

                # 2. Transition to a logic-handling state
                # (You'll need a way to ensure this only runs once)
                game.game_state = "in_minigame"
    pass


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5555))
server_socket.listen(10)

lobby_thread = threading.Thread(target=lobby_thread_func, daemon=True)
game_thread = threading.Thread(target=game_thread_func, daemon=True)

lobby_thread.start()
game_thread.start()


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
