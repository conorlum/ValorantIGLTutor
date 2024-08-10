import PIL
from PIL import Image
import glob


Maps = ["Ascent"]

for Map in Maps:
	for type in ["Default", "ECO", "Pistol", "Full Buy"]:
		location = "./" + Map + "/" + type + "/*"
		files = glob.glob(location)
		for file in files:
			image = PIL.Image.open(file) 
			(width, height) = image.size
			print(file)
			if width == 1320:
				image = image.crop((250,0,1070,773))
				print(image.size)
				image.save(file)
			if width == 820:
				image = image.resize((350,350))
				print(image.size)
				image.save(file)
			
