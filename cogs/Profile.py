import discord, requests, io
from discord.ext import commands, tasks
from bot import solve_font, save_obj, load_obj, get_playersave, get_charinfo, get_playercoins, get_pvp, get_tradecount
from PIL import Image, ImageFont, ImageDraw
from urllib.request import Request, urlopen

bg = "./BGs/Profile"
char_dir = ".//touhoushit"
rarity_dir = ".//Rarities"

im_x = 100
im_y = 280


class Profile(commands.Cog):
	def __init__(self,client):
		self.client = client
		self.profiles = load_obj("Profile")
		self.update = False
		self.save_profiles.start()
	
	@tasks.loop(seconds=30.0)
	async def save_profiles(self):
		if self.update:#Only save if theres been a change
			self.update = False
			save_obj(self.profiles,"Profile")

	@commands.command(aliases = ["set"])
	async def _set(self,ctx,option,*,value):
		"""Setup your profile with +set\nUse the option {card} to change your displayed (Featured) card\nUse the {msg} or {message} option to set a custom message on your profile.
		"""
		#Welcome to Try Except Hell
		try:
			cards = get_charinfo()[ctx.author.id]
		except:
			ctx.send("You don't own any cards. You need to get at least 1 card before setting up your profile")
			return

		try:
			profile = self.profiles[ctx.author.id]
		except:
			profile = [-1,"I love Sakuya Bot. You should upvote it on top.gg"]
		
		if option == "card":
			try:
				value = int(value)
				if value <= 0:
					await ctx.send("You must specify a non-zero non-negative integer ID value")
					return
				elif value > len(cards):
					await ctx.send("You do not have a card with this ID")
					return
			except:
				await ctx.send("You must specify a integer value corresponding to the ID of your card")
				return
				
			value -= 1
			profile[0] = cards[value][10]#saves hidden identifier. ID can change (sort) and card will stay the same
			print(cards[value])
			self.profiles[ctx.author.id] = profile
			await ctx.send("Featured card has been set to {}".format(cards[value][2]))
			self.update = True

		elif option == "msg" or option == "message":
			if len(value) > 500:
				await ctx.send("Your message exceeds the 500 character limit. Please try again")
				return
			profile[1] = value
			self.profiles[ctx.author.id] = profile
			await ctx.send("Profile message has been updated")
			self.update = True
		
		else:
			await ctx.send("The only options are card and message")	
	
	@_set.error
	async def _set_error(self,ctx,error):
		embed = discord.Embed(
			title = "Command Error",
			colour = discord.Color.from_rgb(255,0,0),
			description = "Failed to use the set command due to following error\n{}\nPlease send the error message to @Narwaffles#0927 if it is a serious issue".format(error)
		)
		
		await ctx.send(embed = embed)
	
	@commands.command()
	async def profile(self,ctx):
		try:
			profile = self.profiles[ctx.author.id]
		except:
			profile = [-1,"I love Sakuya Bot. You should upvote it on top.gg"]

		bg_im = Image.open(bg+"//2.jpg")
		bgDraw = ImageDraw.Draw(bg_im)
		
		card_bg = Image.open(bg+"//card_back.png")
		card_bg = card_bg.resize((400,600),resample=Image.NEAREST)
		
		try:
			response = requests.get(ctx.author.avatar_url)#get authors profile img
			user_im = Image.open(io.BytesIO(response.content))
			user_im = user_im.resize((64,64))
		except:
			pass
	
		user_name = str(ctx.author)
		
		try:
			cards = get_charinfo()[ctx.author.id]
		except:
			await ctx.send("You don't own any cards. You need to get at least 1 card before displaying your profile")
			return
			
		if profile[0] != -1:
			for card in cards:
				if card[10] == profile[0]:
					card_data = card
					break
			else:
				card_data = -1
		else:
			card_data = -1
			
		#Theses will always return something if charinfo returns something
		#^ no they don't
		user_coins = get_playercoins(ctx.author.id)

		PvP_class = get_pvp()
		try:
			fights_won = PvP_class.fight_count[ctx.author.id]
		except:
			fights_won = 0
			
		try:
			trades_done = get_tradecount()[ctx.author.id]
		except:
			trades_done = 0
		
		font = ImageFont.truetype("LEMONMILK-Regular.otf",32)
		font_bold = ImageFont.truetype("LEMONMILK-Bold.otf",40)
		font_big = ImageFont.truetype("LEMONMILK-Regular.otf",70)
		
		#User name
		try:
			bg_im.paste(user_im,(10,10,74,74),user_im)
		except:
			try:
				bg_im.paste(user_im,(10,10,74,74))
			except:
				pass
		bgDraw.text((80,20),user_name,(255,255,255),font=font)
		
		#Card
		if card_data != -1:
			print(card_data)
			bgDraw.text((10,100),"Featured Card",(255,255,255),font=font_bold)
			bgDraw.text((10,150),card_data[2],(255,255,255),font=font)
			if not card_data[1].startswith('https'):
				card_im = Image.open(char_dir+"/"+card_data[0]+"/"+card_data[1])
			else:
				req = Request(
					card_data[1],
					headers={'User-Agent': 'Mozilla/5.0'})

				card_im = Image.open(urlopen(req))
			
			bg_im_x = im_x - (400//16)
			bg_im_y = im_y - (600//16)
			bg_im.paste(card_bg,(bg_im_x,bg_im_y,bg_im_x+400,bg_im_y+600))
			
			#lmao fuck image ratios
			width, height = int((400/8)*7), int((600/8)*7)
			card_im = card_im.resize((width,height))
			
			try:
				bg_im.paste(card_im,(im_x,im_y,im_x+width,im_y+height),card_im)
			except:
				bg_im.paste(card_im,(im_x,im_y,im_x+width,im_y+height))
				
			#Card stats
			bgDraw.text((bg_im_x,860),"LVL: {}".format(card_data[3]),(255,255,255),font=font)
			bgDraw.text((bg_im_x+200,860),"HP: {}".format(card_data[5]),(255,255,255),font=font)
			bgDraw.text((bg_im_x+200,900),"ATK: {}".format(card_data[6]),(255,255,255),font=font)
			bgDraw.text((bg_im_x+200,940),"SPD: {}".format(card_data[7]),(255,255,255),font=font)
			
			#Rarity
			rarity = card_data[4]
			r_im = Image.open(rarity_dir+"//"+str(rarity)+".png")
			width, height = r_im.size#Oh yeah I'm reusing the same variable within the same function. Lets hope this doesn't end up biting me in the ass
			if width > 200:#If above 200px reduce to 200px while maintaining ratio
				r_im.resize((200,int(200*(height/width))))
				
			width, height = r_im.size#Shut up im lazy
			r_x = im_x - width//2
			r_y = im_y - height//2
			
			bg_im.paste(r_im,(r_x,r_y,r_x+width,r_y+height),r_im)
			
			
		else:#would be nice if it was larger and diagonally across. Not doing it cause it seems like a pain in the ass to do
			bgDraw.text((10,100),"No Card Featured",(255,255,255),font=font)
		
		#Profile Message (Quote)
		line = ""
		text = ""
		for c in profile[1]:
			line += c
			size = bgDraw.textsize(line,font=font)
			if size[0] >= 600:
				spaced = line.split(" ")
				if len(spaced) == 1:#There is only 1 word on this line
					text += line + "\n"
					line = ""
				else:#Multiple words on this line
					text += " ".join(spaced[:-1]) + "\n"
					line = spaced[-1]
		
		text+=line
		
		bgDraw.text((950,10),text,(255,255,255),font=font)
		
		#Ugly black line
		bgDraw.line((930,0,930,1000),fill = 0,width = 10)
		bgDraw.line((930,800,1600,800),fill = 0,width = 10)
		
		#Cards Owned by Rarity
		rarity_owned = [0,0,0,0,0,0]
		for card in cards:#count up rarity
			rarity_owned[card[4]-1]+=1
		
		#Title
		bgDraw.text((520,100),"Cards Owned",(255,255,255),font=font_bold)
		
		for i,count in enumerate(rarity_owned):
				
			r_im = Image.open(rarity_dir+"//"+str(i+1)+".png")
			width, height = r_im.size

			width =	 int(100*(width/height))
			height = 100

			r_im = r_im.resize((width,height))
			if rarity_owned[5] == 0 and i != 5:#Dont show LR if you dont own any LR cards
				x = 510
				y = 100+(5-i)*120
				
				bg_im.paste(r_im,(x,y,x+width,y+height),r_im)
				bgDraw.text((x+120,y),": {}".format(count),(255,255,255),font=font_big)

			elif rarity_owned[5] != 0:
				x = 510
				y = 100+(6-i)*120
				
				bg_im.paste(r_im,(x,y,x+width,y+height),r_im)
				bgDraw.text((x+120,y),": {}".format(count),(255,255,255),font=font_big)
			
		#Trades and Fights
		bgDraw.text((940,810),"Trades Done : {}".format(trades_done),(255,255,255),font=font_bold)
		bgDraw.text((974,910),"Fights Won : {}".format(fights_won),(255,255,255),font=font_bold)
		
		imgByteArr = io.BytesIO()
		bg_im.save(imgByteArr, format='PNG')
		imgByteArr.seek(0)
		await ctx.send(file=discord.File(imgByteArr,filename="image.png"))
		
	@commands.command()
	async def debug_profile(self,ctx,user):
		user = int(user)
		try:
			profile = self.profiles[user]
		except:
			profile = [-1,"I love Sakuya Bot. You should upvote it on top.gg"]

		bg_im = Image.open(bg+"//2.jpg")
		bgDraw = ImageDraw.Draw(bg_im)
		
		card_bg = Image.open(bg+"//card_back.png")
		card_bg = card_bg.resize((400,600),resample=Image.NEAREST)
		
		response = requests.get(ctx.author.avatar_url)#get authors profile img
		user_im = Image.open(io.BytesIO(response.content))
		user_im = user_im.resize((64,64))
		user_name = str(ctx.author)
		
		try:
			cards = get_charinfo()[user]
		except:
			ctx.send("You don't own any cards. You need to get at least 1 card before displaying your profile")
			return
			
		if profile[0] != -1:
			for card in cards:
				if card[10] == profile[0]:
					card_data = card
					break
			else:
				card_data = -1
		else:
			card_data = -1
			
		#Theses will always return something if charinfo returns something
		user_coins = get_playercoins(user)
		user_saves = get_playersave()[user]
		
		PvP_class = get_pvp()
		try:
			fights_won = PvP_class.fight_count[user]
		except:
			fights_won = 0
			
		try:
			trades_done = get_tradecount()[user]
		except:
			trades_done = 0
		
		font = ImageFont.truetype("LEMONMILK-Regular.otf",32)
		font_bold = ImageFont.truetype("LEMONMILK-Bold.otf",40)
		font_big = ImageFont.truetype("LEMONMILK-Regular.otf",70)
		
		#User name
		try:
			bg_im.paste(user_im,(10,10,74,74),user_im)
		except:
			bg_im.paste(user_im,(10,10,74,74))
		bgDraw.text((80,20),user_name,(255,255,255),font=font)
		
		#Card
		if card_data != -1:
			bgDraw.text((10,100),"Featured Card",(255,255,255),font=font_bold)
			bgDraw.text((10,150),card_data[2],(255,255,255),font=font)
			card_im = Image.open(char_dir+"/"+card_data[0]+"/"+card_data[1])
			
			bg_im_x = im_x - (400//16)
			bg_im_y = im_y - (600//16)
			bg_im.paste(card_bg,(bg_im_x,bg_im_y,bg_im_x+400,bg_im_y+600))
			
			#lmao fuck image ratios
			width, height = int((400/8)*7), int((600/8)*7)
			card_im = card_im.resize((width,height))
			
			try:
				bg_im.paste(card_im,(im_x,im_y,im_x+width,im_y+height),card_im)
			except:
				bg_im.paste(card_im,(im_x,im_y,im_x+width,im_y+height))
				
			#Card stats
			bgDraw.text((bg_im_x,860),"LVL: {}".format(card_data[3]),(255,255,255),font=font)
			bgDraw.text((bg_im_x+200,860),"HP: {}".format(card_data[5]),(255,255,255),font=font)
			bgDraw.text((bg_im_x+200,900),"ATK: {}".format(card_data[6]),(255,255,255),font=font)
			bgDraw.text((bg_im_x+200,940),"SPD: {}".format(card_data[7]),(255,255,255),font=font)
			
			#Rarity
			rarity = card_data[4]
			r_im = Image.open(rarity_dir+"//"+str(rarity)+".png")
			width, height = r_im.size#Oh yeah I'm reusing the same variable within the same function. Lets hope this doesn't end up biting me in the ass
			if width > 200:#If above 200px reduce to 200px while maintaining ratio
				r_im.resize((200,int(200*(height/width))))
				
			width, height = r_im.size#Shut up im lazy
			r_x = im_x - width//2
			r_y = im_y - height//2
			
			bg_im.paste(r_im,(r_x,r_y,r_x+width,r_y+height),r_im)
			
			
		else:#would be nice if it was larger and diagonally across. Not doing it cause it seems like a pain in the ass to do
			bgDraw.text((10,100),"No Card Featured",(255,255,255),font=font)
		
		#Profile Message (Quote)
		line = ""
		text = ""
		for c in profile[1]:
			line += c
			size = bgDraw.textsize(line,font=font)
			if size[0] >= 600:
				spaced = line.split(" ")
				if len(spaced) == 1:#There is only 1 word on this line
					text += line + "\n"
					line = ""
				else:#Multiple words on this line
					text += " ".join(spaced[:-1]) + "\n"
					line = spaced[-1]
		
		text+=line
		
		bgDraw.text((950,10),text,(255,255,255),font=font)
		
		#Ugly black line
		bgDraw.line((930,0,930,1000),fill = 0,width = 10)
		bgDraw.line((930,800,1600,800),fill = 0,width = 10)
		
		#Cards Owned by Rarity
		rarity_owned = [0,0,0,0,0,0]
		for card in cards:#count up rarity
			rarity_owned[card[4]-1]+=1
		
		#Title
		bgDraw.text((520,100),"Cards Owned",(255,255,255),font=font_bold)
		
		for i,count in enumerate(rarity_owned):
				
			r_im = Image.open(rarity_dir+"//"+str(i+1)+".png")
			width, height = r_im.size

			width =	 int(100*(width/height))
			height = 100

			r_im = r_im.resize((width,height))
			if rarity_owned[5] == 0 and i != 5:#Dont show LR if you dont own any LR cards
				x = 510
				y = 100+(5-i)*120
				
				bg_im.paste(r_im,(x,y,x+width,y+height),r_im)
				bgDraw.text((x+120,y),": {}".format(count),(255,255,255),font=font_big)

			elif rarity_owned[5] != 0:
				x = 510
				y = 100+(6-i)*120
				
				bg_im.paste(r_im,(x,y,x+width,y+height),r_im)
				bgDraw.text((x+120,y),": {}".format(count),(255,255,255),font=font_big)
			
		#Trades and Fights
		bgDraw.text((940,810),"Trades Done : {}".format(trades_done),(255,255,255),font=font_bold)
		bgDraw.text((974,910),"Fights Won : {}".format(fights_won),(255,255,255),font=font_bold)
		
		imgByteArr = io.BytesIO()
		bg_im.save(imgByteArr, format='PNG')
		imgByteArr.seek(0)
		await ctx.send(file=discord.File(imgByteArr,filename="image.png"))
		
		
def setup(client):
	client.add_cog(Profile(client))