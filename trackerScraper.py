import pyautogui
import time
import json
import os
import shutil
from PIL import Image
import imagehash
import glob






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
	pyautogui.moveRel(96,0)

def parseOutRoundCount(filename):
	file = open(f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}.html")
	content = file.readlines()
	html = content[165]
	return html.count("text-12 font-medium text-dim")

def saveAllRounds(filename):
	roundCountTotal = parseOutRoundCount(filename)
	print(roundCountTotal)
	TotalRoundIndex = 1
	while roundCountTotal > 0:
		if roundCountTotal > 20:
			roundIndexTotal = 20
		else:
			roundIndexTotal = roundCountTotal + 1

		roundCountTotal -= roundIndexTotal + 1

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
	for i in range(0, roundCountTotal):
		roundIndexStr = str(i+1)
		filePath = f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndexStr}.html"
		with open(filePath, 'r') as file:
			content = file.readlines()
			html = content[165]
			roundHTMLJson[str(i+1)] = html

	filePath = f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerHTMLJsons\\{filename}.json"
	with open(filePath, 'w') as file:
		json.dump(roundHTMLJson, file, indent=4)

def removeHTMLfiles(filename):
	roundCountTotal = parseOutRoundCount(filename)

	try:
		directory = f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}_files"
		shutil.rmtree(directory)
		print(f"Successfully removed the directory: {directory}")
		os.remove(f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}.html")
		print(f"Successfully removed the html file")
	except Exception as e:
		print(f"Error removing the directory: {e}")

	for i in range(0, roundCountTotal):
		roundIndex = str(i+1)
		try:
			directory = f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndex}_files"
			shutil.rmtree(directory)
			print(f"Successfully removed the directory: {directory}")
			os.remove(f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndex}.html")
			print(f"Successfully removed the html file")
		except Exception as e:
			print(f"Error removing the directory: {e}")

def loadHTMLSFromJson(filename):
	htmls = {}
	with open(f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerHTMLJsons\\{filename}.json", 'r') as file:
		htmls = json.load(file)

	return htmls

def parseEconPerRound(filename):
	htmls = loadHTMLSFromJson(filename)

	roundEcons = {}

	for roundIndex in htmls.keys():
		html = htmls[str(roundIndex)]
		roundMarker = html.split(f"text-12 font-medium text-dim\">{roundIndex}<")[1]

		econTeam1Split = roundMarker.split('"w-3 bg-valorant-team-1\" style=\"height: ')[1]
		team1EconString = econTeam1Split.split("px")[0]
		team1EconAdjusted = round(float(team1EconString) * .625 * 1000)



		econTeam2Split = roundMarker.split('"w-3 bg-valorant-team-2\" style=\"height: ')[1]
		team2EconString = econTeam2Split.split("px")[0]
		team2EconAdjusted = round(float(team2EconString) * .625 * 1000)

		roundEcons[roundIndex] = {"Team1" : team1EconAdjusted, "Team2" : team2EconAdjusted}
		

	return roundEcons

def parseRoundOutcome(filename):
	htmls = loadHTMLSFromJson(filename)

	roundOutcomes = {}

	for roundIndex in htmls.keys():
		html = htmls[str(roundIndex)]
		roundMarker = html.split(f"text-12 font-medium text-dim\">{roundIndex}<")[1]

		roundOutcomeSplit = roundMarker.split('alt=')[1]
		roundOutcomeString = roundOutcomeSplit.split('width')[0].replace('"', '').strip()
		roundOutcomes[str(roundIndex)] = roundOutcomeString

	return roundOutcomes

def agentDisplayIconLookup(displayiconNumber, roundIndex, filename):

	png_files = glob.glob("C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\agentDisplayIconPictureReferences\\*.png")
	if displayiconNumber == 0:
		displayiconNumber = ""
	else:
		displayiconNumber = f"({displayiconNumber})"
	# print(f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndex}_files\\displayicon{displayiconNumber}.png")
	hash1 = imagehash.average_hash(Image.open(f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndex}_files\\displayicon{displayiconNumber}.png"))
	best_png = ""
	best_hash = 2147483647

	for png in png_files:
	
		# print(png)
		hash2 = imagehash.average_hash(Image.open(png))

		distance = abs(hash1 - hash2)
		if distance < best_hash:
			best_hash = distance
			best_png = png

	if best_hash > 5:
		return "BAD CLASSIFICATION!"

	return best_png.split("agentDisplayIconPictureReferences\\")[1].split(".png")[0]

def weaponNewImageLookup(newImageNumber, roundIndex, filename):

	png_files = glob.glob("C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\weaponNewImagePictureReferences\\*.png")
	# print(f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndex}_files\\displayicon{newImageNumber}.png")
	hash1 = imagehash.average_hash(Image.open(f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndex}_files\\newimage{newImageNumber}.png"))
	best_png = ""
	best_hash = 2147483647

	for png in png_files:
	
		# print(png)
		hash2 = imagehash.average_hash(Image.open(png))

		distance = abs(hash1 - hash2)
		if distance < best_hash:
			best_hash = distance
			best_png = png

	if best_hash > 5:
		return "BAD CLASSIFICATION!"
	return best_png.split("weaponNewImagePictureReferences\\")[1].split(".png")[0]


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
		logMarkers = roundMarker.split("space-between flex cursor-pointer flex-row items-center")

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


				killerCharacter = agentDisplayIconLookup(killerCharacter, roundIndex, filename)
				deathCharacter = agentDisplayIconLookup(deathCharacter, roundIndex, filename)

				if killerTeam == deathTeam:
					killWeapon = "Friendly"
				elif "newimage" not in logMarker:
					killWeapon = "Environmental"
				else:
					killWeapon = logMarker.split("newimage")[1].split(".png")[0]
					killWeapon = weaponNewImageLookup(killWeapon, roundIndex, filename)


				killLog.append({"killerTeam" : killerTeam, "killerCharacter" : killerCharacter, "deathTeam" : deathTeam, "deathCharacter" : deathCharacter, "killWeapon" : killWeapon})
			else:
				team = classMarkers[1].split("valorant-")[1][:6]
				character = classMarkers[2].split("displayicon")[1][1]
				character = 0 if character == 'p' else character
				character = agentDisplayIconLookup(character, roundIndex, filename)

			if "Planted" in logMarker:
				killLog.append({"Team" : team, "Character" : character, "Planted" : True})

			if "Exploded" in logMarker:
				killLog.append({"Team" : team, "Character" : character, "Exploded" : True})

			if "Defused" in logMarker:
				killLog.append({"Team" : team, "Character" : character, "Defused" : True})

		roundKillLogs[roundIndex] = killLog

	return roundKillLogs


def parseTeamPlayers(filename):
	htmls = loadHTMLSFromJson(filename)
	round1 = htmls["1"]
	usernames = round1.split("trn-ign__username fit-long-username")
	playerUsernamesToAgent = {}
	for usernameIndex in range(0,len(usernames)-1):
		username = usernames[usernameIndex+1]
		playerAgent = usernames[usernameIndex]
		if (username[2:].split("<")[0]) == "":
			continue


		if usernameIndex == 0:
			agent = playerAgent.split("alt=")[-1][1:].split("\"")[0]
		else:
			agent = playerAgent.split("alt=")[1][1:].split("\"")[0]
		playerUsernamesToAgent[(username[2:].split("<")[0])] = {"Agent" : agent}

	return playerUsernamesToAgent
	

def parsePlayerRoundInfo(filename):
	htmls = loadHTMLSFromJson(filename)

	playerUsernamesToAgent = parseTeamPlayers(filename)

	for roundIndex in htmls.keys():
		html = htmls[str(roundIndex)]
		players = html.split("trn-ign__username fit-long-username")

		for player in players:
			username = (player[2:].split("<")[0])
			score = int(player.split("st__item st-content__item-value st-content__item-value--active st__item--align-center")[1].split("value\">")[1].split("<")[0])
			kills = int(player.split("st__item st-content__item-value st-content__item-value--active st__item--align-center")[1].split("value\">")[2].split("<")[0])
			deaths = int(player.split("st__item st-content__item-value st-content__item-value--active st__item--align-center")[1].split("value\">")[3].split("<")[0])
			assists = int(player.split("st__item st-content__item-value st-content__item-value--active st__item--align-center")[1].split("value\">")[4].split("<")[0])

			playerData = playerUsernamesToAgent[username]
			roundPlayerData = {}
			playerData["score"] = score
			playerData["kills"] = kills
			playerData["deaths"] = deaths
			playerData["assists"] = assists




if __name__ == "__main__":
	print("Starting the scraping")
	print("Open the match in a new window on the main screen")
	print("Save the round overview for the first round as a single file mhtml and name it with the structure MapDDMMYYHMM")

	filename = input("Please enter the map followed by date month year and time\n")

	# saveAllRounds(filename)
	# saveHTMLToJson(filename)
	# removeHTMLfiles(filename)

	# print(parseEconPerRound(filename))
	# print(parseRoundOutcome(filename))
	# print(parseRoundKillList(filename)["2"])
	# print(parseRoundKillList(filename)["23"])

	parseTeamPlayers(filename)
	

	




	