import tkinter as tk
import random
from tkinter import messagebox

class CrazyChaseGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Task 3: Catch Me If You Can!")
        self.window.geometry("600x500")
        self.window.configure(bg="#FFDE59") # Bright funny yellow
        
        self.score = 0
        self.taunts = ["Too slow!", "Missed me!", "Try harder!", "LOL", "My grandma is faster!", "Nope!"]
        
        self.setup_ui()

    def setup_ui(self):
        # Scoreboard
        self.label = tk.Label(self.window, text="Score: 0", font=('Comic Sans MS', 20, 'bold'), 
                              bg="#FFDE59", fg="#542437")
        self.label.pack(pady=20)

        # The "Prank" Button
        self.target = tk.Button(self.window, text="CLICK ME!", font=('Arial', 12, 'bold'),
                                bg="#FF3131", fg="white", width=10, height=2,
                                command=self.on_success)
        self.target.place(x=250, y=200)

        # Bind hover event - The button runs away when you try to click!
        self.target.bind("<Enter>", self.run_away)

    def run_away(self, event):
        # 30% chance it actually lets you try to click it, 70% it teleports
        if random.random() < 0.7:
            new_x = random.randint(50, 500)
            new_y = random.randint(100, 400)
            self.target.place(x=new_x, y=new_y)
            
            # Change the button text to mock the player
            self.target.config(text=random.choice(self.taunts), bg=random.choice(["#FF3131", "#5271FF", "#00BF63"]))

    def on_success(self):
        self.score += 10
        self.label.config(text=f"Score: {self.score}")
        
        # Surprise: Gambling!
        if self.score % 30 == 0:
            if messagebox.askyesno("GAMBLE?", "Double your points or lose them all?"):
                if random.random() > 0.5:
                    self.score *= 2
                    messagebox.showinfo("LUCKY!", "JACKPOT! Points doubled!")
                else:
                    self.score = 0
                    messagebox.showerror("OOPS", "You lost everything. Sad.")
        
        self.label.config(text=f"Score: {self.score}")
        self.run_away(None)

if __name__ == "__main__":
    game = CrazyChaseGame()
    game.window.mainloop()