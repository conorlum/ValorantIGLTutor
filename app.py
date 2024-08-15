import tkinter as tk
from tkinter import *
from tkinter import PhotoImage
import PIL
from PIL import Image, ImageTk
import glob

class Application(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Valorant IGL Help")
		self.geometry("1500x1100")
		

		self.round = 1
		self.roundPlanTypes = ["Pistol", "ECO", "Full Buy"]
		self.roundPlanType = 0
		self.mapName = "Ascent"
		
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

		self.roundTypeCycleButton = tk.Button(self, text="Change Plan", command=self.changePlanButtonAction)
		self.roundTypeCycleButton.config(height=3, width=25, bg="orange")
		self.roundTypeCycleButton.place(x=1300, y=150)


		self.generateMapPlanButtons()

	
	def generateMapPlanButtons(self):
		self.mapPlanButtons = []
		plansLocations = self.getGoodPlans()

		ButtonLeftTop = tk.Button(self, command=lambda: self.mapPlanButtonAction(0))
		image = self.makeThumbnail(plansLocations[0])
		image = ImageTk.PhotoImage(image)
		ButtonLeftTop.config(image=image)
		ButtonLeftTop.image = image
		ButtonLeftTop.place(x=200,y=250)
		plan = self.getPlanNameFromLocation(plansLocations[0])
		textLeftTop = tk.Text(self, height=1, width=20, font=("Helvetica", 18))
		textLeftTop.insert(tk.END, plan)
		textLeftTop.place(x=200, y=220)
		self.mapPlanButtons.append({"imageButtonElement" : ButtonLeftTop, "planLocation" : plansLocations[0], "buttonId" : 0, "textElement" : textLeftTop, "text" : plan})

		ButtonMiddleTop = tk.Button(self, command=lambda: self.mapPlanButtonAction(1))
		image = self.makeThumbnail(plansLocations[1])
		image = ImageTk.PhotoImage(image)
		ButtonMiddleTop.config(image=image)
		ButtonMiddleTop.image = image
		ButtonMiddleTop.place(x=600,y=250)
		plan = self.getPlanNameFromLocation(plansLocations[1])
		textMiddleTop = tk.Text(self, height=1, width=20, font=("Helvetica", 18))
		textMiddleTop.insert(tk.END, plan)
		textMiddleTop.place(x=600, y=220)
		self.mapPlanButtons.append({"imageButtonElement" : ButtonMiddleTop, "planLocation" : plansLocations[1], "buttonId" : 1, "textElement" : textMiddleTop, "text" : plan})

		ButtonRightTop = tk.Button(self, command=lambda: self.mapPlanButtonAction(2))
		image = self.makeThumbnail(plansLocations[2])
		image = ImageTk.PhotoImage(image)
		ButtonRightTop.config(image=image)
		ButtonRightTop.image = image
		ButtonRightTop.place(x=1000,y=250)
		plan = self.getPlanNameFromLocation(plansLocations[2])
		textRightTop = tk.Text(self, height=1, width=20, font=("Helvetica", 18))
		textRightTop.insert(tk.END, plan)
		textRightTop.place(x=1000, y=220)
		self.mapPlanButtons.append({"imageButtonElement" : ButtonRightTop, "planLocation" : plansLocations[2], "buttonId" : 2, "textElement" : textRightTop, "text" : plan})


		plansLocations = self.getDefaultPlans()

		ButtonLeftBottom = tk.Button(self, command=lambda: self.mapPlanButtonAction(3))
		image = self.makeThumbnail(plansLocations[0])
		image = ImageTk.PhotoImage(image)
		ButtonLeftBottom.config(image=image)
		ButtonLeftBottom.image = image
		ButtonLeftBottom.place(x=200,y=650)
		plan = self.getPlanNameFromLocation(plansLocations[0])
		textLeftTop = tk.Text(self, height=1, width=20, font=("Helvetica", 18))
		textLeftTop.insert(tk.END, plan)
		textLeftTop.place(x=200, y=620)
		self.mapPlanButtons.append({"imageButtonElement" : ButtonLeftBottom, "planLocation" : plansLocations[0], "buttonId" : 3, "textElement" : textLeftTop, "text" : plan})

		ButtonMiddleBottom = tk.Button(self, command=lambda: self.mapPlanButtonAction(4))
		image = self.makeThumbnail(plansLocations[1])
		image = ImageTk.PhotoImage(image)
		ButtonMiddleBottom.config(image=image)
		ButtonMiddleBottom.image = image
		ButtonMiddleBottom.place(x=600,y=650)
		plan = self.getPlanNameFromLocation(plansLocations[1])
		textMiddleTop = tk.Text(self, height=1, width=20, font=("Helvetica", 18))
		textMiddleTop.insert(tk.END, plan)
		textMiddleTop.place(x=600, y=620)
		self.mapPlanButtons.append({"imageButtonElement" : ButtonMiddleBottom, "planLocation" : plansLocations[1], "buttonId" : 4, "textElement" : textMiddleTop, "text" : plan})

		ButtonRightBottom = tk.Button(self, command=lambda: self.mapPlanButtonAction(5))
		image = self.makeThumbnail(plansLocations[2])
		image = ImageTk.PhotoImage(image)
		ButtonRightBottom.config(image=image)
		ButtonRightBottom.image = image
		ButtonRightBottom.place(x=1000,y=650)
		plan = self.getPlanNameFromLocation(plansLocations[2])
		textRightTop = tk.Text(self, height=1, width=20, font=("Helvetica", 18))
		textRightTop.insert(tk.END, plan)
		textRightTop.place(x=1000, y=620)
		self.mapPlanButtons.append({"imageButtonElement" : ButtonRightBottom, "planLocation" : plansLocations[2], "buttonId" : 5, "textElement" : textRightTop, "text" : plan})




	def getPossiblePlans(self):
		roundType = self.roundPlanTypes[self.roundPlanType]
		location = "./" + self.mapName + "/" + roundType + "/*"
		files = glob.glob(location)
		return files

	def getGoodPlans(self):
		plans = self.getPossiblePlans()
		if len(plans) == 3:
			return plans
		if len(plans) == 2:
			plans.append(plans[0])
			return plans
		if len(plans) > 3:
			#cool logic later?
			return plans[:3]

	def getDefaultPlans(self):
		location = "./" + self.mapName + "/Default/*"
		files = glob.glob(location)
		return files


	def getPlanNameFromLocation(self, location):
		return location.split("\\")[-1].split(".")[0]

	def mapPlanButtonAction(self, buttonId):
		self.removeMapPlanButtons()

		buttonElement = self.mapPlanButtons[buttonId]
		image = PIL.Image.open(buttonElement["planLocation"])
		image = image.crop((250,0,1070,773))
		image = ImageTk.PhotoImage(image)
		self.chosenPlan = tk.Label(self, image=image, text=buttonElement["text"], compound="bottom", font=("Helvetica", 18))
		self.chosenPlan.image = image
		self.chosenPlan.text = buttonElement["text"]
		self.chosenPlan.place(x=400, y=250)


		

	def removeMapPlanButtons(self):
		for button in self.mapPlanButtons:
			button["imageButtonElement"].destroy()
			button["textElement"].destroy()


	def changePlanButtonAction(self):
		self.refreshMapPlanButtons()
 

	def makeThumbnail(self, file_location):
		image = PIL.Image.open(file_location)
		image = image.crop((250,0,1070,773))
		image = image.resize((350,350))
		return image


	def roundWinButtonAction(self):
		tableOutcomeText = self.tableOutcomeTexts[self.round-1]
		tableOutcomeText.config(bg="green")
		self.round += 1
		self.refreshRoundOnText()
		self.refreshPlanText()
		self.refreshMapPlanButtons()

	def roundLossButtonAction(self):
		tableOutcomeText = self.tableOutcomeTexts[self.round-1]
		tableOutcomeText.config(bg="red")
		self.round += 1
		self.refreshRoundOnText()
		self.refreshPlanText()
		self.refreshMapPlanButtons()

	def roundTypeCycleButtonAction(self):
		self.roundPlanType = (self.roundPlanType + 1) % 3
		self.refreshPlanText()
		self.refreshMapPlanButtons()

	def refreshMapPlanButtons(self):
		self.removeMapPlanButtons()
		try:
			self.chosenPlan.destroy()
		except:
			pass
		self.generateMapPlanButtons()

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
