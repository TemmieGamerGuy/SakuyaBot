import discord, random, os
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from bot import solve_font, save_obj, load_obj, get_playersave, get_charinfo, get_playercoins, get_pvp, get_tradecount, put_charinfo
from base_stats import *
from uniques import *
import operator
mergedcards = 0

#character ID (0), file name (1), nickname (2), level (3), rarity (4), HP (5), ATK (6), SPD (7), Favourite (8), Current XP (9), Hidden Identifier (10)

char_dir = ".//touhoushit"


async def automerge(ctx, user):
	global mergedcards
	userchar_info = get_charinfo()[user]
	sortedcards = sorted(userchar_info, key=operator.itemgetter(0, 4))
	for i, card in enumerate(sortedcards):
		if card == sortedcards[-1]:
			break
		if card[0] == sortedcards[i + 1][0] and not card[8] and not sortedcards[i + 1][8]:
			if card[4] == sortedcards[i + 1][4]:
				if card[4] <= 5:
					Card1 = card
					Card2 = sortedcards[i + 1]
					# Create new Character
					# Calulate total xp of both characters
					xp = sum([n ** 3 for n in range(Card1[3] + 1)]) + sum(
						[n ** 3 for n in range(Card2[3] + 1)]) + Card1[9] + Card2[9]
					if Card1[1] in unique:  # unique characters
						base = unique[Card1[1]]
					else:  # generic characters
						base = base_stats.get(Card1[0])
					if base == None:
						base = [10, 10, 10]
					xp_toLvl = lambda n: n ** 3
					level = 1
					HP, ATK, SPD = base
					while xp > xp_toLvl(level):
						xp -= xp_toLvl(level)
						level += 1
						HP += base[0] + random.randint(-2, 2) + (Card1[4])
						ATK += base[1] + random.randint(-2, 2) + (Card1[4])
						SPD += base[2] + random.randint(-2, 2) + (Card1[4])
					# New card should not have a stat lower than the original (Can happen cause rng stats lol)
					if HP < Card1[5]: HP = Card1[5]
					if ATK < Card1[6]: ATK = Card1[6]
					if SPD < Card1[7]: SPD = Card1[7]
					newCard = [Card1[0], Card1[1], Card1[2], level, Card1[4] + 1, HP, ATK, SPD, Card1[8], xp,
							   Card1[10]]
					# Remove Characters from List
					userchar_info.remove(Card1)
					userchar_info.remove(Card2)
					# Add new Card to List
					userchar_info.append(newCard)
					# Update Cards owned
					put_charinfo(user, userchar_info)
					mergedcards += 1
					await automerge(ctx, user)
					return
	await ctx.send(str(mergedcards) + " cards were merged")
	mergedcards = 0

class Merge(commands.Cog):
	def __init__(self,client):
		self.client = client

	@commands.command()	
	async def merge(self,ctx,ID1,ID2=None):
		if ID1 == "all":
			await automerge(ctx, ctx.author.id)
			return
		try:
			ID1 = int(ID1)
			ID2 = int(ID2)
		except:
			await ctx.send("Invalid card IDs")
			return
		char_info = get_charinfo()[ctx.author.id]
		ID1 -= 1
		ID2 -= 1
			
		Card1 = char_info[ID1]
		Card2 = char_info[ID2]
		
		#Checks
		if ID1 < 0 or ID2 < 0:
			embed = discord.Embed(
				title = "Non Valid IDs",
				colour = discord.Color.from_rgb(255,0,0),
				description = "Please make sure ID values greater than or equal to 1"
			)
		elif Card1[0] != Card2[0]:
			embed = discord.Embed(
				title = "Non Matching Characters",
				colour = discord.Color.from_rgb(255,0,0),
				description = "The card IDs given are not the same characters"
			)
		elif Card1[4] != Card2[4]:
			embed = discord.Embed(
				title = "Non Matching Rarity",
				colour = discord.Color.from_rgb(255,0,0),
				description = "The card IDs given do not have the same rarity"
			)
		elif Card1[10] == Card2[10]:
			embed = discord.Embed(
				title = "Same Card",
				colour = discord.Color.from_rgb(255,0,0),
				description = "You cannot merge a card to its self. Please use two different cards"
			)
		elif Card1[4] >= 6:
			embed = discord.Embed(
				title = "Max Rarity",
				colour = discord.Color.from_rgb(255,0,0),
				description = "You card you are trying to merge with is already at the max rarity. It cannot be merged with another card"
			)
		else:#Successful
			try:
				#Create new Character
				
				#Calulate total xp of both characters
				xp = sum([n**3 for n in range(Card1[3]+1)]) + sum([n**3 for n in range(Card2[3]+1)]) + Card1[9] + Card2[9]
				
				if Card1[1] in unique:#unique characters
					base = unique[Card1[1]]
				else:#generic characters
					base = base_stats.get(Card1[0])
				if base == None:
					base = [10,10,10]
					
				xp_toLvl = lambda n: n**3
				level = 1
				HP, ATK, SPD = base
				
				
				while xp > xp_toLvl(level):
					xp -= xp_toLvl(level)
					level += 1
					HP += base[0] + random.randint(-2,2) + (Card1[4])
					ATK += base[1] + random.randint(-2,2) + (Card1[4])
					SPD += base[2] + random.randint(-2,2) + (Card1[4])
				
				
				#New card should not have a stat lower than the original (Can happen cause rng stats lol)
				if HP < Card1[5]: HP = Card1[5]
				if ATK < Card1[6]: ATK = Card1[6]
				if SPD < Card1[7]: SPD = Card1[7]
				
				
				newCard = [Card1[0],Card1[1],Card1[2],level,Card1[4]+1,HP,ATK,SPD,Card1[8],xp,Card1[10]]
				
				#Remove Characters from List
				char_info.remove(Card1)
				char_info.remove(Card2)
				#Add new Card to List
				char_info.append(newCard)
				
				#Update Cards owned
				put_charinfo(ctx.author.id,char_info)
				
				embed = discord.Embed(
				title = "Successful Merge",
				colour = discord.Color.from_rgb(0,255,0),
				description = "The two cards have sucessfully been merged and placed into your inventory"
				)	
				
			except Exception as e:
				embed = discord.Embed(
					title = "Command Error",
					colour = discord.Color.from_rgb(255,0,0),
					description = "The following error has occured when running the merge command\n{}\nPlease message TemmieGamerGuy#3754 if this proves to be an issue".format(e)
				)
			
			
			
		await ctx.send(embed = embed)
		
	@merge.error
	async def merge_error(self,ctx,error):
		embed = discord.Embed(
			title = "Command Error",
			colour = discord.Color.from_rgb(255,0,0),
			description = "The following error has occured when running the merge command\n{}\nPlease message TemmieGamerGuy#3754 if this proves to be an issue".format(error)
		)
		
		await ctx.send(embed = embed)





def setup(client):
	client.add_cog(Merge(client))