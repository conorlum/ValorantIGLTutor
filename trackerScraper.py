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
		file = open(f"C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\TrackerPages\\{filename}-Round{roundIndexStr}.html")
		content = file.readlines()
		html = content[145]

		roundHTMLJson[i+1] = html

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



if __name__ == "__main__":
	print("Starting the scraping")
	print("Open the match in a new window on the main screen")
	print("Save the round overview for the first round and name it with the structure MapDDMMYYHMM")

	filename = input("Please enter the map followed by date month year and time\n")

	saveAllRounds(filename)
	saveHTMLToJson(filename)
	removeHTMLfiles(filename)

	

	




	