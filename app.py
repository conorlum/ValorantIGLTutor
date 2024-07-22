import tkinter as tk
from tkinter import messagebox

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Valorant IGL Help")
        self.geometry("1500x800")

        self.round = 1
        
        self.tableTopText = tk.Text(self, height=1, width=10)
        self.tableTopText.insert(tk.END, "ROUNDS")
        self.tableTopText.place(x=750, y=0)

        
        for i in range(1,32):
            self.tableRoundText = tk.Text(self, height=1, width=5)
            self.tableRoundText.insert(tk.END, str(i))
            self.tableRoundText.place(x=20+45*i, y=30)

        self.tableOutcomeTexts = []
        for i in range(1,32):
            self.tableOutcomeText = tk.Text(self, bg="white", height=1, width=5)
            self.tableOutcomeText.place(x=20+45*i, y=50)
            self.tableOutcomeTexts.append(self.tableOutcomeText)

        self.roundOnText = tk.Text(self, height=1, width=23, font=("Helvetica", 32))
        self.roundOnText.insert(tk.END, "OUTCOME OF ROUND: " + str(self.round))
        self.roundOnText.place(x=500, y=80)

      self.roundWinButton = tk.Button(self, text="Round Win", command=self.roundWinButtonAction)
        self.roundWinButton.config(height=3, width=25, bg="green")
        self.roundWinButton.place(x=200, y=80)

        self.roundLossButton = tk.Button(self, text="Round Loss", command=self.roundLossButtonAction)
        self.roundLossButton.config(height=3, width=25, bg="red")
        self.roundLossButton.place(x=1200, y=80)


    def roundWinButtonAction(self):
        tableOutcomeText = self.tableOutcomeTexts[self.round-1]
        tableOutcomeText.config(bg="green")
        self.round += 1
        self.roundOnText.delete('1.0', tk.END)
        self.roundOnText.insert(tk.END, "OUTCOME OF ROUND: " + str(self.round))

    def roundLossButtonAction(self):
        tableOutcomeText = self.tableOutcomeTexts[self.round-1]
        tableOutcomeText.config(bg="red")
        self.round += 1
        self.roundOnText.delete('1.0', tk.END)
        self.roundOnText.insert(tk.END, "OUTCOME OF ROUND: " + str(self.round))


# Create and run the application
if __name__ == "__main__":
    app = Application()
    app.mainloop()
