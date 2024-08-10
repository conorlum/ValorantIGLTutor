import tkinter as tk
from tkinter import *
from tkinter import PhotoImage

class Application(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Valorant IGL Help")
		self.geometry("1500x1000")
		

		self.round = 1
		self.roundPlanTypes = ["Pistol", "ECO", "Full Buy"]
		self.roundPlanType = 0
		
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

		self.roundPlanText = tk.Text(self, height=1, width=23, font=("Helvetica", 32))
		self.roundPlanText.insert(tk.END, "Plan for Round: " + str(self.round) + "  " + self.roundPlanTypes[self.roundPlanType])
		self.roundPlanText.place(x=500, y=150)

		self.roundWinButton = tk.Button(self, text="Round Win", command=self.roundWinButtonAction)
		self.roundWinButton.config(height=3, width=25, bg="green")
		self.roundWinButton.place(x=200, y=80)

		self.roundLossButton = tk.Button(self, text="Round Loss", command=self.roundLossButtonAction)
		self.roundLossButton.config(height=3, width=25, bg="red")
		self.roundLossButton.place(x=1200, y=80)

		self.roundTypeCycleButton = tk.Button(self, text="Plan Type Cycle", command=self.roundTypeCycleButtonAction)
		self.roundTypeCycleButton.config(height=3, width=25, bg="yellow")
		self.roundTypeCycleButton.place(x=1100, y=150)

		self.imageLabel1 = tk.Label(self)#crop and resize in place then so that using the big picutre later is easy and not shit resolution
		image = PhotoImage(file="Rush.png")
		self.imageLabel1.config(image=image)
		self.imageLabel1.image = image
		
		self.imageLabel1.place(x=400,y=400)


		




	def roundWinButtonAction(self):
		tableOutcomeText = self.tableOutcomeTexts[self.round-1]
		tableOutcomeText.config(bg="green")
		self.round += 1
		self.refreshRoundOnText()
		self.refreshPlanText()

	def roundLossButtonAction(self):
		tableOutcomeText = self.tableOutcomeTexts[self.round-1]
		tableOutcomeText.config(bg="red")
		self.round += 1
		self.refreshRoundOnText()
		self.refreshPlanText()

	def roundTypeCycleButtonAction(self):
		self.roundPlanType = (self.roundPlanType + 1) % 3
		self.refreshPlanText()


	def refreshRoundOnText(self):
		self.roundOnText.delete('1.0', tk.END)
		self.roundOnText.insert(tk.END, "OUTCOME OF ROUND: " + str(self.round))

	def refreshPlanText(self):
		self.roundPlanText.delete('1.0', tk.END)
		self.roundPlanText.insert(tk.END, "Plan for Round: " + str(self.round) + "  " + self.roundPlanTypes[self.roundPlanType])



# Create and run the application
if __name__ == "__main__":
	app = Application()
	app.mainloop()
