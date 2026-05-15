import socket
import time

from Interface import password
#
# player_id = 0
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect(('127.0.0.1', 8080))
# if (host):
#     sock.send("host".encode('utf-8'))
# if(client):
#     sock.send(password.encode('utf-8'))
#     time.sleep(1)
#     player_id = sock.recv(1024)
#
#
# def shopping():
#     money = sock.recv(1024).decode().strip().upper()
#     display_money(money)
#     currency = money[player_id]
#     purchase = shopping(currency)
#
#     sock.send(purchase)
#
#
# def miniGame(id):
#     run_mini_game(id)
#
# def is_host():
#
#
# while (True):
#     state = sock.recv(1024).decode('utf-8')
#     if(state == "waiting"):
#         continue
#     if(state == "start minigame"):
#         result = miniGame(sock.recv(1024).decode().strip().upper())
#         sock.send(result)
#         continue
#     if(state == "waiting for result"):
#         continue
#
#     if(state == "leaderboards"):
#         placement = sock.recv(1024).decode().strip().upper()
#         if placement != state:
#             display_leaderboards(result)
#         time.sleep(5)
#     if(state == "buy phase"):
#         shopping()
#         continue
#     if(state == "game finished"):
#         break
#
# time.sleep(1)
# end_result = sock.recv(1024).decode().strip().upper()
# game_over(end_result)
#

class Client:
    def __init__(self, is_host=False):
        self.is_host_flag = is_host
        self.player_id = 0
        self.coins = 10
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 8080))
        self.active_bid = {"amount": 0, "predicted_rank": 0}

    def get_player_id(self):
        return self.sock.recv(1024).decode().strip().upper()
    def get_rankings(self):
        return self.sock.recv(1024).decode().strip().upper()[self.player_id]

    def get_player_money(self):
        return self.sock.recv(1024).decode().strip().upper()[self.player_id]
    
    def get_all_money(self):
        return self.sock.recv(1024).decode().strip().upper()

    def send_left_money(self, money):
        self.sock.sendall(money.encode(int))

    def get_minigame(self):
        return self.sock.recv(1024).decode().strip().upper()

    def get_state(self):
        return self.sock.recv(1024).decode().strip().upper()

    def joined_count(self):
        return self.sock.recv(1024).decode().strip().upper()[self.player_id]

    def place_pre_game_bid(self, bid, rank):
        try:
            self.active_bid = {"amount": bid, "predicted_rank": rank}
            print(f"Bid locked: {bid} coins on Rank {rank}.")
        except ValueError:
            self.active_bid = {"amount": 0, "predicted_rank": 0}

    def check_bid(self, leaderboard_str):
        """
        Parses: 'LEADERBOARD: P0: 10.5 | P1: 8.0'
        Calculates if the bid was successful.
        """
        # 1. Strip the prefix and split into individual entries
        data = leaderboard_str.replace("LEADERBOARD: ", "").strip()
        entries = data.split(" | ")

        actual_rank = -1
        for index, entry in enumerate(entries):
            # entry looks like 'P0: 10.5'
            if f"P{self.player_id}:" in entry:
                actual_rank = index + 1  # Ranks are 1-based (1st, 2nd, etc)
                break

        print(f"\n--- Round Results ---")
        print(f"You placed: {actual_rank}")
        print(f"You predicted: {self.predicted_rank}")

        # 2. Logic: If correct, add the bid amount. If wrong, subtract it.
        if self.active_bid_amount > 0:
            if actual_rank == self.predicted_rank:
                print(f"BINGO! You won {self.active_bid_amount} coins.")
                self.local_coins += self.active_bid_amount
            else:
                print(f"BOO! You lost {self.active_bid_amount} coins.")
                self.local_coins -= self.active_bid_amount

        self.active_bid_amount = 0
        self.predicted_rank = 0

        return self.local_coins

