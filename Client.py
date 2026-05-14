import socket
import time
from http import client
from locale import currency
from unittest import result
from urllib import request

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


gameRunning = False
while(gameRunning == False):
    state = sock.recv(1024).decode('utf-8')
    if(state == "running"):
        gameRunning = True
def shopping():
    money = sock.recv(1024)
    displayLeaderBoard(money)
    currency = money[player_id]
    purchase = shopping(currency)
    bid = purchase[0]
    purchase.pop(0)
    sock.send(purchase)
    return bid


def miniGame(int id):




while (True):
    result = miniGame(sock.recv(1024).decode(int))
    sock.send(str(result).encode('utf-8'))
    time.sleep(1)
    result = sock.recv(1024)
    show_result(result)

    bid = shopping()



