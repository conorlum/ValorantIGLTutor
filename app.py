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
		
		self.setRootVariables()
		

		self.generateMapPickerScreen()
		
	def setRootVariables(self):
		self.round = 1
		self.rounds = []
		self.roundPlanTypes = ["Pistol", "ECO", "Full Buy"]
		self.roundPlanType = 0
		self.PISTOL = 0
		self.ECO = 1
		self.FULLBUY = 2
		self.mapName = ""
		self.isDefense = False
		self.isAttack = False
		self.overTime = False

	def resetRoot(self):
		for widget in self.winfo_children():
			widget.destroy()

	def generateMapPickerScreen(self):
		self.tableTopText = tk.Text(self, height=1, width=11, font=("Helvetica", 32))
		self.tableTopText.insert(tk.END, "Pick the map")
		self.tableTopText.place(x=650, y=0)

		mapNamesToCoordinates = {
		"Abyss" : (50, 150), 
		"Ascent" : (400, 150), 
		"Bind" : (750, 150), 
		"Breeze" : (1100, 150),
		"Fracture" : (50, 450),
		"Haven" : (400, 450),
		"Icebox" : (750, 450),
		"Lotus" : (1100, 450),
		"Pearl" : (50, 750),
		"Split" : (400, 750),
		"Sunset" : (750, 750)
		}

		mapNameToButton = {}

		for key in mapNamesToCoordinates.keys():
			response = self.generateMapButton(key, mapNamesToCoordinates[key])
			mapNameToButton.update(response)


	def generateMapButton(self, mapName, coordinates):
		mapImagesLocations = glob.glob("./mapThumbnails/*")
		mapButton = tk.Button(self, command=lambda: self.mapSelectionButtonAction(mapName))
		mapLocation = ""
		for location in mapImagesLocations:
			if mapName in location:
				mapLocation = location

		image = self.makeMapSelectionImage(mapLocation)
		image = ImageTk.PhotoImage(image)
		mapButton.config(image=image)
		mapButton.image = image
		mapButton.place(x=coordinates[0],y=coordinates[1])

		return {mapName : mapButton}


	def makeMapSelectionImage(self, location):
		image = PIL.Image.open(location)
		image = image.resize((300,200))
		return image
		
	def mapSelectionButtonAction(self, mapName):
		self.mapName = mapName
		self.resetRoot()
		self.generateAttackDefensePickerScreen()

	def generateAttackDefensePickerScreen(self):
		self.attackButton = tk.Button(self, text="ATTACK", font=("Helvetica", 32), command=self.attackButtonAction)
		self.attackButton.config(height=22, width=30, bg="#fa4d39")
		self.attackButton.place(x=0, y=0)


		self.defenseButton = tk.Button(self, text="DEFENSE", font=("Helvetica", 32), command=self.defenseButtonAction)
		self.defenseButton.config(height=22, width=30, bg="#02f7b6")
		self.defenseButton.place(x=750, y=0)


	def attackButtonAction(self):
		self.isAttack = True
		self.isDefense = False
		self.resetRoot()
		self.generateMapPlanPickerScreen()

	def defenseButtonAction(self):
		self.isDefense = True
		self.isAttack = False
		self.resetRoot()
		self.generateMapPlanPickerScreen()


	def generateMapPlanPickerScreen(self):
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

		#can add plan type underneath maybe?  chosenText is given and possible to use

		self.roundOnText = tk.Text(self, height=1, width=23, font=("Helvetica", 32))
		self.roundOnText.insert(tk.END, "OUTCOME OF ROUND: " + str(self.round))
		self.roundOnText.place(x=500, y=80)

		self.roundPlanText = tk.Text(self, height=1, width=23, font=("Helvetica", 32))
		self.roundPlanText.insert(tk.END, "Plan for Round: " + str(self.round) + "  " + self.roundPlanTypes[self.roundPlanType])
		self.roundPlanText.place(x=500, y=150)

		self.roundWinButton = tk.Button(self, text="Round Win", command=lambda: self.endOfRoundOutcomeButtonAction("W"))
		self.roundWinButton.config(height=3, width=25, bg="green")
		self.roundWinButton.place(x=200, y=80)

		self.roundLossButton = tk.Button(self, text="Round Loss", command=lambda: self.endOfRoundOutcomeButtonAction("L"))
		self.roundLossButton.config(height=3, width=25, bg="red")
		self.roundLossButton.place(x=1200, y=80)

		self.roundTypeCycleButton = tk.Button(self, text="Plan Type Cycle", command=self.roundTypeCycleButtonAction)
		self.roundTypeCycleButton.config(height=3, width=25, bg="yellow")
		self.roundTypeCycleButton.place(x=1100, y=150)

		self.roundTypeCycleButton = tk.Button(self, text="Change Plan", command=self.changePlanButtonAction)
		self.roundTypeCycleButton.config(height=3, width=25, bg="orange")
		self.roundTypeCycleButton.place(x=1300, y=150)

		self.backToMapSelectorButton = tk.Button(self, text="Back To Map Selector", command=self.backToMapSelector)
		self.backToMapSelectorButton.config(height=3, width=25, bg="purple")
		self.backToMapSelectorButton.place(x=50, y=150)

		self.generateMapPlanButtons()

	
	def generateMapPlanButtons(self): #maybe rewrite this to use a function seems like it works?
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
		location = "mapPlans/"
		if self.isAttack:
			location += "Attack/"
		else:
			location += "Defense/"
		if self.isDefense and roundType == self.roundPlanTypes[0]:
			roundType = self.roundPlanTypes[2]
		location += self.mapName + "/" + roundType + "/*.png"
		files = glob.glob(location)
		return files

	def getGoodPlans(self):
		plans = self.getPossiblePlans()
		if len(plans) == 3:
			return plans
		if len(plans) == 2:
			plans.append(plans[0])
			return plans
		if len(plans) == 1:
			plans.append(plans[0])
			plans.append(plans[0])
			return plans
		if len(plans) > 3:
			#cool logic later?
			return plans[:3]

	def getDefaultPlans(self):
		location = "mapPlans/"
		if self.isAttack:
			location += "Attack/"
		else:
			location += "Defense/"
		location += self.mapName + "/Default/*.png"
		if self.isDefense:
			location = location.replace("Default", "Full Buy")
		files = glob.glob(location)
		return files


	def getPlanNameFromLocation(self, location):
		return location.split("\\")[-1].split(".")[0]

	def mapPlanButtonAction(self, buttonId):
		self.removeMapPlanButtons()

		buttonElement = self.mapPlanButtons[buttonId]
		image = PIL.Image.open(buttonElement["planLocation"])
		image = image.resize((1320,773))
		image = image.crop((250,0,1070,773))
		image = ImageTk.PhotoImage(image)
		self.chosenPlan = tk.Label(self, image=image, text=buttonElement["text"], compound="bottom", font=("Helvetica", 32))
		self.chosenPlan.image = image
		self.chosenPlan.text = buttonElement["text"]
		self.chosenPlan.place(x=600, y=250)

		self.setupCommsLabel = tk.Label(self, text="Pre Round Comms:", compound="bottom", font=("Helvetica", 32))
		self.setupCommsLabel.text = "Pre Round Comms:"
		self.setupCommsLabel.place(x=75, y=250)

		textLocation = buttonElement["planLocation"].replace("png", "txt")
		setupCommsText = ""
		with open(textLocation) as file:
			setupCommsText = file.read()

		self.chosenPlanSetupCommsText = tk.Text(self, height=20, width=25, font=("Helvetica", 24))
		self.chosenPlanSetupCommsText.insert(tk.END, setupCommsText)
		self.chosenPlanSetupCommsText.place(x=75, y=300)




	def backToMapSelector(self):
		self.resetRoot()
		self.generateMapPickerScreen()
		self.setRootVariables()
		

	def removeMapPlanButtons(self):
		for button in self.mapPlanButtons:
			button["imageButtonElement"].destroy()
			button["textElement"].destroy()


	def changePlanButtonAction(self):
		self.refreshMapPlanButtons()
 
	def makeThumbnail(self, file_location):
		image = PIL.Image.open(file_location)
		image = image.resize((1320,773))
		image = image.crop((250,0,1070,773))
		image = image.resize((350,350))
		return image

	def changeSides(self):
		if self.isAttack:
			self.isDefense = True
			self.isAttack = False
		else:
			self.isAttack = True
			self.isDefense = True

	def endOfRoundOutcomeButtonAction(self, outcome):
		background = "red"
		if outcome == "W":
			background = "green"
		tableOutcomeText = self.tableOutcomeTexts[self.round-1]
		tableOutcomeText.config(bg=background)
		self.round += 1
		self.rounds.append({"roundType" : self.roundPlanType, "planText" : self.chosenPlan.text, "outcome" : outcome})

		if self.round == 13:
			self.changeSides()

		if self.overTime:
			self.changeSides()

		if self.round == 25:
			self.generateAttackDefensePickerScreen()
			self.overTime = True
			return

		self.roundPlanTypeOutcomeLogic()
		self.refreshRoundOnText()
		self.refreshPlanText()
		self.refreshMapPlanButtons()


	def roundPlanTypeOutcomeLogic(self):
		if self.overTime:
			self.roundPlanType = self.FULLBUY
			return

		roundsIndex = self.round - 2
		self.roundPlanType = self.ECO

		if self.rounds[roundsIndex]["roundType"] == self.FULLBUY and self.rounds[roundsIndex]["outcome"] == "W":
			self.roundPlanType = self.FULLBUY

		if self.rounds[roundsIndex]["roundType"] == self.ECO:
			self.roundPlanType = self.FULLBUY

		roundModIndex = 12 if self.round > 12 else 0

		if self.round % 12 == 1:
			self.roundPlanType = self.PISTOL

		if self.round % 12 == 2:
			if self.rounds[roundModIndex]["outcome"] == "W":
				self.roundPlanType = self.FULLBUY
			else:
				self.roundPlanType = self.ECO
		if self.round % 12 == 3:
			if self.rounds[roundModIndex]["outcome"] == "W":
				self.roundPlanType = self.ECO
			else:
				self.roundPlanType = self.FULLBUY
		if self.round % 12 == 4:
			if self.rounds[roundModIndex]["outcome"] == "W":
				self.roundPlanType = self.FULLBUY
			elif self.rounds[roundsIndex]["outcome"] == "W":
				self.roundPlanType = self.FULLBUY
			else:
				self.roundPlanType = self.ECO

		


	def roundTypeCycleButtonAction(self):
		
		if self.roundPlanType == self.ECO:
			self.roundPlanType = self.FULLBUY
		else:
			self.roundPlanType = self.ECO

		if self.round % 12 == 1:
			self.roundPlanType = self.PISTOL
		self.refreshPlanText()
		self.refreshMapPlanButtons()

	def refreshMapPlanButtons(self):
		self.removeMapPlanButtons()
		try:
			self.chosenPlan.destroy()
			self.setupCommsLabel.destroy()
			self.chosenPlanSetupCommsText.destroy()
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
