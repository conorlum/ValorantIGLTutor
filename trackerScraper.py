import pyautogui
import time
import json
import os
import shutil







def clickAndSaveRound(roundCount, filenamePrefix):
	pyautogui.click()
	pyautogui.keyDown('ctrl')
	pyautogui.press('s')
	pyautogui.keyUp('ctrl')

	time.sleep(2)

	pyautogui.press('backspace')
	pyautogui.write(filenamePrefix + f"-Round{roundCount}")
	pyautogui.press('enter')
	time.sleep(10)

def moveOneRoundOver():
	pyautogui.moveRel(64,0)

def parseOutRoundCount(filename):
	file = open(f"C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}.html")
	content = file.readlines()
	html = content[145]
	return html.count("cursor-pointer flex flex-col gap-3 items-center px-4 bg-white/10 py-2")

def saveAllRounds(filename):
	roundCountTotal = parseOutRoundCount(filename)
	TotalRoundIndex = 1
	while roundCountTotal > 0:
		if roundCountTotal > 20:
			roundIndexTotal = 20
		else:
			roundIndexTotal = roundCountTotal + 1

		roundCountTotal -= roundIndexTotal

		print("Move mouse onto start loop round")
		input()

		print("looping for: " + str(roundIndexTotal))
		for roundIndex in range(0,roundIndexTotal):
			clickAndSaveRound(roundIndex + TotalRoundIndex, filename)
			moveOneRoundOver()

		TotalRoundIndex += roundIndexTotal

def saveHTMLToJson(filename):
	roundCountTotal = parseOutRoundCount(filename)
	roundHTMLJson = {}
	for i in range(0, roundCountTotal + 1):
		roundIndexStr = str(i+1)
		filePath = f"C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndexStr}.html"
		with open(filePath, 'r') as file:
			content = file.readlines()
			html = content[145]
			roundHTMLJson[str(i+1)] = html

	filePath = f"C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\TrackerHTMLJsons\\{filename}.json"
	with open(filePath, 'w') as file:
		json.dump(roundHTMLJson, file, indent=4)

def removeHTMLfiles(filename):
	roundCountTotal = parseOutRoundCount(filename)

	try:
		directory = f"C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}_files"
		shutil.rmtree(directory)
		print(f"Successfully removed the directory: {directory}")
		os.remove(f"C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}.html")
		print(f"Successfully removed the html file")
	except Exception as e:
		print(f"Error removing the directory: {e}")

	for i in range(0, roundCountTotal+1):
		roundIndex = str(i+1)
		try:
			directory = f"C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndex}_files"
			shutil.rmtree(directory)
			print(f"Successfully removed the directory: {directory}")
			os.remove(f"C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndex}.html")
			print(f"Successfully removed the html file")
		except Exception as e:
			print(f"Error removing the directory: {e}")

def loadHTMLSFromJson(filename):
	htmls = {}
	with open(f"C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\TrackerHTMLJsons\\{filename}.json", 'r') as file:
		htmls = json.load(file)

	return htmls

def parseEconPerRound(filename):
	htmls = loadHTMLSFromJson(filename)

	roundEcons = {}

	for roundIndex in htmls.keys():
		html = htmls[str(roundIndex)]
		roundMarker = html.split("cursor-pointer flex flex-col gap-3 items-center px-4 bg-white/20 py-3")[1]

		econTeam1Split = roundMarker.split('"bg-valorant-team-1 w-3\" style=\"height: ')[1]
		team1EconString = econTeam1Split.split("px")[0]
		team1EconAdjusted = round(float(team1EconString) * .625 * 1000)



		econTeam2Split = roundMarker.split('"bg-valorant-team-2 w-3\" style=\"height: ')[1]
		team2EconString = econTeam2Split.split("px")[0]
		team2EconAdjusted = round(float(team2EconString) * .625 * 1000)

		roundEcons[roundIndex] = {"Team1" : team1EconAdjusted, "Team2" : team2EconAdjusted}
		

	return roundEcons

def parseRoundOutcome(filename):
	htmls = loadHTMLSFromJson(filename)

	roundOutcomes = {}

	for roundIndex in htmls.keys():
		html = htmls[str(roundIndex)]
		roundMarker = html.split("cursor-pointer flex flex-col gap-3 items-center px-4 bg-white/20 py-3")[1]

		roundOutcomeSplit = roundMarker.split('alt=')[1]
		roundOutcomeString = roundOutcomeSplit.split('width')[0].replace('"', '').strip()
		roundOutcomes[str(roundIndex)] = roundOutcomeString

	return roundOutcomes


def parseRoundKillList(filename):
	# need to consider sage clove and kayo res.  pheonix ult does not show up in the kill logs.  
	# thinking that the "res" will show up as a second death or later kill for that specific image. 
	# the res can go unknown if not shown in log, but in this case had little affect on the round.
	htmls = loadHTMLSFromJson(filename)

	# figure this out 
	roundKillLogs = {}

	for roundIndex in htmls.keys():
		html = htmls[str(roundIndex)]

		roundMarker = html.split("Event Log")[1]
		logMarkers = roundMarker.split("cursor-pointer flex flex-row items-center")

		logMarkers = logMarkers[1:]

		killLog = []
		for logMarker in logMarkers:
			if "Planted" not in logMarker and "Exploded" not in logMarker and "Defused" not in logMarker:


				classMarkers = logMarker.split("class")
				killerTeam = classMarkers[1].split("valorant-")[1][:6]
				killerCharacter = classMarkers[2].split("displayicon")[1][1]
				
				try:
					deathTeam = classMarkers[-3].split("valorant-")[1][:6]
					deathCharacter = classMarkers[-2].split("displayicon")[1][1]
				except Exception as e:
					try:
						deathTeam = classMarkers[8].split("valorant-")[1][:6]
						deathCharacter = classMarkers[9].split("displayicon")[1][1]
					except Exception as e:
						try:
							deathTeam = classMarkers[7].split("valorant-")[1][:6]
							deathCharacter = classMarkers[8].split("displayicon")[1][1]
						except Exception as e:
							print(classMarkers)
							print(e)
				killerCharacter = 0 if killerCharacter == 'p' else killerCharacter
				deathCharacter = 0 if deathCharacter == 'p' else deathCharacter

				killLog.append({"killerTeam" : killerTeam, "killerCharacter" : killerCharacter, "deathTeam" : deathTeam, "deathCharacter" : deathCharacter})
			else:
				team = classMarkers[1].split("valorant-")[1][:6]
				character = classMarkers[2].split("displayicon")[1][1]
				character = 0 if character == 'p' else character

			if "Planted" in logMarker:
				killLog.append({"Team" : team, "Character" : character, "Planted" : True})

			if "Exploded" in logMarker:
				killLog.append({"Team" : team, "Character" : character, "Exploded" : True})

			if "Defused" in logMarker:
				killLog.append({"Team" : team, "Character" : character, "Defused" : True})

		roundKillLogs[roundIndex] = killLog

	return roundKillLogs

if __name__ == "__main__":
	print("Starting the scraping")
	print("Open the match in a new window on the main screen")
	print("Save the round overview for the first round and name it with the structure MapDDMMYYHMM")

	filename = input("Please enter the map followed by date month year and time\n")

	# saveAllRounds(filename)
	# saveHTMLToJson(filename)
	# removeHTMLfiles(filename)

	parseEconPerRound(filename)
	parseRoundOutcome(filename)
	parseRoundKillList(filename)
	

	




	