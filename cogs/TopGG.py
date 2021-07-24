import topgg
import discord
from discord.ext import commands, tasks
from bot import add_playervouchers
from settings import *
import asyncio
import logging

VOUCHERS = 1


class TopGG(commands.Cog):
	"""Handles interactions with the top.gg API"""

	def __init__(self, bot):
		self.bot = bot
		self.token = str(TOPGGTOKEN) # set this to your DBL token
		self.dblpy = topgg.DBLClient(self.bot, self.token)
		self.weekend = False
		self.claimable = []
		self.update_stats.start()
	
	
	@tasks.loop(minutes=30.0)
	async def update_stats(self):
		"""This function runs every 30 minutes to automatically update your server count"""
		self.weekend = await self.dblpy.get_weekend_status()
		logger.info('Attempting to post server count')
		try:
			await self.dblpy.post_guild_count()
			logger.info('Posted server count ({})'.format(self.dblpy.guild_count))
		except Exception as e:
			logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

		
	@commands.command()
	async def weekend(self,ctx):
		embed = discord.Embed(
			title = "Weekend Status",
			color = 0x00FF00,
			description = "The bot currently recognizes that it is the weekend and you will receive {} vouchers for voting".format(VOUCHERS*2)*self.weekend+"It is not the weekend according to the bot. You will receive {} voucher for voting".format(VOUCHERS)*(not self.weekend)
		)
		await ctx.send(embed = embed)
	
	@commands.command(aliases = ["claim"])
	async def vote(self, ctx):
		with open("vote_info.txt", 'r+') as f:
			content = f.readlines()
			f.truncate(0)

		self.claimable.extend([x.strip().replace("\n", "").split(",") for x in content])
		print(str(self.claimable))
		for id in self.claimable:
			vote = (int(id[0]),int(id[1]))#comes in as string but i dont want to add int(id[num]) every single time i check for values
			if ctx.author.id == vote[0]:
				add_playervouchers(vote[0],vote[1])
				embed = discord.Embed(
					title = "Vote Received",
					colour = discord.Color.from_rgb(255,0,255),
					description = "Thank you for voting for Sakuya Bot <@{}>.\nYou have received {}:tickets: Reward Vouchers".format(vote[0],vote[1])
				)
				await ctx.send(embed=embed)
				self.claimable.remove(id)
				break
		else:
			embed = discord.Embed(
				title = "Vote For Bot",
				colour = 0x00FF00,
				description = "Vote for the bot at https://top.gg/bot/864237884473999382\n\nAfter voting type in +claim or +vote again to recieve a rewards voucher. You will recieve {} if you voted on the weekend. You can check if the bot recognizes that its the weekend by typing in +weekend".format(VOUCHERS*2)
			)

			await ctx.send(embed = embed)
		#await ctx.send("Command currently not in use")


	@commands.command()
	async def see_vote_list(self,ctx):
		print(self.claimable)
		
	'''@commands.command()
	async def test_vote(self,ctx):
		self.claimable.append([ctx.author.id,VOUCHERS])'''


def setup(bot):
	global logger
	logger = logging.getLogger('bot')
	
	bot.add_cog(TopGG(bot))