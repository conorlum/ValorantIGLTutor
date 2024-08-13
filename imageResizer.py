
import glob


Maps = ["Ascent"]

for Map in Maps:
	for type in ["Default", "ECO", "Pistol", "Full Buy"]:
		location = "./" + Map + "/" + type + "/*"
		files = glob.glob(location)
		for file in files:
			print(file)
			
