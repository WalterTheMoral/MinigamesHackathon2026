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

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            threading.Thread(target=self.listen_to_server, daemon=True).start()
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

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.process_server_command(line.strip())

            except Exception as e:
                print(f"\n[Connection Error] {e}")
                sys.exit(1)

    def process_server_command(self, msg):
        if not msg:
            return

        if "YOUR_ID:" in msg:
            id_start = msg.find("YOUR_ID:") + 8
            start_game_idx = msg.find("START_GAME:")

            if start_game_idx != -1:
                self.player_id = msg[id_start:start_game_idx]
                print(f"\n[SERVER] Assigned Player ID: {self.player_id}")
                msg = msg[start_game_idx:]
            else:
                self.player_id = msg[id_start:]
                print(f"\n[SERVER] Assigned Player ID: {self.player_id}")
                return

        if msg.startswith("START_GAME:"):
            game_name = msg.split(":")[1]
            self.run_mini_game(game_name)

        elif msg.startswith("LEADERBOARD:"):
            print(f"\n[LEADERBOARD] {msg.replace('LEADERBOARD:', '').strip()}")

        elif msg.startswith("FINAL_RESULTS:"):
            print(f"\n[GAME OVER] {msg.replace('FINAL_RESULTS:', '').strip()}")

        elif msg.startswith("DISCONNECT:"):
            print("\n[SERVER CLOSED GAME]")
            sys.exit(0)
        else:
            print(f"\n[SERVER] {msg}")

    def run_mini_game(self, game_name):
        print(f"\n>>> Starting Minigame: {game_name} <<<")
        print("Playing... (Simulating gameplay for 2 seconds)")
        time.sleep(2)
        score = round(random.uniform(10.0, 50.0), 1)
        result_str = f"{score},score"
        print(f"-> Finished! Sending result: {result_str}")
        self.sock.sendall(result_str.encode('utf-8'))

    def handle_user_input(self):
        while True:
            try:
                user_input = input()
                if user_input:
                    self.sock.sendall(user_input.encode('utf-8'))
            except KeyboardInterrupt:
                print("\nClosing client...")
                self.sock.close()
                sys.exit(0)


if __name__ == "__main__":
    client = GameClient()
    client.connect()