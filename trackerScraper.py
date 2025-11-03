import pyautogui
import time
import json
import os
import shutil
from PIL import Image
import imagehash
import glob
import shutil
from pathlib import Path
import networkx as nx

User = "conor" #or User
baseLocation = f"C:\\Users\\{User}\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\"



def createMapFolder(filename):
	path = os.path.join(baseLocation, filename + "_ALL_FILES")

	# Create the folder
	os.makedirs(path, exist_ok=True)

def clickAndSaveRound(roundCount, filenamePrefix):
	pyautogui.click()
	pyautogui.keyDown('ctrl')
	pyautogui.press('s')
	pyautogui.keyUp('ctrl')

	time.sleep(2)

	pyautogui.press('backspace')
	time.sleep(3)
	filename = filenamePrefix + f"-Round{roundCount}"
	pyautogui.write(filename)
	time.sleep(3)
	pyautogui.press('enter')
	time.sleep(5)

	while checkFileExists(filenamePrefix, filename) is False:
		print("waiting")
		time.sleep(10)

def checkFileExists(filenamePrefix, filename):
	path = f"{baseLocation}{filenamePrefix}_ALL_FILES\\"
	pattern = os.path.join(path, f"*{filename}*")
	print(pattern)
	print(glob.glob(pattern))
	return bool(glob.glob(pattern))


def moveOneRoundOver():
	resolutionScaling = 1 #1.5 when on 4k
	pyautogui.moveRel(64 * resolutionScaling,0)

def parseOutRoundCount(filename):
	html = ""

	nextLine = False
	with open(f"{baseLocation}{filename}_ALL_FILES\\{filename}.html", "r", encoding="utf-8") as file:
		for line in file:

			if nextLine:
				html = line
				nextLine = False
				break
			if "<body>" in line:
				nextLine = True


	return html.count("text-12 font-medium text-dim")

def saveAllRounds(filename):
	roundCountTotal = parseOutRoundCount(filename)
	TotalRoundIndex = 1
	while roundCountTotal > 0:
		if roundCountTotal >= 20:
			roundIndexTotal = 20
			roundCountTotal -= 20
		else:
			roundIndexTotal = roundCountTotal
			roundCountTotal = 0

		print("Move mouse onto start loop round")
		input()

		print("looping for: " + str(roundIndexTotal))
		for roundIndex in range(0,roundIndexTotal):
			clickAndSaveRound(roundIndex + TotalRoundIndex, filename)
			moveOneRoundOver()

		TotalRoundIndex += roundIndexTotal


def cleanUpFiles(filename):

	path = os.path.join(baseLocation, filename + "_ALL_FILES")

	# Create the folder
	os.makedirs(path, exist_ok=True)

	files = glob.glob(f"{baseLocation}{filename}*")

	prefix = Path(path + "\\")
	
	for file in files:
		if "ALL_FILES" in file:
			continue
		dst = str(prefix) +"\\" + file.split("TrackerPages\\")[1]
		shutil.move(str(file), str(dst))



def saveHTMLToJson(filename):
	roundCountTotal = parseOutRoundCount(filename)
	roundHTMLJson = {}
	for i in range(0, roundCountTotal):
		roundIndexStr = str(i+1)
		filePath = f"{baseLocation}{filename}_ALL_FILES\\{filename}-Round{roundIndexStr}.html"
		with open(filePath, 'r') as file:
			nextLine = False
			for line in file:

				if nextLine:
					html = line
					nextLine = False
					break
				if "<body>" in line:
					nextLine = True
			
			roundHTMLJson[str(i+1)] = html

	filePath = f"C:\\Users\\{User}\\Documents\\GitHub\\ValorantIGLTutor\\TrackerHTMLJsons\\{filename}.json"
	with open(filePath, 'w') as file:
		json.dump(roundHTMLJson, file, indent=4)

# def removeHTMLfiles(filename):
# 	roundCountTotal = parseOutRoundCount(filename)

# 	try:
# 		directory = f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}_files"
# 		shutil.rmtree(directory)
# 		print(f"Successfully removed the directory: {directory}")
# 		os.remove(f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}.html")
# 		print(f"Successfully removed the html file")
# 	except Exception as e:
# 		print(f"Error removing the directory: {e}")

# 	for i in range(0, roundCountTotal):
# 		roundIndex = str(i+1)
# 		try:
# 			directory = f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndex}_files"
# 			shutil.rmtree(directory)
# 			print(f"Successfully removed the directory: {directory}")
# 			os.remove(f"C:\\Users\\User\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndex}.html")
# 			print(f"Successfully removed the html file")
# 		except Exception as e:
# 			print(f"Error removing the directory: {e}")

def loadHTMLSFromJson(filename):
	htmls = {}
	with open(f"C:\\Users\\{User}\\Documents\\GitHub\\ValorantIGLTutor\\TrackerHTMLJsons\\{filename}.json", 'r') as file:
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

	png_files = glob.glob(f"C:\\Users\\{User}\\Documents\\GitHub\\ValorantIGLTutor\\agentDisplayIconPictureReferences\\*.png")
	hash1 = imagehash.average_hash(Image.open(f"{baseLocation}{filename}_ALL_FILES\\{filename}-Round{roundIndex}_files\\displayicon{displayiconNumber}.png"))
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

	png_files = glob.glob("C:\\Users\\{User}\\Documents\\GitHub\\ValorantIGLTutor\\weaponNewImagePictureReferences\\*.png")
	hash1 = imagehash.average_hash(Image.open(f"{baseLocation}{filename}_ALL_FILES\\{filename}-Round{roundIndex}_files\\newimage{newImageNumber}.png"))
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


def convertTime(stringTime):
	return int(stringTime[0])*60 + int(stringTime[2:])

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

		team1ACSBonus = 150
		team2ACSBonus = 150

		for logMarker in logMarkers:

			eventTime = convertTime(logMarker.split("text-16 font-medium leading-3/4\">")[1].split("<")[0])


			if "Planted" not in logMarker and "Exploded" not in logMarker and "Defused" not in logMarker:


				classMarkers = logMarker.split("class")
				killerTeam = classMarkers[1].split("valorant-")[1][:6]

				killerCharacter = classMarkers[2].split("displayicon")[1].split(".png")[0]

				try:
					deathTeam = classMarkers[-3].split("valorant-")[1][:6]
					deathCharacter = classMarkers[-2].split("displayicon")[1].split(".png")[0]
				except Exception as e:
					try:
						deathTeam = classMarkers[8].split("valorant-")[1][:6]
						deathCharacter = classMarkers[9].split("displayicon")[1].split(".png")[0]
					except Exception as e:
						try:
							deathTeam = classMarkers[7].split("valorant-")[1][:6]
							deathCharacter = classMarkers[8].split("displayicon")[1].split(".png")[0]
						except Exception as e:
							print(classMarkers)
							print(e)


				killerCharacter = agentDisplayIconLookup(killerCharacter, roundIndex, filename)
				deathCharacter = agentDisplayIconLookup(deathCharacter, roundIndex, filename)

				if killerTeam == deathTeam:
					killWeapon = "Friendly"
				elif "newimage" not in logMarker:
					killWeapon = "Environmental"
				else:
					killWeapon = logMarker.split("newimage")[1].split(".png")[0]
					killWeapon = weaponNewImageLookup(killWeapon, roundIndex, filename)

				

				ACSBonus = team1ACSBonus if killerTeam == "team-1" else team2ACSBonus

				killLog.append({"killerTeam" : killerTeam, "killerCharacter" : killerCharacter, "deathTeam" : deathTeam, "deathCharacter" : deathCharacter, "killWeapon" : killWeapon, "eventTime" : eventTime, "Event" : "Kill", "ACS_Bonus" : ACSBonus})

				if killerTeam == "team-1":
					team1ACSBonus -= 20
				else:
					team2ACSBonus -= 20
			else:
				team = classMarkers[1].split("valorant-")[1][:6]
				character = classMarkers[2].split("displayicon")[1].split(".png")[0]
				character = 0 if character == 'p' else character
				character = agentDisplayIconLookup(character, roundIndex, filename)

			if "Planted" in logMarker:
				killLog.append({"Team" : team, "Character" : character, "Event" : "Planted", "eventTime" : eventTime})

			if "Exploded" in logMarker:
				killLog.append({"Team" : team, "Character" : character, "Event" : "Exploded", "eventTime" : eventTime})

			if "Defused" in logMarker:
				killLog.append({"Team" : team, "Character" : character, "Event" : "Defused", "eventTime" : eventTime})

		roundKillLogs[roundIndex] = killLog

	return roundKillLogs


def parseTeamPlayers(filename):
	htmls = loadHTMLSFromJson(filename)
	round1 = htmls["1"]
	playerLogRecords = round1.split("st-custom-name st-entry-party st-entry")
	playerUsernamesToAgent = {}

	teamCount = 0
	team = "team-1"

	for playerLogIndex in range(0,10):
		playerLogRecord = playerLogRecords[playerLogIndex+1]
		playerAgent = playerLogRecord.split("alt=\"")[1].split("\"")[0]

		username = playerLogRecord.split("trn-ign__username fit-long-username\">")[1].split("<")[0]


		playerUsernamesToAgent[username] = {"Agent" : playerAgent, "Team" : team, "RoundInfo" : []}

		teamCount += 1
		if teamCount == 5:
			team = "team-2"

	return playerUsernamesToAgent
	

def parsePlayerRoundInfo(filename):
	htmls = loadHTMLSFromJson(filename)

	playerUsernamesToAgent = parseTeamPlayers(filename)

	for roundIndex in htmls.keys():
		html = htmls[str(roundIndex)]
		players = html.split("trn-ign__username fit-long-username")

		
		for player in players:
			if "st__item st-content__item-value st-content__item-value--active st__item--align-center" in player:
				username = (player[2:].split("<")[0])
				commaScore = player.split("st__item st-content__item-value st-content__item-value--active st__item--align-center")[1].split("value\">")[1].split("<")[0]
				score = int(commaScore.replace(",", ""))
				kills = int(player.split("st__item st-content__item-value st-content__item-value--active st__item--align-center")[1].split("value\">")[2].split("<")[0])
				deaths = int(player.split("st__item st-content__item-value st-content__item-value--active st__item--align-center")[1].split("value\">")[3].split("<")[0])
				assists = int(player.split("st__item st-content__item-value st-content__item-value--active st__item--align-center")[1].split("value\">")[4].split("<")[0])
				commaLoadout= player.split("st__item st-content__item-value st-content__item-value--active st__item--align-center")[1].split("value\">")[5].split("<")[0]
				commaRemaining = player.split("st__item st-content__item-value st-content__item-value--active st__item--align-center")[1].split("value\">")[5].split("label\">")[1].split("<")[0]
				loadout = int(commaLoadout.replace(",", ""))
				remaining = int(commaRemaining.replace(",", ""))

				roundPlayerData = {}
				roundPlayerData["Score"] = score
				roundPlayerData["Kills"] = kills
				roundPlayerData["Deaths"] = deaths
				roundPlayerData["Assists"] = assists
				roundPlayerData["Loadout"] = loadout
				roundPlayerData["Remaining"] = remaining
				playerUsernamesToAgent[username]["RoundInfo"].append(roundPlayerData)

	return playerUsernamesToAgent


def measureOutgoingImpact(filename):

	htmls = loadHTMLSFromJson(filename)

	playersRoundInfo = parsePlayerRoundInfo(filename)
	# print(playersRoundInfo)

	roundKillLogs = parseRoundKillList(filename)
	roundKillLogs = calculateEconDifferential(playersRoundInfo, roundKillLogs)
	roundKillLogs = calculateKillOrderBonuses(roundKillLogs)
	

	playersRoundInfo = calculateDamageAndAssists_KillOrderSum_KillFactorAverage(playersRoundInfo, roundKillLogs)

	playersRoundInfo = calculateRoundImpact(playersRoundInfo, roundKillLogs)

	displayImpact(playersRoundInfo, True)

def displayImpact(playersRoundInfo, roundInfoBool):
	for username in playersRoundInfo.keys():
		player = playersRoundInfo[username]
		agent = player["Agent"]
		team = player["Team"]

		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		print(username)
		print(agent)
		print(team)
		print("\n\n")

		avgDeathImpact = 0
		avgKillImpact = 0
		avgImpact = 0
		avgACS = 0
		for roundIndex in range(0,len(player["RoundInfo"])):
			if roundInfoBool:
				print("Round " + str(roundIndex+1))
				print(player["RoundInfo"][roundIndex]["ImpactDisplay"])
				print("ACS: " + str(player["RoundInfo"][roundIndex]["Score"]))
				print("\n")
			avgKillImpact += player["RoundInfo"][roundIndex]["killImpact"]
			avgDeathImpact += player["RoundInfo"][roundIndex]["deathImpact"]
			avgImpact += player["RoundInfo"][roundIndex]["Impact"]
			avgACS += player["RoundInfo"][roundIndex]["Score"]

		print("Average Kill Impact: " + str(round(avgKillImpact/len(player["RoundInfo"]))))
		print("Average Death Impact: " + str(round(avgDeathImpact/len(player["RoundInfo"]))))
		print("Average Impact: " + str(round(avgImpact/len(player["RoundInfo"]))))
		print("Average ACS: " + str(round(avgACS/len(player["RoundInfo"]))))
		print("\n\n")


def calculateRoundImpact(playersRoundInfo, roundKillLogs):


	for username in playersRoundInfo.keys():
		player = playersRoundInfo[username]
		agent = player["Agent"]
		team = player["Team"]

		for roundIndex in range(0,len(player["RoundInfo"])):
			ACS = player["RoundInfo"][roundIndex]["Damage+Assists"]
			killOrderBonus = player["RoundInfo"][roundIndex]["killOrderBonusSum"]
			killOrderBonusXEconFactorSum = player["RoundInfo"][roundIndex]["killOrderBonus*EconFactorSum"]
			deathOrderBonusXEconFactorSum = player["RoundInfo"][roundIndex]["deathOrderBonus*EconFactorSum"]
			killFactorAverage = player["RoundInfo"][roundIndex]["EconomyDifferentialFactorAverage"]
			if killFactorAverage == 0:
				killFactorAverage = 1
			ACS_Scalor = 1.25
			damages = round(ACS*killFactorAverage*ACS_Scalor)
			killImpact = round(damages + killOrderBonusXEconFactorSum)

			deathImpact = round(deathOrderBonusXEconFactorSum)
			player["RoundInfo"][roundIndex]["killImpact"] = killImpact
			player["RoundInfo"][roundIndex]["deathImpact"] = deathImpact

			impact = killImpact - deathImpact
			player["RoundInfo"][roundIndex]["Impact"] = impact
			player["RoundInfo"][roundIndex]["ImpactDisplay"] = "Impact: " + str(round(impact)) + "     Breakdown  -->     killImpact: " + str(killImpact) +  "  Damage: " + str(damages) + "   Kill Order: " + str(round(killOrderBonusXEconFactorSum)) + "    Death Order: " + str(round(deathOrderBonusXEconFactorSum)) + "   Econ Factor: " + str(killFactorAverage)

	return playersRoundInfo


def calculateDamageAndAssists_KillOrderSum_KillFactorAverage(playersRoundInfo, roundKillLogs):

	for username in playersRoundInfo.keys():
		player = playersRoundInfo[username]
		agent = player["Agent"]
		team = player["Team"]

		for roundIndex in range(0,len(player["RoundInfo"])):
			ACS = player["RoundInfo"][roundIndex]["Score"]
			killOrderBonus = 0
			killFactorAverage = 0
			killOrderBonusXEconFactorSum = 0
			killsInRound = 0

			for killLog in roundKillLogs[str(roundIndex+1)]:
				
				if killLog["Event"] == "Kill":
					if killLog["killerTeam"] == team and killLog["killerCharacter"] == agent:
						ACS -= killLog["ACS_Bonus"]
						killOrderBonus += killLog["killOrderBonus"]
						killFactorAverage += killLog["EconomyDifferentialFactor"]
						killsInRound += 1
						killOrderBonusXEconFactorSum += killLog["killOrderBonus*EconFactor"]

			player["RoundInfo"][roundIndex]["Damage+Assists"] = ACS
			player["RoundInfo"][roundIndex]["killOrderBonusSum"] = killOrderBonus
			player["RoundInfo"][roundIndex]["killOrderBonus*EconFactorSum"] = killOrderBonusXEconFactorSum

			
			if killsInRound == 0:
				killsInRound = 1
			player["RoundInfo"][roundIndex]["EconomyDifferentialFactorAverage"] = killFactorAverage/killsInRound

		for roundIndex in range(0,len(player["RoundInfo"])):
			deathOrderBonusXEconFactorSum = 0

			for killLog in roundKillLogs[str(roundIndex+1)]:
				
				if killLog["Event"] == "Kill":
					if killLog["deathTeam"] == team and killLog["deathCharacter"] == agent:
						deathOrderBonusXEconFactorSum += killLog["deathOrderBonus*EconFactor"]

			player["RoundInfo"][roundIndex]["deathOrderBonus*EconFactorSum"] = deathOrderBonusXEconFactorSum

	return playersRoundInfo

def calculateKillOrderBonuses(roundKillLogs):
	

	for roundIndex in roundKillLogs.keys():

		team1KillIndex = 5
		team2KillIndex = 5
		killsInRound = 0	
		print(roundIndex)
		for killLog in roundKillLogs[roundIndex]:
			if killLog["Event"] == "Kill":

				killOrderBonus = calculateKillOrderBonus(team1KillIndex, team2KillIndex, killLog["killerTeam"], killsInRound)
				killLog["killOrderBonus"] = killOrderBonus
				killLog["killOrderBonus*EconFactor"] = killOrderBonus * killLog["EconomyDifferentialFactor"]

				killLog["deathOrderBonus"] = killOrderBonus 
				killLog["deathOrderBonus*EconFactor"] = killOrderBonus * (killLog["EconomyDifferentialFactor"])

				# if roundIndex == "2":
				# 	print("death")
				# 	print(team1KillIndex)
				# 	print(team2KillIndex)
				# 	print(killOrderBonuses[team1KillIndex][team2KillIndex])
				# 	print(killLog["EconomyDifferentialFactor"])
				# 	print(killLog["deathOrderBonus*EconFactor"])

				if killLog["killerTeam"] == "team-1":
					team1KillIndex -= 1
				else:
					team2KillIndex -= 1

				killsInRound += 1

	return roundKillLogs

def calculateKillOrderBonus(team1KillIndex, team2KillIndex, killTeam, killsInRound):
	G = nx.DiGraph()
	G.add_weighted_edges_from([
		("5v5", "4v5", 150),
		("5v5", "5v4", 150),

		("4v5", "3v5", 130),
		("4v5", "4v4", 140),
		("5v4", "4v4", 140),
		("5v4", "5v3", 130),

		("3v5", "2v5", 90),
		("3v5", "3v4", 120),
		("4v4", "3v4", 170),
		("4v4", "3v4", 170),
		("5v3", "4v3", 120),
		("5v3", "5v2", 90),

		("2v5", "1v5", 50),
		("2v5", "2v4", 70),
		("3v4", "2v4", 130),
		("3v4", "3v3", 160),
		("4v3", "3v3", 160),
		("4v3", "4v2", 130), 
		("5v2", "4v2", 70),
		("5v2", "5v1", 50),

		("1v5", "0v5", 40),
		("1v5", "1v4", 60),
		("2v4", "1v4", 80),
		("2v4", "2v3", 130),
		("3v3", "2v3", 180),
		("3v3", "3v2", 180),
		("4v2", "3v2", 130),
		("4v2", "4v1", 80),
		("5v1", "4v1", 60),
		("5v1", "5v0", 40),

		("1v4", "0v4", 50),
		("1v4", "1v3", 70),
		("2v3", "1v3", 100),
		("2v3", "2v2", 170),
		("3v2", "2v2", 170),
		("3v2", "3v1", 100),
		("4v1", "3v1", 70),
		("4v1", "4v0", 50),

		("1v3", "0v3", 70),
		("1v3", "1v2", 120),
		("2v2", "1v2", 200),
		("2v2", "2v1", 200),
		("3v1", "2v1", 120),
		("3v1", "3v0", 70),

		("1v2", "0v2", 130),
		("1v2", "1v1", 190),
		("2v1", "1v1", 190),
		("2v1", "2v0", 130),

		("1v1", "0v1", 250),
		("1v1", "1v0", 250)
	])



	beforeNode = f"{team1KillIndex}v{team2KillIndex}"
	if killTeam == "team-1":
		team1KillIndex -= 1
	else:
		team2KillIndex -= 1

	afterNode = f"{team1KillIndex}v{team2KillIndex}"
	print("kill")
	print(beforeNode)
	print(afterNode)
	try:
		return G[beforeNode][afterNode]["weight"]
	except Exception as e:
		return 100


	# killOrderConstant = 150
	# killScalor = 10


	# differentialFactor = killDifferentialFactor(team1KillIndex, team2KillIndex, killTeam)
	# playerCount = 10 - killsInRound
	# killOrderBonus = (killOrderConstant - (killScalor*killsInRound)) * (differentialFactor/playerCount)
	# return killOrderBonus

def killDifferentialFactor(team1KillIndex, team2KillIndex, killTeam):
	if killTeam == "team-1":
		return 10 * (differentialFactorFunction(team1KillIndex, team2KillIndex))
	else:
		return 10 * (differentialFactorFunction(team1KillIndex, team2KillIndex))

def differentialFactorFunction(team1, team2):
	delta = abs(team1 - team2)
	return (delta + 1)/ (delta*delta + 2* delta + 1)

def reverseAgentTeamToPlayerUsername(playersRoundInfo):

	agentTeamToPlayer = {}
	for username in playersRoundInfo.keys():
		player = playersRoundInfo[username]
		agent = player["Agent"]
		team = player["Team"]

		key = team+agent
		agentTeamToPlayer[key] = username

	return agentTeamToPlayer

def categorizeEcon(EconOfLoadout):
	if EconOfLoadout < 1000:
		return 8 #SAVE
	elif EconOfLoadout < 3300:
		return 6 #ECON
	else:
		return 4 #FULL BUY	

def calculateEconDifferential(playersRoundInfo, roundKillLogs):

	agentTeamToPlayer = reverseAgentTeamToPlayerUsername(playersRoundInfo)

	for roundIndex in roundKillLogs.keys():

		for killLog in roundKillLogs[roundIndex]:
			if killLog["Event"] == "Kill":
				killerKey = killLog["killerTeam"]+killLog["killerCharacter"]
				killerUsername = agentTeamToPlayer[killerKey]
				killerEcon = playersRoundInfo[killerUsername]["RoundInfo"][int(roundIndex)-1]["Loadout"]

				deathKey = killLog["deathTeam"]+killLog["deathCharacter"]
				deathUsername = agentTeamToPlayer[deathKey]
				deathEcon = playersRoundInfo[deathUsername]["RoundInfo"][int(roundIndex)-1]["Loadout"]

				killLog["EconomyDifferentialFactor"] = categorizeEcon(killerEcon)/categorizeEcon(deathEcon)

	return roundKillLogs


if __name__ == "__main__":
	print("Starting the scraping")
	print("Open the match in a new window on the main screen")

	filename = input("Please enter the map followed by date month year and time Ex: <MAP>MMDDYYHHMM\n")

	# createMapFolder(filename)

	input("save the tracker page as a complete webpage into the newly created folder following the same name")

	# saveAllRounds(filename)
	# cleanUpFiles(filename)
	saveHTMLToJson(filename)
	

	# print(parseEconPerRound(filename))
	# print(parseRoundOutcome(filename))
	# print(parseRoundKillList(filename)["2"])
	# print(parseRoundKillList(filename)["23"])

	# parseTeamPlayers(filename)
	# print(parsePlayerRoundInfo(filename))

	measureOutgoingImpact(filename)
	

	




	