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


		self.mapPlanButtons = []
		plansLocations = self.getGoodPlans()

		imageLeftTop = tk.Button(self, command=lambda: self.mapPlanButtonAction(0))
		image = self.makeThumbnail(plansLocations[0])
		image = ImageTk.PhotoImage(image)
		imageLeftTop.config(image=image)
		imageLeftTop.image = image
		imageLeftTop.place(x=200,y=250)
		plan = self.getPlanNameFromLocation(plansLocations[0])
		textLeftTop = tk.Text(self, height=1, width=20, font=("Helvetica", 18))
		textLeftTop.insert(tk.END, plan)
		textLeftTop.place(x=200, y=220)
		self.mapPlanButtons.append({"imageButton" : imageLeftTop, "planLocation" : plansLocations[0], "buttonId" : 0, "text" : textLeftTop})

		imageMiddleTop = tk.Button(self, command=lambda: self.mapPlanButtonAction(1))
		image = self.makeThumbnail(plansLocations[1])
		image = ImageTk.PhotoImage(image)
		imageMiddleTop.config(image=image)
		imageMiddleTop.image = image
		imageMiddleTop.place(x=600,y=250)
		plan = self.getPlanNameFromLocation(plansLocations[1])
		textMiddleTop = tk.Text(self, height=1, width=20, font=("Helvetica", 18))
		textMiddleTop.insert(tk.END, plan)
		textMiddleTop.place(x=600, y=220)
		self.mapPlanButtons.append({"imageButton" : imageMiddleTop, "planLocation" : plansLocations[1], "buttonId" : 1, "text" : textMiddleTop})

		imageRightTop = tk.Button(self, command=lambda: self.mapPlanButtonAction(2))
		image = self.makeThumbnail(plansLocations[2])
		image = ImageTk.PhotoImage(image)
		imageRightTop.config(image=image)
		imageRightTop.image = image
		imageRightTop.place(x=1000,y=250)
		plan = self.getPlanNameFromLocation(plansLocations[2])
		textRightTop = tk.Text(self, height=1, width=20, font=("Helvetica", 18))
		textRightTop.insert(tk.END, plan)
		textRightTop.place(x=1000, y=220)
		self.mapPlanButtons.append({"imageButton" : imageRightTop, "planLocation" : plansLocations[2], "buttonId" : 2, "text" : textRightTop})


		# self.imageLabel1 = tk.Button(self, command=lambda: self.mapPlanButtonAction("button 1"))
		# image = self.makeThumbnail("./Ascent/ECO\\A Rush.png")
		# image = ImageTk.PhotoImage(image)
		# self.imageLabel1.config(image=image)
		# self.imageLabel1.image = image
		# self.imageLabel1.place(x=200,y=250)

		# self.roundOnText = tk.Text(self, height=1, width=23, font=("Helvetica", 32))

		# self.imageLabel2 = tk.Button(self, command=lambda: self.mapPlanButtonAction("button 2"))
		# image = self.makeThumbnail("./Ascent/ECO\\A Rush.png")
		# image = ImageTk.PhotoImage(image)
		# self.imageLabel2.config(image=image)
		# self.imageLabel2.image = image
		# self.imageLabel2.place(x=600,y=250)

		# self.imageLabel3 = tk.Button(self)
		# image = self.makeThumbnail("./Ascent/ECO\\A Rush.png")
		# image = ImageTk.PhotoImage(image)
		# self.imageLabel3.config(image=image)
		# self.imageLabel3.image = image
		# self.imageLabel3.place(x=1000,y=250)




		# self.imageLabel4 = tk.Button(self)
		# image = self.makeThumbnail("./Ascent/ECO\\A Rush.png")
		# image = ImageTk.PhotoImage(image)
		# self.imageLabel4.config(image=image)
		# self.imageLabel4.image = image
		# self.imageLabel4.place(x=200,y=650)

		# self.imageLabel5 = tk.Button(self)
		# image = self.makeThumbnail("./Ascent/ECO\\A Rush.png")
		# image = ImageTk.PhotoImage(image)
		# self.imageLabel5.config(image=image)
		# self.imageLabel5.image = image
		# self.imageLabel5.place(x=600,y=650)

		# self.imageLabel6 = tk.Button(self)
		# image = self.makeThumbnail("./Ascent/ECO\\A Rush.png")
		# image = ImageTk.PhotoImage(image)
		# self.imageLabel6.config(image=image)
		# self.imageLabel6.image = image
		# self.imageLabel6.place(x=1000,y=650)
		


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
		print("button" + str(buttonId))	

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
