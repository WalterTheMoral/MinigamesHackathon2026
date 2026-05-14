import tkinter as tk
import random
import time


def simon_game_minigame():
    class SimonGame:
        def __init__(self, root):
            self.root = root
            self.root.title("Simon Says Challenge")
            self.root.geometry("500x600")

            self.colors = ["green", "red", "yellow", "blue"]
            self.bright_colors = ["#00FF00", "#FF0000", "#FFFF00", "#0000FF"]
            self.dark_colors = ["#008000", "#800000", "#808000", "#000080"]

            self.sequence = []
            self.user_index = 0
            self.accept_input = False

            self.canvas = tk.Canvas(root, width=400, height=400, bg="white", highlightthickness=0)
            self.canvas.pack(pady=20)

            self.buttons = {
                "green": self.canvas.create_arc(50, 50, 350, 350, start=90, extent=90, fill=self.dark_colors[0],
                                                outline="black"),
                "red": self.canvas.create_arc(50, 50, 350, 350, start=0, extent=90, fill=self.dark_colors[1],
                                              outline="black"),
                "yellow": self.canvas.create_arc(50, 50, 350, 350, start=180, extent=90, fill=self.dark_colors[2],
                                                 outline="black"),
                "blue": self.canvas.create_arc(50, 50, 350, 350, start=270, extent=90, fill=self.dark_colors[3],
                                               outline="black")
            }

            self.info_label = tk.Label(root, text="Press Start to Play", font=("Arial", 16))
            self.info_label.pack()

            self.start_btn = tk.Button(root, text="Start Game", command=self.start_game, font=("Arial", 12), width=15)
            self.start_btn.pack(pady=10)

            self.canvas.bind("<Button-1>", self.on_canvas_click)

        def start_game(self):
            self.sequence = []
            self.start_btn.config(state="disabled")
            self.next_round()

        def next_round(self):
            self.user_index = 0
            self.accept_input = False
            self.sequence.append(random.choice(self.colors))
            self.info_label.config(text=f"Watch the Sequence! (Round {len(self.sequence)})")
            self.root.after(1000, self.play_sequence)

        def play_sequence(self):
            delay = 0
            for color in self.sequence:
                self.root.after(delay, lambda c=color: self.flash_button(c))
                delay += 600
            self.root.after(delay, self.enable_input)

        def enable_input(self):
            self.accept_input = True
            self.info_label.config(text="Your Turn!")

        def flash_button(self, color):
            idx = self.colors.index(color)
            self.canvas.itemconfig(self.buttons[color], fill=self.bright_colors[idx])
            self.root.after(300, lambda: self.canvas.itemconfig(self.buttons[color], fill=self.dark_colors[idx]))

        def on_canvas_click(self, event):
            if not self.accept_input:
                return

            items = self.canvas.find_closest(event.x, event.y)
            if not items: return
            item = items[0]

            clicked_color = None
            for color, tag in self.buttons.items():
                if tag == item:
                    clicked_color = color

            if clicked_color:
                self.flash_button(clicked_color)
                self.check_answer(clicked_color)

        def check_answer(self, color):
            if color == self.sequence[self.user_index]:
                self.user_index += 1
                if self.user_index == len(self.sequence):
                    self.accept_input = False
                    self.info_label.config(text="Correct!")
                    self.root.after(1000, self.next_round)
            else:
                # --- THIS IS THE CHANGE ---
                # We subtract 1 because the user failed the CURRENT round
                completed_rounds = len(self.sequence) - 1
                self.info_label.config(text=f"Game Over!\nTotal Successful Rounds: {completed_rounds}")
                self.start_btn.config(state="normal", text="Restart")
                self.accept_input = False

    root = tk.Tk()
    game = SimonGame(root)
    root.mainloop()


# To run the game
simon_game_minigame()