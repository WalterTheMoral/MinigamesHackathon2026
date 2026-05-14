import tkinter as tk
import random
import time


def reaction_time_minigame():
    # We store the final sum in a list so the function can "grab" it at the end
    result_data = {"total_sum": 0}

    class ReactionGame:
        def __init__(self, root):
            self.root = root
            self.root.title("Reaction Timer")
            self.root.geometry("600x400")

            self.start_time = 0
            self.waiting = False
            self.tries = 0
            self.scores = []

            self.label = tk.Label(root, text="Click to Start\n(2 Tries)", font=("Arial", 30),
                                  bg="white", width=100, height=100)
            self.label.pack(expand=True, fill="both")
            self.label.bind("<Button-1>", self.handle_click)

        def handle_click(self, event):
            if self.tries >= 2:
                return

            if self.label["text"] == "Click to Start\n(2 Tries)" or "ms" in self.label["text"] or "EARLY" in self.label[
                "text"]:
                self.label.config(text="Wait for Green...", bg="red")
                self.waiting = True
                self.root.after(random.randint(2000, 5000), self.turn_green)

            elif self.waiting:
                self.label.config(text="TOO EARLY!\nClick to try again", bg="orange")
                self.waiting = False

            elif self.label["bg"] == "green":
                end_time = time.time()
                result = int((end_time - self.start_time) * 1000)
                self.scores.append(result)
                self.tries += 1

                if self.tries < 2:
                    self.label.config(text=f"{result} ms\nClick for Try 2", bg="white")
                else:
                    total = sum(self.scores)
                    result_data["total_sum"] = total  # Save the final sum here
                    self.label.config(text=f"DONE!\nTotal Sum: {total} ms", bg="cyan")

        def turn_green(self):
            if self.waiting:
                self.label.config(bg="green", text="CLICK NOW!")
                self.start_time = time.time()
                self.waiting = False

    root = tk.Tk()
    game = ReactionGame(root)
    root.mainloop()

    # This returns the total sum.
    # If total_sum is 0, Python treats this as False.
    # If total_sum > 0, Python treats this as True.
    return result_data["total_sum"]


# --- How to use the return ---
final_result = reaction_time_minigame()
print(f"The total time returned was: {final_result}")