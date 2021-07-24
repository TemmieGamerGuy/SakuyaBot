import discord, math, random, os
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from bot import get_charinfo, put_charinfo, get_playercoins, add_playercoins, add_playervouchers, add_playerpasses, \
	get_playervouchers, get_playerpasses, info_internal, create_card
from settings import *
from char_list import *

char_dir = ".//touhoushit"


class rewards(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.quotes = ["Tomorrow's dish is fried chicken.",
					   "No, we're trying to kill you.",
					   "There's only one day before tomorrow, but that's unlimited time for me.",
					   "You're speaking to me quite rudely. There's no need to worry. We have as much time as we need.",
					   "Your time is mine. Well, it'd be nice if you had something else besides time, but...",
					   "Human meat!",
					   "I'm carrying only three changes of clothes. For myself. That, and a spare set of knives too.",
					   "Oh my, magicians are actually more in need of mercy.",
					   "Come back two hours earlier.",
					   "Your time is mine..."]

	@commands.command()
	async def testing2(self, ctx):
		x = get_playervouchers(ctx.author.id)
		print(x)

	@commands.command()
	@commands.cooldown(10, 600, commands.BucketType.user)
	async def change_image(self, ctx, ID: int, Image=0):
		char_info = get_charinfo()[ctx.author.id]
		ID -= 1

		# Checks
		if ID < 0:
			embed = discord.Embed(
				title="Non Valid IDs",
				colour=discord.Color.from_rgb(255, 0, 0),
				description="Please make sure ID values are greater than or equal to 1"
			)
			await ctx.send(embed=embed)
			return
		try:
			card = char_info[ID]
		except:
			embed = discord.Embed(
				title="Command Error",
				colour=discord.Color.from_rgb(255, 0, 0),
				description="Couldn't load a card with the given ID number. Please double to make sure you own a card with the given ID.\nPlease message Narwaffles#0927 if this proves to be an issue"
			)

			await ctx.send(embed=embed)
			return

		char_name = card[0]

		if Image == 0:
			for i, image_dir in enumerate(os.listdir(char_dir + "//" + char_name)):
				with open(char_dir + "//" + char_name + "//" + image_dir, "rb") as imagefile:
					image = discord.File(imagefile, "image" + "." + image_dir.split(".")[-1])
				await ctx.send(i + 1, file=image)

			embed = discord.Embed(
				title="Select Image",
				colour=discord.Color.from_rgb(0, 255, 0),
				description="Type in +change_image {ID} {Image Number}\nto change your character's image.\nNote that this requires and consumes an image change pass"
			)

			await ctx.send(embed=embed)
		else:
			# Change image here
			Image -= 1
			img_list = os.listdir(char_dir + "//" + char_name)  # get list of images

			# add confirm message and check for ticket
			confirm_embed = discord.Embed(
				title="Confirm Selection",
				colour=discord.Color.from_rgb(255, 166, 0),
				description="<@{}> are you sure you want to change your card with ID: {} Into the below image? \nThis action can not be reversed without another Image change pass.\nClick on the green check mark to confirm.\n\nNote: If you trade this card away or sort your inventory before clicking the confirm button the image transfer may fail. Failure of transfer will result in the return of your image pass, however unforseen side effects may occur. Please message @Narwaffles#0927 if you encounter a seroius issue".format(
					ctx.author.id, ID + 1)
			)

			confirm_embed.set_image(url="attachment://" + "image" + "." + img_list[Image].split(".")[-1])
			confirm_embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author)
			confirm_embed.set_footer(text="{}:{}:{}".format(ID, Image, card[10]))

			try:
				target_image = img_list[Image]
			except:
				embed = discord.Embed(
					title="Command Error",
					colour=discord.Color.from_rgb(255, 0, 0),
					description="The Value you inputed for Image is not within the valid range for the character requested. Please try again with a valid Image number"
				)

				await ctx.send(embed=embed)
				return

			with open(char_dir + "//" + char_name + "//" + target_image, "rb") as imagefile:
				image_file = discord.File(imagefile, "image" + "." + target_image.split(".")[-1])
				msg = await ctx.send(file=image_file, embed=confirm_embed)

			await msg.add_reaction(u'\u2705')  # Check mark
			await msg.add_reaction(u"\u274C")  # X mark

	@change_image.error
	async def change_image_error(self, ctx, error):
		embed = discord.Embed(
			title="Command Error",
			colour=discord.Color.from_rgb(255, 0, 0),
			description="The following error has occured when running the change image command\n{}\nPlease message Narwaffles#0927 if this proves to be an issue".format(
				error)
		)

		await ctx.send(embed=embed)

	@commands.command()
	@commands.cooldown(1, 79200, commands.BucketType.user)
	async def daily(self, ctx):

		add_playervouchers(ctx.author.id, 1)

		embed = discord.Embed(
			title="Daily Claimed",
			color=discord.Colour.from_rgb(0, 255, 0)
		)

		img_list = os.listdir(char_dir + "//6-5")
		random_image = random.choice(img_list)

		embed.add_field(name="You have claimed your daily reward voucher.\nYou can claim your next one in 22 hours",
						value="*" + random.choice(self.quotes) + "*")
		embed.set_image(url="attachment://" + "image" + "." + random_image.split(".")[-1])

		with open(char_dir + "//6-5" + "//" + random_image, "rb") as imagefile:
			image_file = discord.File(imagefile, "image" + "." + random_image.split(".")[-1])
			await ctx.send(file=image_file, embed=embed)

	@daily.error
	async def daily_error(self, ctx, error):
		embed = discord.Embed(
			title="Daily Cooldown",
			colour=discord.Color.from_rgb(255, 0, 0),
			description="You can only run this command once every 22 hours. Please try again in {}s".format(
				int(error.retry_after))
		)

		await ctx.send(embed=embed)

	@commands.command()
	async def give_voucher(self, ctx, id: int, amount: int):
		if ctx.author.id == OWNER_ID:
			add_playervouchers(id, amount)
			print(amount)
		else:
			print(OWNER_ID)
			print(ctx.author.id)

	@commands.command(aliases=["rewardshop", "rewards", "reward"])
	async def shop(self, ctx):
		shop_embed = discord.Embed(
			title="Reward voucher shop",
			colour=discord.Color.from_rgb(128, 0, 128),
			description="Exchange your reward vouchers for prizes. You can get the prize you want by clicking on the corresponding emoji below\nYou have {} :tickets: vouchers".format(
				get_playervouchers(ctx.author.id))
		)

		shop_embed.add_field(name=":one: Random Level 50 Card", value="Cost: 1 :tickets:", inline=False)
		shop_embed.add_field(name=":two: Common Level 1 Card of Choice", value="Cost: 1 :tickets:", inline=False)
		# shop_embed.add_field(name=":two: Common Level 1 Card of Choice",value = "WIP. Option will be available soon:tm:",inline=False)
		shop_embed.add_field(name=":three: 200000 <:point:795490918563840011>", value="Cost: 1 :tickets:", inline=False)
		shop_embed.add_field(name=":four: Image Change Pass", value="Cost: 5 :tickets:", inline=False)

		shop_embed.set_image(url="attachment://" + "image.png")

		shop_embed.set_footer(text="no refunds")

		with open("shop.png", "rb") as imagefile:
			image_file = discord.File(imagefile, "image.png")
			msg = await ctx.send(file=image_file, embed=shop_embed)

		await msg.add_reaction("1\u20E3")
		await msg.add_reaction("2\u20E3")
		await msg.add_reaction("3\u20E3")
		await msg.add_reaction("4\u20E3")

	async def not_enough(self, channel):
		embed = discord.Embed(
			title="Not enough vouchers",
			colour=0xFF0000,
			description="Sorry but you do not have enough vouchers to purchase this item"
		)

		await channel.send(embed=embed)

	async def locate_failed(self, channel, name):
		embed = discord.Embed(
			title="Failed to locate character",
			color=0xFF0000,
			description="Failed to find a character with the name {}.\nPlease double check the spelling or let Narwaffles#0927 if there is an issue with character identification.\n\nReminder that only names that work for the main guessing game will work with this command".format(
				name)
		)
		await channel.send(embed=embed)

	@commands.command()
	async def buy_select(self, ctx, *, name):
		try:
			vouchers = get_playervouchers(ctx.author.id)
		except:
			embed = discord.Embed(
				title="You do not have a wallet",
				color=0xFF0000,
				description="Failed to locate a wallet beloning to {}. Please start by using the +guess command".format(
					ctx.author.name)
			)
			await ctx.send(embed=embed)
			return

		name_lower = name.lower()
		char_id = None
		if vouchers >= 1:
			for key in characters:
				if name_lower in [x.lower() for x in characters[key]]:
					char_id = key
					break
			else:
				await self.locate_failed(ctx.channel, name)
				return

			embed = discord.Embed(
				title="Confirm character choice",
				color=0x800081,  # (128,0,129)
				description="Select the check mark reaction below to purchase a card with this character for 1:tickets: reward voucher.\n\nImportant Note: The card you get may not be the exact image shown. It will however be the same character"
			)

			embed.set_footer(text="{}:{}".format(ctx.author.id, char_id))

			directory = char_dir + "//" + char_id
			image = os.listdir(directory)[0]
			with open(directory + "//" + image, "rb") as imagefile:
				img = discord.File(imagefile, "image" + "." + image.split(".")[-1])
			embed.set_image(url="attachment://" + "image" + "." + image.split(".")[-1])

			msg = await ctx.send(embed=embed, file=img)
			await msg.add_reaction(u'\u2705')
		else:
			await not_enough(ctx.channel)

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if reaction.message.author.id == BOT_ID and user.id != BOT_ID:  # User reacted to a bot message and the user is not the bot
			if not reaction.message.embeds:
				return
			embed = reaction.message.embeds[0]
			vouchers = get_playervouchers(user.id)
			color = embed.color
			if color == discord.Colour(8388736) and str(reaction) == "1\u20E3":
				if vouchers >= 1:
					char = random.choice(list(characters))
					add_playervouchers(user.id, -1)
					directory = char_dir + "//" + char
					image_name = random.choice(os.listdir(directory))
					index = create_card(user.id, char, image_name, 50, [40, 30, 20, 8, 2])

					responce = discord.Embed(
						title="Item purchased",
						colour=discord.Color.from_rgb(128, 0, 127),
						description="Thank you for purchasing 1 random Level 50 Character. The card has been put into your account and will be displayed below shortly"
					)
					await reaction.message.channel.send(embed=responce)
					await info_internal(reaction.message.channel, user.id, index)
				else:
					await self.not_enough(reaction.message.channel)
			elif color == discord.Colour(8388736) and str(reaction) == "2\u20E3":
				if vouchers >= 1:
					responce = discord.Embed(
						title="Select desired character",
						color=discord.Color.from_rgb(128, 0, 127),
						description='Pick the character by typing in +buy_select "name of char"\nSpaces are allowed and you will receive a confirmation screen asking you to confirm your choice.'
					)
					await reaction.message.channel.send(embed=responce)
				else:
					await self.not_enough(reaction.message.channel)
			elif color == discord.Colour(8388736) and str(reaction) == "3\u20E3":
				if vouchers >= 1:
					add_playercoins(user.id, 200000)
					add_playervouchers(user.id, -1)
					responce = discord.Embed(
						title="Item purchased",
						colour=discord.Color.from_rgb(128, 0, 127),
						description="Thank you for purchasing 200000 <:point:795490918563840011>.\n200000 <:point:795490918563840011> has been deposited into your account"
					)
					await reaction.message.channel.send(embed=responce)
				else:
					await self.not_enough(reaction.message.channel)
			elif color == discord.Colour(8388736) and str(reaction) == "4\u20E3":
				if vouchers >= 5:
					add_playerpasses(user.id, 1)
					add_playervouchers(user.id, -5)
					responce = discord.Embed(
						title="Item purchased",
						colour=discord.Color.from_rgb(128, 0, 127),
						description="Thank you for purchasing 1 :ticket: Image Change Pass.\n1 :ticket: Image Change Pass has been deposited into your account"
					)
					await reaction.message.channel.send(embed=responce)
				else:
					await self.not_enough(reaction.message.channel)
			elif color == discord.Colour(8388737) and str(reaction) == u'\u2705':  # check mark for select level 1 image
				target_user, char = embed.footer.text.split(":")
				if user.id == int(target_user):
					if vouchers >= 1:
						add_playervouchers(user.id, -1)
						directory = char_dir + "//" + char
						image_name = random.choice(os.listdir(directory))
						index = create_card(user.id, char, image_name, 1, [100, 0, 0, 0, 0])
						responce = discord.Embed(
							title="Item purchased",
							colour=discord.Color.from_rgb(128, 0, 127),
							description="Thank you for purchasing 1 select Lv1 common card. The card has been put into your account and will be displayed below shortly"
						)
						await reaction.message.channel.send(embed=responce)
						await info_internal(reaction.message.channel, user.id, index)
					else:
						not_enough(reaction.message.channel)

			elif color == discord.Colour(16754176) and str(reaction) == u'\u2705':  # check mark for image change
				target = embed.description.split(" ")[0]
				target = target.replace("<@", "").replace(">", "")
				target = int(target)
				if target == user.id:  # person reacted is the expected user
					await reaction.message.delete()
					change_data = embed.footer.text.split(":")
					target_card = int(change_data[0])
					image_number = int(change_data[1])
					hidden_id = int(change_data[2])

					char_info = get_charinfo()[user.id]
					try:
						card = char_info[target_card]
					except:
						embed = discord.Embed(
							title="Image Change Failed",
							colour=0xFF0000,
							description="Couldn't load a card with the given ID number. Please double to make sure you own a card with the given ID. The Image Change Pass has been returned"
						)

						await reaction.message.channel.send(embed=embed)
						return

					if card[10] != hidden_id:
						embed = discord.Embed(
							title="Image Change Failed",
							colour=0xFF0000,
							description="Card discrepancy detected. The card about to be changed is no longer the same as the card you wished to change before. This could be because the IDs of the card you own have changed. This could be because you either traded, sold cards, or sorted your inventory. The Image Change Pass has been returned"
						)
						await reaction.message.channel.send(embed=embed)
						return

					img_list = os.listdir(char_dir + "//" + card[0])  # get list of images

					if get_playerpasses(target) >= 1:
						add_playerpasses(target, -1)
						card[1] = img_list[image_number]  # Change Image

						embed = discord.Embed(
							title="Image Change Success",
							colour=0x00FF00,
							description="The image of the requested card has been successfully changed"
						)
						await reaction.message.channel.send(embed=embed)
						return
					else:
						embed = discord.Embed(
							title="No Image Change Pass",
							colour=0xFF0000,
							description="You do not have an image pass to use"
						)
						await reaction.message.channel.send(embed=embed)
						return

			elif color == discord.Colour(16754176) and str(reaction) == u'\u274C':  # x mark for image change
				target = embed.description.split(" ")[0]
				target = target.replace("<@", "").replace(">", "")
				target = int(target)
				if target == user.id:  # person reacted is the expected user
					await reaction.message.delete()

					embed = discord.Embed(
						title="Image Change Aborted",
						colour=0xFF0000,
						description="The image change process has been aborted"
					)

					await reaction.message.channel.send(embed=embed)
					return


def setup(client):
	client.add_cog(rewards(client))
