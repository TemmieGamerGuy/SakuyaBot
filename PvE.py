import discord, random

#user_obj -> user discord object
#user_level_data -> entire achievements file for user (including actual achievements and level completion data)

#card (pvp) => [#0 = hp,1 = atk, 2 = spd,3 = defending, 4 = statuses, 5 = nickname, 6 = spell card, 7 = Max hp, 8 = status value]

#card (normal) => character ID (0), file name (1), nickname (2), level (3), rarity (4), HP (5), ATK (6), SPD (7), Favourite (8), Current XP (9), Hidden Identifier (10)

def get_level_data(data,key):
	return_value = data[0].get(key)
	if return_value == None: return_value = 0
	return return_value
	
def generate_preview_embed(user,cards,quest,stage):
	embed = discord.Embed(
		title = "Your opponents",
		color = 0xFFFF04,
		description = "<@{}> here's the opponents you'll be facing in this stage. Press the :white_check_mark: to start the fight or :x: to cancel".format(user.id)
	)
	for card in cards:
		if card == None:
			continue
		embed.add_field(name = card[2]+" Lv."+str(card[3]),value = "HP: "+str(card[5])+"\nATK: "+str(card[6])+"\nSPD: "+str(card[7]),inline = True)
		
	embed.set_footer(text=str(quest)+":"+str(stage))
	
	return embed

def generic_AI(move,points,char_list):
	move_list = []
	AI_points = points[1]
	
	for card in char_list[1]:
		if "dead" in card[4]:
			continue
		spell_cost = card[6][2]
		hp_left = (card[0]/card[7])
		if random.random() < (hp_left*2):#randomly chose to defend (if % of hp left is bigger than random number, we attack. If less than we defend) -> (less hp = high chance to defend, doesnt defend until below 50% hp)
			target = random.randint(0,2)
			while char_list[0][target][0] <= 0:#char is dead (find another target)
				target = (target+1)%3#shut up atleast its a fix ok
				
			if  AI_points >= spell_cost and random.random() >= 0.5:#50/50 chance of using spellcard if AI has enough points (doesn't work with ally targeting spells. => fix later)
				move_list.append([card,"spell",(0,target),0,1])
				points[1] -= spell_cost
			else:
				move_list.append([card,"atk",(0,target),10,1])
		else:
			move_list.append([card,"def",None,5,1])
	return move_list

def training_display(user_obj,user_level_data):#Shows list of stages in the quest
	embed = discord.Embed(
		title = "Sakuya's Dojo",
		color = 0xFFFF03,
		description = "Welcome to sakuya's training dojo "+str(user_obj)+". Sakuya and the maids ready to train you personally. Items that can drop are listed below each stage\nMaid Images by: niwatazumi / 潦(にわたずみ)"
	)
	embed.add_field(name = ":one: Easy (Lv10) :white_check_mark:", value = "Prereqs: None", inline = False)
	embed.add_field(name = ":two: Normal (Lv30) :white_check_mark:", value = "Prereqs: None", inline = False)
	embed.add_field(name = ":three: Hard (Lv50) :white_check_mark:", value = "Prereqs: None", inline = False)
	embed.add_field(name = ":four: Lunatic (Lv70) :white_check_mark:", value = "Prereqs: None", inline = False)
	embed.add_field(name = ":five: Extra (Lv100) :white_check_mark:", value = "Prereqs: None", inline = False)
	embed.add_field(name = ":six: Phantasm (Lv150) :white_check_mark:", value = "Prerequs: None", inline = False)
	
	embed.set_footer(text="0")
	
	return embed
	
def training_prereqs(level,user_obj,user_level_data):#Checks for required prereqs
	return True

def training_preview(level,user):#sends embed displaying enemies in pvp
	if int(level) == 0:
		return "https://www.youtube.com/watch?v=aEIKunHflIo"
	cards = training_cards(level)
	return generate_preview_embed(user,cards,level,0)

def training_cards(level):#returns characters used in level
	cards = [[["Misc","1_niwatazumi.jpg","Maid A",25,1,250,250,250,False,0,1],["6-5","6-5 Sakuya Izayoi.png","Sakuya",30,2,330,550,330,False,0,2],["Misc","2_niwatazumi.jpg","Maid B",25,1,250,250,250,False,0,3]],
			[["Misc","3_niwatazumi.jpg","Maid A",47,1,480,470,470,False,0,1],["6-5","6-5 Sakuya Izayoi.png","Sakuya",50,2,550,800,550,False,0,2],["Misc","4_niwatazumi.jpg","Maid B",47,1,480,470,470,False,0,3]],
			[["Misc","c_niwatazumi.jpg","Maid A",64,1,660,600,600,False,0,1],["6-5","6-5 Sakuya Izayoi.png","Sakuya",70,5,800,1500,800,False,0,2],["Misc","d_niwatazumi.jpg","Maid B",64,1,660,600,600,False,0,3]],
			[["Misc","a_niwatazumi.jpg","Maid A",96,1,960,960,960,False,0,1],["Raid","Stand User Sakuya.jpg","Sakuya",100,5,1200,2500,1200,False,0,2],["Misc","b_niwatazumi.jpg","Maid B",96,1,960,960,960,False,0,3]],
			[["Misc","e_niwatazumi.jpg","Maid A",130,1,1300,1300,1300,False,0,1],["Raid","Stand User Sakuya.jpg","Sakuya",150,5,1600,4000,1600,False,0,2],["Misc","d_niwatazumi.jpg","Maid B",130,1,1300,1300,1300,False,0,3]]
			]
			
	return cards[level-1]#only (-1) here cause :one: is a joke level and indexing is changed to 0 before calling these commands
	
def training_AI(move,level,points,char_list):#Called at the start of every turn to decide action
	#move => list of moves by player
	#level => stage number
	#points => points owned by both players [player,AI]
	#char_list => list of chars owned by both the player and bot (char_list[0] is player and [1] is bot)
	
	#move (that the game needs) => [0 = card, 1 = action, 2 = target, 3 = priority, 4 = user (owner of card) (int [0 or 1])]
	#action = "atk" "def" or "spell"
	#target = None or (player(0,1),target(0~2))
	
	move_list = []
	AI_points = points[1]
	
	for card in char_list[1]:
		hp_left = (card[0]/card[7])
		if random.random() < (hp_left*2):#randomly chose to defend (if % of hp left is bigger than random number, we attack. If less than we defend) -> (less hp = high chance to defend, doesnt defend until below 50% hp)
			target = random.randint(0,2)
			while char_list[0][target][0] <= 0:#char is dead (find another target)
				target = (target+1)%3#shut up atleast its a fix ok
				
			if card[5] == "Sakuya" and AI_points >= 60 and random.random() >= 0.5:#50/50 chance of sakuya using spellcard if she has enough points
				move_list.append([card,"spell",(0,target),0,1])
				points[1] -= 60
			else:
				move_list.append([card,"atk",(0,target),10,1])
		else:
			move_list.append([card,"def",None,5,1])
	return move_list
	
def training_end(winner,level):
	pass
	
def mansion_display(user_obj,user_level_data):
	try:
		completion = user_level_data[0]["mansion"]
	except:
		completion = 0

	embed = discord.Embed(
		title = "Scarlet Devil Mansion",
		color = 0xFFFF03,
		description = "The Scarlet devil invites you into her Mansion. Fight your way through and get great rewards "+str(user_obj)+"! Items that can drop are listed below each stage\nMaid Images by: niwatazumi / 潦(にわたずみ)"
	)
	embed.add_field(name = ":one: The Mansion Gate keeper :white_check_mark:", value = "Prereqs: None", inline = False)
	embed.add_field(name = ":two: The Library "+":white_check_mark:"*(completion >= 1)+":x:"*(completion < 1), value = "Prereqs: Beat The Mansion Gate keeper", inline = False)
	embed.add_field(name = ":three: The Devil's Maid "+":white_check_mark:"*(completion >= 2)+":x:"*(completion < 2), value = "Prereqs: Beat The Library", inline = False)
	embed.add_field(name = ":four: The Scarlet Devil "+":white_check_mark:"*(completion >= 3)+":x:"*(completion < 3), value = "Prereqs: Beat The Devil's Maid", inline = False)
	embed.add_field(name = ":five: The Basement "+":white_check_mark:"*(completion >= 4)+":x:"*(completion < 4), value = "Prereqs: Beat The Scarlet Devil", inline = False)
	
	embed.set_footer(text="2")
	
	return embed
	
def mansion_prereqs(level,user_obj,user_level_data):
	try:
		completion = user_level_data[0]["mansion"]
	except:
		completion = 0
	return completion >= level
	
def mansion_preview(level,user):
	cards = mansion_cards(level)
	return generate_preview_embed(user,cards,level,2)
	
def mansion_cards(level):
	cards = [[["Misc","1_niwatazumi.jpg","Maid A",45,1,450,450,450,False,0,1],["6-3","6 Meiling.png","Meiling",54,2,650,650,650,False,0,2],["Misc","2_niwatazumi.jpg","Maid B",45,1,450,450,450,False,0,3]],
			[["Misc","a_niwatazumi.jpg","Maid A",47,1,480,470,470,False,0,1],["6-4","6 Patchouli.png","Patchouli",60,2,600,900,550,False,0,2],["6-4-2","Koakuma.png","Koakuma",53,1,550,600,570,False,0,3]],
			[["Misc","c_niwatazumi.jpg","Maid A",47,1,480,470,470,False,0,1],["6-5","6 Sakuya.png","Sakuya",63,5,800,1100,800,False,0,2],["Misc","d_niwatazumi.jpg","Maid B",47,1,480,470,470,False,0,3]],
			[["Misc","b_niwatazumi.jpg","Maid A",47,1,480,470,470,False,0,1],["6-6","6RemiliaAlt3.png","Remilia",65,5,900,1200,1200,False,0,2],["Misc","4_niwatazumi.jpg","Maid B",45,1,450,450,450,False,0,3]],
			[["Misc","e_niwatazumi.jpg","Maid A",55,1,550,550,550,False,0,1],["6-7","6 Flandre.png","Flandre",68,5,800,1500,900,False,0,2],["Misc","3_niwatazumi.jpg","Maid B",55,1,550,550,550,False,0,3]]
			]
			
	return cards[level]
	
def mansion_AI(move,level,points,char_list):
	#move => list of moves by player
	#level => stage number
	#points => points owned by both players [player,AI]
	#char_list => list of chars owned by both the player and bot (char_list[0] is player and [1] is bot)
	
	#move (that the game needs) => [0 = card, 1 = action, 2 = target, 3 = priority, 4 = user (owner of card) (int [0 or 1])]
	#action = "atk" "def" or "spell"
	#target = None or (player(0,1),target(0~2))
	
	move_list = []
	AI_points = points[1]
	
	for card in char_list[1]:
		hp_left = (card[0]/card[7])
		if random.random() < (hp_left*2):#randomly chose to defend (if % of hp left is bigger than random number, we attack. If less than we defend) -> (less hp = high chance to defend, doesnt defend until below 50% hp)
			target = random.randint(0,2)
			while char_list[0][target][0] <= 0:#char is dead (find another target)
				target = (target+1)%3#shut up atleast its a fix ok
				
			#This is actually garbage and terrible. But it works:tm: I hate myself
			if card[5] == "Sakuya" and AI_points >= 60 and random.random() >= 0.5:
				move_list.append([card,"spell",(0,target),0,1])
				points[1] -= 60
			elif card[5] == "Meiling" and AI_points >= 90 and random.random() >= 0.5:
				move_list.append([card,"spell",(0,target),0,1])
				points[1] -= 90
			elif card[5] == "Patchouli" and AI_points >= 95 and random.random() >= 0.5:
				move_list.append([card,"spell",(0,target),0,1])
				points[1] -= 95
			elif card[5] == "Koakuma" and AI_points >= 90 and random.random() >= 0.5:
				move_list.append([card,"spell",(0,target),0,1])
				points[1] -= 90
			elif card[5] == "Remilia" and AI_points >= 120:#Remilia should use it asap
				move_list.append([card,"spell",(0,target),0,1])
				points[1] -= 120
			elif card[5] == "Flandre" and AI_points >= 200:#Flandre should use it asap
				move_list.append([card,"spell",(0,target),0,1])
				points[1] -= 200
			else:
				move_list.append([card,"atk",(0,target),10,1])
		else:
			move_list.append([card,"def",None,5,1])
	return move_list
	
def mansion_end(winner,level,user_level_data):
	pass
	
def shrine_n_display(user_obj,user_level_data):
	try:
		completion = user_level_data[0]["shrine_n"]
	except:
		completion = 0
		
	embed = discord.Embed(
		title = "Hakurei Shrine",
		color = 0xFFFF03,
	)
	
	embed.add_field(name = ":one: Three Fairies behind the Shrine :white_check_mark:", value = "Prereqs: None", inline = False)
	embed.add_field(name = ":two: Guarding the Shrine "+":white_check_mark:"*(completion >= 1)+":x:"*(completion < 1), value = "Prereqs: Beat The Three Fairies behind the Shrine", inline = False)
	embed.add_field(name = ":three: Local Residents "+":white_check_mark:"*(completion >= 2)+":x:"*(completion < 2), value = "Prereqs: Beat The Guarding the Shrine", inline = False)
	embed.add_field(name = ":four: Haunting Ghosts of the Shrine "+":white_check_mark:"*(completion >= 3)+":x:"*(completion < 3), value = "Prereqs: Beat The Local Residents", inline = False)
	embed.add_field(name = ":five: Temporary residents "+":white_check_mark:"*(completion >= 4)+":x:"*(completion < 4), value = "Prereqs: Beat The Haunting Ghosts of the Shrine", inline = False)
	embed.add_field(name = ":six: Common Visitors "+":white_check_mark:"*(completion >= 5)+":x:"*(completion < 5), value = "Prereqs: Beat The Temporary residents", inline = False)
	
	embed.set_footer(text="3")
	
	return embed
	
def shrine_n_prereqs(level,user_obj,user_level_data):
	try:
		completion = user_level_data[0]["shrine_n"]
	except:
		completion = 0
	return completion >= level

def shrine_n_preview(level,user):
	cards = shrine_n_cards(level)
	return generate_preview_embed(user,cards,level,3)#make sure this number is differnet

def shrine_n_cards(level):
	cards = [[["12.8-A","128Star.png","Star Sapphire",28,1,280,280,280,False,0,1],["12.8-B","128Luna.png","Luna Child",28,1,280,280,280,False,0,2],["12.8-C","128Sunny.png","Sunny Milk",28,1,280,280,280,False,0,3]],
			[None,["16-3","16Aunn.png","Aunn Komano",40,5,800,500,220,False,0,1],None],
			[["EX-19","Genji.png","Genji",32,4,430,300,100,False,0,1],["15-5","15Clownpiece.png","Clownpiece",28,5,380,380,380,False,0,2],None],
			[["1-2-B","2 Mima No Weapon.png","Mima",38,5,430,550,500,False,0,1],["3-3","3 Kana.png","Kana Anaberal",36,5,400,490,550,False,0,2],None],
			[["15.5-1","Shion Yorigami.jpg","Shion Yorigami",44,4,550,550,550,False,0,1],["14-6","Th145Shinmyoumaru.png","Shinmyoumaru Sukuna",43,4,400,600,600,False,0,1],None],
			[["7.5-1","Th075Suika.png","Suika Ibuki",46,5,600,500,500,False,0,1],["1-0-2","Th13.5Marisa.png","Marisa Kirisame",49,5,550,900,800,False,0,1],["14.5-1","Th155Kasen.png","Kasen Ibaraki",46,5,600,500,500,False,0,3]]
			]
			
	return cards[level]
	
def shrine_n_AI(move,level,points,char_list):
	return generic_AI(move,points,char_list)
	
def shrine_n_end(winner,level,user_level_data):
	pass

def shrine_ex_display(user_obj,user_level_data):
	try:
		completion = user_level_data[0]["shrine_ex"]
	except:
		completion = 0
		
	embed = discord.Embed(
		title = "Hakurei Shrine EX",
		color = 0xFFFF03,
		description = "Revisit the Hakurei Shrine. The Shrine Maiden is ready to welcome you with open arms"
	)
	
	embed.add_field(name = ":one: Three Fairies behind the Shrine :white_check_mark:", value = "Prereqs: None", inline = False)
	embed.add_field(name = ":two: Residents of the Shrine "+":white_check_mark:"*(completion >= 1)+":x:"*(completion < 1), value = "Prereqs: Beat The Three Fairies behind the Shrine", inline = False)
	embed.add_field(name = ":three: Common Visitors "+":white_check_mark:"*(completion >= 2)+":x:"*(completion < 2), value = "Prereqs: Beat The Residents of the Shrine", inline = False)
	embed.add_field(name = ":four: Other Visitors "+":white_check_mark:"*(completion >= 3)+":x:"*(completion < 3), value = "Prereqs: Beat Common Visitors", inline = False)
	embed.add_field(name = ":five: The Magician "+":white_check_mark:"*(completion >= 4)+":x:"*(completion < 4), value = "Prereqs: Beat The Other Visitors", inline = False)
	embed.add_field(name = ":six: The Gap Youkai "+":white_check_mark:"*(completion >= 5)+":x:"*(completion < 5), value = "Prereqs: Beat The Magician", inline = False)
	embed.add_field(name = ":seven: The Shrine Maiden "+":white_check_mark:"*(completion >= 6)+":x:"*(completion < 6), value = "Prereqs: Beat The Gap Youkai", inline = False)
	
	embed.set_footer(text="4")
	
	return embed
	
def shrine_ex_prereqs(level,user_obj,user_level_data):
	try:
		completion = user_level_data[0]["shrine_ex"]
	except:
		completion = 0
	return completion >= level

def shrine_ex_preview(level,user):
	cards = shrine_ex_cards(level)
	return generate_preview_embed(user,cards,level,4)#make sure this number is differnet
	
def shrine_ex_cards(level):
	cards = [[["12.8-A","128Star.png","Star Sapphire",91,1,910,910,910,False,0,1],["12.8-B","128Luna.png","Luna Child",91,1,910,910,910,False,0,2],["12.8-C","128Sunny.png","Sunny Milk",91,1,910,910,910,False,0,3]],
			[["15-5","15Clownpiece.png","Clownpiece",92,1,920,920,920,False,0,2],["16-3","16Aunn.png","Aunn Komano",94,2,1400,1100,600,False,0,1],None],
			[["7.5-1","75 Suika.png","Suika Ibuki",95,3,1450,1000,1000,False,0,1],["9-1","16Aya.png","Aya Shameimaru",96,4,1800,900,900,False,0,2],["14.5-1","145Kasen.png","Kasen Ibaraki",95,3,800,1500,1200,False,0,3]],
			[["6-5","6SakuyaAlt3.png","Sakuya",96,4,1050,2150,1000,False,0,1],["6-6","6 Remilia Alt.png","Remilia Scarlet",99,4,1650,2500,1350,False,0,2],None],
			[None,["1-0-2","Th13.5Marisa.png","Kirisame Marisa",100,4,4700,3000,1200,False,0,1],None],
			[None,["7-7","Th105Yukari.png","Yukari Yakumo",100,5,6000,3500,2500,False,0,1],None],
			[None,["1-0-1","Reimu Drip.png","Reimu",100,6,7500,4000,2500,False,0,1],None]
			]
			
	return cards[level]
	
def shrine_ex_AI(move,level,points,char_list):
	return generic_AI(move,points,char_list)
	
def shrine_ex_end(winner,level,user_level_data):
	pass
	
	
def myouren_display(user_obj,user_level_data):
	try:
		completion = user_level_data[0]["myouren"]
	except:
		completion = 0
		
	embed = discord.Embed(
		title = "Myouren Shrine",
		color = 0xFFFF03,
		description = ""
	)
	
	embed.add_field(name = ":one: Temple Entrance :white_check_mark:", value = "Prereqs: None", inline = False)
	embed.add_field(name = ":two: Temple Guards "+":white_check_mark:"*(completion >= 1)+":x:"*(completion < 1), value = "Prereqs: Beat The Temple Entrance", inline = False)
	embed.add_field(name = ":three: Captain of the Palanquin Ship "+":white_check_mark:"*(completion >= 2)+":x:"*(completion < 2), value = "Prereqs: Beat The Temple Guards", inline = False)
	embed.add_field(name = ":four: Disciple of Bishamonten "+":white_check_mark:"*(completion >= 3)+":x:"*(completion < 3), value = "Prereqs: Beat the Captain of the Palanquin Ship", inline = False)
	embed.add_field(name = ":five: Residents of the Temple "+":white_check_mark:"*(completion >= 4)+":x:"*(completion < 4), value = "Prereqs: Beat The Disciple of Bishamonten", inline = False)
	embed.add_field(name = ":six: The Buddhist Monks "+":white_check_mark:"*(completion >= 5)+":x:"*(completion < 5), value = "Prereqs: Beat The Residents of the Temple", inline = False)

	embed.set_footer(text="5")
	
	return embed

def myouren_prereqs(level,user_obj,user_level_data): 
	try:
		completion = user_level_data[0]["myouren"]
	except:
		completion = 0
	return completion >= level

def myouren_preview(level,user):
	cards = myouren_cards(level)
	return generate_preview_embed(user,cards,level,5)#make sure this number is differnet

def myouren_cards(level):
	cards = [[["13-2","13Kyouko.png","Kyouko Kasodani",48,1,560,520,480,False,0,1],["11-7","11Koishi.png","Koishi Komeiji",51,1,550,580,500,False,0,2],None],
			[["12-3","Th145Ichirin.png","Ichirin Kumoi",50,1,520,600,550,False,0,1],["EX-15","12Unzan.png","Unzan",48,1,490,470,480,False,0,2],["16-3","16Aunn.png","Aunn Komano",50,1,650,520,490,False,0,3]],
			[None,["12-4","12Murasa.png","Murasa Minamitsu",50,5,1500,1250,700,False,0,1],None],
			[["12-5","12Shou.png","Shou Toramaru",51,2,650,680,580,False,0,1],["12-1","12Nazrin.png","Nazrin",51,2,650,580,680],None],
			[["15.5-2","Th155Joon.png","Joon Yorigami",53,2,680,800,600,False,0,1],["12-7","12Nue.png","Nue Houjuu",54,3,700,1000,570,False,0,2],["13-7","Th145Mamizou.png","Mamizou Futatsuiwa",53,2,680,770,600,False,0,3]],
			[["12-6","12Byakuren.png","Byakuren Hijiri",55,5,1000,1500,800,False,0,1],["EX-23","Myouren Hijiri.png","Myouren Hijiri",55,5,1000,1500,800,False,0,1],None]
			]
			
	return cards[level]

def myouren_AI(move,level,points,char_list):
	return generic_AI(move,points,char_list)
	
def myouren_end(winner,level,user_level_data):
	pass