import discord, math
from discord.ext import commands
from bot import put_class,get_tradeinst,get_charsave,get_playersave,get_charinfo,get_playercoins
from collections import OrderedDict

class leaderboards(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	@commands.command(aliases=["gboard","globalboard","leaderboardglobal","gb","leaderboard","lb"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def globalleaderboard(self,ctx,pointer=1):
		"""Displays leaderboard of the +guess command"""
		player_save = get_playersave()
		
		pointer -= 1
		
		if pointer == 0:#top 10 is special ok
			size = 10
		else:
			size = 5
		
		position = 0
		desc = ""
		title = ""
		player_save = OrderedDict(sorted(player_save.items(), key = lambda x: x[1]))
		for i,key in enumerate(reversed(player_save.keys())):
			if i >= pointer and i < (pointer + size):#loop until we hit size	
				user = await self.client.fetch_user(int(key))#API call to discord for user info
				desc += (str(user)+" : "+str(player_save[key])+"\n")
		
		position = list(reversed(player_save)).index(ctx.message.author.id) + 1
		
		if position == 0:
			title += "\nYou are not on the leaderboard"
		else:
			ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])#I ripped this off the interent
			title += "\nYou are in " + ordinal(position) +" place"
	
		embed = discord.Embed(
			title = title,
			description = desc,
			color = discord.Colour.from_rgb(0,255,0)
		)
	
		embed.set_author(icon_url=ctx.author.avatar_url,name=ctx.author)
		
		await ctx.send(embed=embed)
	
	@globalleaderboard.error
	async def globalleaderboard_error(self,ctx,error):
		try:
			embed = discord.Embed(
				title = "Command Cooldown",
				colour = discord.Color.from_rgb(255,0,0),
				description = "You can only run this command once every 5 seconds. Please try again in {}s".format(int(error.retry_after))
			)
		except:
			embed = discord.Embed(
			title = "Command Error",
			colour = discord.Color.from_rgb(255,0,0),
			description = "The following error has occured when running the leaderboard command\n{}\nPlease message Narwaffles#0927 if this proves to be an issue".format(error)
			)
		
		await ctx.send(embed = embed)

"""	
	@commands.command(aliases = ["lb","topboard","localboard","lboard"])
	async def leaderboard(self,ctx,size=5):
		#Displays leaderboard of the +guess command for users within the server
		player_save = get_playersave()
		
		count = 0
		position = 0
		desc = ""
		title = ""
		if ctx.message.guild == None:
			await ctx.send("This command works only in servers and shows the local leaderboard.\nPlease use `+gboard {size}` without the brackets for the global leaderboard")
			return
		player_save = OrderedDict(sorted(player_save.items(), key = lambda x: x[1]))
		for key in reversed(player_save.keys()):
			user = ctx.message.guild.get_member(key)
			if user != None:
				count += 1
				if count <= size:#add the top (size) positions to list
					desc += (str(user)+" : "+str(player_save[key])+"\n")
				if key == ctx.message.author.id:
					position = count
		
		
		if position == 0:
			title += "\nYou are not on the leaderboard"
		else:
			ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])#I ripped this off the interent
			title += "\nYou are in " + ordinal(position) +" place"
	
		embed = discord.Embed(
			title = title,
			description = desc,
			color = discord.Colour.from_rgb(0,255,0)
		)
	
		embed.set_author(icon_url=ctx.author.avatar_url,name=ctx.author)
		
		await ctx.send(embed=embed)
"""

def setup(client):
	client.add_cog(leaderboards(client))