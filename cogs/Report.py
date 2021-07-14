import discord, math
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from bot import get_charinfo,gen_inv,info_internal,put_charinfo
from settings import *

class Report(commands.Cog):
	def __init__(self,client):
		self.client = client
		self.owner = OWNER_ID
		
	@commands.command()
	@commands.cooldown(2, 300, commands.BucketType.user)
	async def report(self,ctx,*,message):
		"""Sends a report message to the bot owner. Please write in detail what the problem is and how to replicate it if possible. This command can be used once every 5 minutes to prevent spam."""
		send_to = self.client.get_user(self.owner) #messages will be sent to this user (me)
		await send_to.send(str(ctx.message.author)+": "+message)
		await send_to.send(str(ctx.message.author.id))
		await ctx.send("Report message has been sent to bot owner. Thank you")

	@report.error
	async def report_error(self,ctx,error):
		await ctx.send(error)
		
	@commands.command()
	async def change_activity(self,ctx,*,activity):
		if ctx.message.author.id == self.owner:
			await self.client.change_presence(status = discord.Status.online, activity = discord.Game(name = activity))
	
	@commands.command()
	async def respond(self,ctx,user,*,message):
		"""Bot owner only. Used to send a message back to a user who sent a report message"""
		if ctx.message.author.id == self.owner:
			user = self.client.get_user(int(user))
			await user.send(message)
			await ctx.send("Messsage sent")
		else:
			await ctx.send("naa I think I'm good.")
		
	@respond.error
	async def respond_error(self,ctx,error):
		await ctx.send(error)

	@commands.command()
	async def debug_user(self,ctx,user,page=1):
		if ctx.message.author.id == self.owner:
			page -= 1
			user_chars = get_charinfo()[int(user)]
			user_obj = await self.client.fetch_user(user)
			
			inv_embed = discord.Embed(
				title = str(user_obj)+"'s Touhou Cards:",
				colour = discord.Color.from_rgb(0,255,254),
			)
			inv_embed.set_author(icon_url=user_obj.avatar_url,name=user_obj)
	
			cards = gen_inv(user_chars,page)

			if cards == "":
				await ctx.send("You do not have any characters on that page")
				return None

			inv_embed.add_field(name = "	ID	|		Nickname		|	Level	|	HP	|	ATK	|	SPD	|	Rarity	|",value=cards)
			inv_embed.set_footer(text="Displaying page "+str(page+1)+" out of "+str(math.ceil(len(user_chars)/12))+" page(s)")
			await ctx.send(embed = inv_embed)
			
	@commands.command()
	async def debug_card(self,ctx,user,id=1):
		id -= 1
		if ctx.author.id == self.owner:
			await info_internal(ctx,int(user),int(id)+1)#assumes index without -1 before
			data = get_charinfo()[int(user)][int(id)]
			await ctx.send(data)
			
	@commands.command()
	async def edit_card(self,ctx,user,id,index,value):
		id -= 1
		if ctx.author.id == self.owner:
			char_info = get_charinfo()[int(user)]
			char_info[int(id)][int(index)] = int(value)
			put_charinfo(int(id),char_info)
			
	@commands.command()
	async def fix_hidden_id(self,ctx,user,id=1):
		if ctx.author.id == self.owner:
			char_info = get_charinfo()[int(user)]
			max = 0
			for char in char_info:
				if char[10] > max:
					max = char[10]
			
			await self.edit_card(ctx,user,id,10,max+1)
			await self.debug_card(ctx,user,id)
	

def setup(client):
	client.add_cog(Report(client))