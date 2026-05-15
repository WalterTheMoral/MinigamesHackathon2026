import socket
import time



import socket
import threading
import time
import random
import sys


class GameClient:
    def __init__(self, host='10.13.244.168', port=5555):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.player_id = None
        self.coins = 0
        self.active_bid = {"amount": 0, "predicted_rank": 0}

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")

            # Start background thread to listen for server messages
            threading.Thread(target=self.listen_to_server, daemon=True).start()

            # Start main loop for user inputs
            self.handle_user_input()
        except ConnectionRefusedError:
            print("Connection failed. Is the server running?")

    def listen_to_server(self):
        buffer = ""
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    print("\n[Disconnected from server]")
                    sys.exit(0)

                buffer += data

                # 1. Handle prompts that don't end in newlines
                prompts = [
                    "Welcome! Type 'HOST' or 'JOIN': ",
                    "Enter a password for your game: ",
                    "Enter Password: ",
                    "Wrong! Try again: "
                ]
                for prompt in prompts:
                    if prompt in buffer:
                        print(f"\n[SERVER] {prompt}", end="", flush=True)
                        buffer = buffer.replace(prompt, "")

                # 2. Handle complete lines from the server
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.process_server_command(line.strip())

            except Exception as e:
                print(f"\n[Connection Error] {e}")
                sys.exit(1)

    def process_server_command(self, msg):
        if not msg:
            return

        # FIX: Handle the missing newline issue in the server where
        # YOUR_ID and START_GAME get glued together into one string.
        if "YOUR_ID:" in msg:
            id_start = msg.find("YOUR_ID:") + 8
            start_game_idx = msg.find("START_GAME:")

            if start_game_idx != -1:
                self.player_id = msg[id_start:start_game_idx]
                print(f"\n[SERVER] Assigned Player ID: {self.player_id}")
                msg = msg[start_game_idx:]  # Leave START_GAME to be processed below
            else:
                self.player_id = msg[id_start:]
                print(f"\n[SERVER] Assigned Player ID: {self.player_id}")
                return

        # Handle specific game states based on your server's logic
        if msg.startswith("START_GAME:"):
            game_name = msg.split(":")[1]
            self.run_mini_game(game_name)

        elif msg.startswith("LEADERBOARD:"):
            print(f"\n[LEADERBOARD] {msg.replace('LEADERBOARD:', '').strip()}")

        elif msg.startswith("PHASE:BUY"):
            self.shopping()

        elif msg.startswith("FINAL_RESULTS:"):
            print(f"\n[GAME OVER] {msg.replace('FINAL_RESULTS:', '').strip()}")

        elif msg.startswith("DISCONNECT:"):
            print("\n[SERVER CLOSED GAME]")
            sys.exit(0)

        else:
            # Catch-all for basic server messages (like "Game created. Waiting for players...")
            print(f"\n[SERVER] {msg}")

    def run_mini_game(self, game_name):
        print(f"\n>>> Starting Minigame: {game_name} <<<")
        print("Playing... (Simulating gameplay for 2 seconds)")
        time.sleep(2)

        # Server expects format: "score_value,score" or "score_value,time"
        # We simulate a random score to automatically send back.
        score = round(random.uniform(10.0, 50.0), 1)
        result_str = f"{score},score"

        print(f"-> Finished! Sending result: {result_str}")
        self.sock.sendall(result_str.encode('utf-8'))

    def shopping(self):
        print("\n>>> SHOP PHASE <<<")
        print(f"Local Coins tracked: {self.coins}")
        # The server expects us to send an integer back right now to set our new coin balance.
        print("Type your updated coin balance as an integer to send to the server (e.g., '15'): ", end="", flush=True)

    def handle_user_input(self):
        # This loop purely exists to take whatever you type in the terminal
        # and send it to the server. (e.g. typing HOST, password, START, or coin amounts)
        while True:
            try:
                user_input = input()
                if user_input:
                    self.sock.sendall(user_input.encode('utf-8'))
            except KeyboardInterrupt:
                print("\nClosing client...")
                self.sock.close()
                sys.exit(0)

    def place_pre_game_bid(self, bid, rank):
        try:
            self.active_bid_amount = bid
            self.predicted_rank = rank
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

        # 2. Logic: If correct, add the bid amount. If wrong, subtract it.
        if self.active_bid_amount > 0:
            if actual_rank == self.predicted_rank:
                print(f"BINGO! You won {self.active_bid_amount} coins.")
                self.coins += self.active_bid_amount
            else:
                print(f"BOO! You lost {self.active_bid_amount} coins.")
                self.coins -= self.active_bid_amount

        self.active_bid_amount = 0
        self.predicted_rank = 0

        return self.coins


if __name__ == "__main__":
    client = GameClient()
    client.connect()