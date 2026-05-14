import socket
import time

from MinigamesHackathon2026.Interface import password

player_id = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 8080))
if (host):
    sock.send("host".encode('utf-8'))
if(client):
    sock.send(password.encode('utf-8'))
    time.sleep(1)
    player_id = sock.recv(1024)


def shopping():
    money = sock.recv(1024).decode().strip().upper()
    display_money(money)
    currency = money[player_id]
    purchase = shopping(currency)

    sock.send(purchase)


def miniGame(id):
    run_mini_game(id)

def is_host():


while (True):
    state = sock.recv(1024).decode('utf-8')
    if(state == "waiting"):
        continue
    if(state == "start minigame"):
        result = miniGame(sock.recv(1024).decode().strip().upper())
        sock.send(result)
        continue
    if(state == "waiting for result"):
        continue

    if(state == "leaderboards"):
        placement = sock.recv(1024).decode().strip().upper()
        if placement != state:
            display_leaderboards(result)
        time.sleep(5)
    if(state == "buy phase"):
        shopping()
        continue
    if(state == "game finished"):
        break

time.sleep(1)
end_result = sock.recv(1024).decode().strip().upper()
game_over(end_result)


class Client:
    def __init__(self, is_host=False):
        self.is_host_flag = is_host
        self.player_id = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 8080))

    def get_rankings(self):

    def shopping_phase(self):
        money = self.sock.recv(1024).decode().strip().upper()
        self.display_money(money)
        currency = money[self.player_id]
        purchase = self.get_purchase(currency)  # renamed to avoid recursion
        self.sock.sendall(purchase.encode('utf-8'))

    def get_minigame(self):
        return self.sock.recv(1024).decode().strip().upper()

    def has_started(self):
        return (sock.recv(1024).decode().strip().upper() != "waiting")

    def joined_count(self):
        return sock.recv(1024).decode().strip().upper()[self.player_id]
