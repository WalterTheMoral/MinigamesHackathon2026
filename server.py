import socket
import threading
import time
import random

in_processing_players = []
running_games = []
game_lock = threading.Lock()


class single_game:

    def __init__(self, game_password):
        self.player_count = 0
        self.game_state = "waiting"
        self.player_list = []
        self.game_password = game_password
        self.id_of_games_left = [0, 1, 2, 3, 4, 5, 6, 7]
        self.mini_game_results = {}

    def add_player(self, player):
        self.player_count += 1
        self.player_list.append(player)

    def broadcast(self, message):
        formatted_msg = f"{message}\n"
        encoded_msg = formatted_msg.encode('utf-8')
        disconnected_players = []

        for p in list(self.player_list):
            try:
                p.socket.sendall(encoded_msg)
            except (ConnectionError, socket.error) as e:
                print(f"Error sending to player. Disconnecting them. Error: {e}")
                disconnected_players.append(p)
            except Exception as e:
                print(f"Unexpected error: {e}")
                disconnected_players.append(p)

        for p in disconnected_players:
            if p in self.player_list:
                self.player_list.remove(p)
            try:
                p.socket.close()
            except:
                pass

    def give_players_id(self):
        for i in range(len(self.player_list)):
            self.player_list[i].give_player_id(i)

    def generate_game_id(self):
        if not self.id_of_games_left:
            return "FINISHED"
        index = random.randrange(0, len(self.id_of_games_left))
        return self.id_of_games_left.pop(index)

    def organize_leader_board(self):
        processed_results = []
        for p, raw_data in self.mini_game_results.items():
            try:
                parts = raw_data.split(",")
                if len(parts) != 2: continue

                score_val = float(parts[0])
                score_type = parts[1].strip().lower()

                processed_results.append({
                    'player_obj': p,
                    'p_id': p.player_id,
                    'score': score_val,
                    'is_score': score_type == "score"
                })
            except Exception as e:
                print(f"Error parsing score: {e}")
                continue

        if not processed_results:
            self.leaderboard_display = "No results."
            return

        is_score_game = processed_results[0]['is_score']
        processed_results.sort(key=lambda x: x['score'], reverse=is_score_game)

        # Award coins using the actual player objects
        self.award_coins(processed_results)

        self.leaderboard_display = " | ".join([f"P{res['p_id']}: {res['score']}" for res in processed_results])

    def award_coins(self, sorted_results):
        rewards = [25, 20, 15, 10, 5]

        for rank, entry in enumerate(sorted_results):
            if rank < len(rewards):
                # FIXED: Retrieve the exact player object avoiding list index mismatches.
                target_player = entry['player_obj']
                target_player.coins += rewards[rank]
                print(f"P{entry['p_id']} (Rank {rank + 1}) awarded {rewards[rank]} coins.")


class player:
    def __init__(self, socket, is_host):
        self.socket = socket
        self.host = is_host
        self.coins = 0

    def give_player_id(self, id):
        self.player_id = id


def search_for_games(password):
    for game in running_games:
        if (password == game.game_password):
            print("connected")
            return game
    print("failed")
    return None


def mini_game_switch(mini_game_id):
    game_list = ["space", "colour", "circle", "blink", "rhythm", "reaction", "trivia", "speed"]
    return game_list[mini_game_id]


def lobby_thread_func():
    while True:
        try:
            client_conn, addr = server_socket.accept()
            client_conn.setblocking(False)
            client_conn.send(b"Welcome! Type 'HOST' or 'JOIN': ")
            in_processing_players.append({"socket": client_conn, "state": "CHOOSING"})
        except BlockingIOError:
            pass

        for p_data in in_processing_players[:]:
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
                    new_player = player(sock, True)
                    password = data
                    new_game = single_game(password)
                    new_game.add_player(new_player)
                    running_games.append(new_game)
                    p_data["state"] = "HOST_WAITING"
                    p_data["game_ref"] = new_game
                    sock.send(b"Game created. Waiting for players (need at least 3)...\n")

                elif p_data["state"] == "HOST_WAITING":
                    if data == "START":
                        game = p_data["game_ref"]
                        if game.player_count >= 2:
                            game.give_players_id()
                            game.game_state = "playing"
                            in_processing_players.remove(p_data)
                            game.broadcast("GAME STARTING NOW!\n")
                        else:
                            sock.send(b"Not enough players yet (need 3+).\n")

                elif p_data["state"] == "PASSWORD_CHECK":
                    with game_lock:
                        target_game = search_for_games(data)
                        if target_game != None:
                            new_player = player(sock, False)
                            target_game.add_player(new_player)
                            target_game.broadcast(f"Player joined! Total players: {target_game.player_count}")
                            in_processing_players.remove(p_data)
                        else:
                            sock.send(b"Wrong! Try again: ")

            except (BlockingIOError, ConnectionResetError):
                continue
        time.sleep(0.1)


def game_thread_func():
    while True:
        with game_lock:
            for game in running_games[:]:
                if game.game_state == "playing":
                    if not game.id_of_games_left:
                        game.game_state = "end_game"
                        continue
                    game_id = game.generate_game_id()
                    for p in game.player_list[:]:
                        try:
                            p.socket.sendall(f"YOUR_ID:{p.player_id}".encode())
                        except:
                            game.player_list.remove(p)
                            game.player_count -= 1

                    game_name = mini_game_switch(game_id)
                    game.broadcast(f"START_GAME:{game_name}\n".encode('utf-8'))

                    game.mini_game_results = {}
                    game.game_state = "waiting_for_results"

                elif game.game_state == "waiting_for_results":
                    for p in game.player_list[:]:
                        if p in game.mini_game_results:
                            continue
                        try:
                            data = p.socket.recv(1024).decode().strip()
                            if data:
                                game.mini_game_results[p] = data
                        except BlockingIOError:
                            continue
                        except:
                            game.player_list.remove(p)
                            game.player_count -= 1

                    if game.player_count > 0 and len(game.mini_game_results) >= game.player_count:
                        game.game_state = "leaderboard"
                    elif game.player_count == 0:
                        running_games.remove(game)

                elif game.game_state == "leaderboard":
                    game.organize_leader_board()
                    lb_msg = "LEADERBOARD: " + game.leaderboard_display
                    game.broadcast(lb_msg + "\n")

                    # Set brief pause for clients to view the leaderboard UI
                    game.wait_until = time.time() + 5
                    game.game_state = "leaderboard_wait"

                # FIXED: Non-blocking leaderboard wait so we don't freeze the threads
                elif game.game_state == "leaderboard_wait":
                    if time.time() < getattr(game, 'wait_until', 0):
                        continue

                    print("Moving to next game. Current Standings:")
                    for p in game.player_list:
                        print(f"P{p.player_id}: {p.coins} coins")

                    game.game_state = "playing"

                elif game.game_state == "end_game":
                    final_sorted = sorted(game.player_list, key=lambda p: p.coins, reverse=True)
                    results_str = " | ".join(
                        [f"RANK {i + 1}: P{p.player_id} ({p.coins} coins)" for i, p in enumerate(final_sorted)])

                    game.broadcast(f"FINAL_RESULTS: {results_str} \n")
                    time.sleep(2)
                    for p in game.player_list:
                        try:
                            p.socket.send(b"DISCONNECT: Server closing game.")
                            p.socket.close()
                        except:
                            pass
                    print(f"Game with password {game.game_password} has finished and been removed.")
                    running_games.remove(game)

        time.sleep(0.1)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5555))
server_socket.listen(10)
server_socket.setblocking(False)

lobby_thread = threading.Thread(target=lobby_thread_func, daemon=True)
game_thread = threading.Thread(target=game_thread_func, daemon=True)

lobby_thread.start()
game_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")