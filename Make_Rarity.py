import os
from PIL import Image

char_dir = ".//touhoushit"

try:
	file = open("save.csv","r+")
except:
	f = open("save.csv","w")
	f.close()
	file = open("save.csv","r+")

def the_thing(skip=0):
	rarity = None
	pointer = skip
	save = ""
	for char in os.listdir(char_dir):
		for image in os.listdir(char_dir+"//"+char):
			if skip > 0:
				skip -= 1
				continue
			im = Image.open(char_dir+"//"+char+"//"+image)
			im.show()
			while rarity==None:
				try:
					rarity = input("Rarity is?: ")
					if rarity == "quit":
						return save,pointer
					rarity = int(rarity)
					if rarity>5 or rarity<1:
						0/0#yeah fuck you
				except Exception:
					rarity = None
					print("Give number rarity between 1-5")
			save+=char+","+image+","+str(rarity)+"\n"
			im.close()
			rarity = None
			pointer += 1

	return save,pointer


content = file.read().split("\n\n")
print(content)
try:
	values = content[1]
except:
	values = ""
try:
	skip = int(content[0])
except:
	skip = 0

result,pointer = the_thing(skip)

result = str(pointer)+"\n\n"+values+result

file.seek(0)
file.write(result)
file.truncate()

file.close()