# character ID (0), file name (1), nickname (2), level (3), rarity (4), HP (5), ATK (6), SPD (7), Favourite (8),
# Current XP (9), Hidden Identifier (10)
import asyncio
import discord
import io
import math
import os
import pickle
import random
import re
from PIL import Image, ImageFont, ImageDraw
from base_stats import *
from char_list import *
from collections import OrderedDict
from discord.ext import tasks, commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext.commands.cooldowns import BucketType
from help_data import *
from settings import *
from spellcards import *
from time import time
from uniques import *
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

# intents = discord.Intents.default()
# intents.members = True

# client = commands.Bot(command_prefix = "+",intents = intents)
client = commands.Bot(command_prefix="+")
slash = SlashCommand(client, sync_commands=True)
guild_ids=[]

activity = discord.Game(name="+new | New commands")

guess_counter = 0
correct_counter = 0

client.remove_command('help')

# remove_msg = True
guess_inst = []
trade_inst = []
PvP_class = None

# discord.Activity(type=discord.ActivityType.watching, name="movie")

char_dir = ".//touhoushit"
rarity_dir = ".//Rarities"
bg_dir = ".//BGs"


# -------------------------------------------#

def save_obj(obj, name):
	with open(name + '.pkl', 'wb') as f:
		pickle.dump(obj, f, 4)


def load_obj(name):
	with open(name + '.pkl', 'rb') as f:
		return pickle.load(f)


# load files
char_save = load_obj("Char_save")
player_save = load_obj("Player_save")
char_info = load_obj("Char_info")
player_coins = load_obj("Coin_info")
trade_count = load_obj("Trade_count")
achievements = load_obj("achievements")


def get_pvp():  # returns the PvP class
	global PvP_class
	return PvP_class


def put_class(object):
	global PvP_class
	PvP_class = object


def get_tradeinst():  # trades going on atm
	global trade_inst
	return trade_inst


def get_charsave():  # guess rate
	global char_save
	return char_save


def get_playersave():  # player score 
	global player_save
	return player_save


def get_charinfo():  # player owned cards
	# character ID (0), file name (1), nickname (2), level (3), rarity (4), HP (5), ATK (6), SPD (7), Favourite (8),
	# Current XP (9), Hidden Identifier (10)
	global char_info
	return char_info


def put_charinfo(user, list):  # change player owned cards
	global char_info
	char_info[user] = list
	return char_info


def get_playercoins(id):  # player coins
	global player_coins
	return player_coins[id][0]


def get_tradecount():  # trade count
	global trade_count
	return trade_count


def add_playercoins(id, value):  # gives player x amount of coins
	global player_coins
	try:
		player_coins[id][0] += value
	except:
		player_coins[id] = [value, 0, 0, {}]


def add_playervouchers(id, value):
	global player_coins
	try:
		player_coins[id][1] += value
	except:
		player_coins[id] = [0, value, 0, {}]


def get_playervouchers(id):
	global player_coins
	return player_coins[id][1]


def add_playerpasses(id, value):
	global player_coins
	try:
		player_coins[id][2] += value
	except:
		player_coins[id] = [0, 0, value, {}]


def add_playeritem(id, name, value):
	global player_coins
	try:
		player_coins[id][3][name] += value
	except:
		try:
			player_coins[id][3][name] = value
		except:
			player_coins[id].append({name: value})


def get_playeritem(id, name):
	global player_coins
	try:
		value = player_coins[id][3][name]
	except:
		value = 0
		try:
			player_coins[id][3][name] = 0
		except:
			player_coins[id].append({name: 0})

	return value


def get_playerpasses(id):
	global player_coins
	return player_coins[id][2]


def get_achievements(player):
	global achievements
	return achievements.get(player)


def set_completion(player, level, value):
	global achievements
	try:
		if achievements[player][0][level] < value:
			achievements[player][0][level] = value
	except:
		achievements[player][0][level] = value


@client.command()
async def print_achievement(player):
	global achievements
	print(achievements[player])


def set_achievement(player, name, value):
	global achievements
	achievements[player][1][name] = value


def new_pve_user(player):
	global achievements
	achievements[player] = [{}, {}]
	return achievements[player]


@tasks.loop(minutes=5.0)
async def save():
	global player_save
	global char_save
	global char_info
	global player_coins
	global trade_count
	global achievements

	save_obj(player_save, "Player_save")
	save_obj(char_save, "Char_save")
	save_obj(char_info, "Char_info")
	save_obj(player_coins, "Coin_info")
	save_obj(trade_count, "Trade_count")
	save_obj(achievements, "achievements")


@tasks.loop(hours=24)
async def suggestions():
	with open("suggestions.txt", "r+", encoding="utf-8") as f:
		suggests = [line.rstrip() for line in f]
		f.truncate(0)
	if len(suggests) >=1:
		owner = await client.fetch_user(OWNER_ID)
		await owner.send("New suggestions for today")
		for sugest in suggests:
			await owner.send(sugest)


@tasks.loop(minutes=1.0)
async def log_useage():
	global guess_counter
	global correct_counter

	file = open("useage_log.txt", "a+")
	file.write(str(correct_counter) + "," + str(guess_counter) + '\n')


async def log_start():
	file = open("useage_log.txt", "a+")
	file.write(str(time()) + '\n')


@client.event
async def on_connect():
	global guild_ids
	print("Bot is running")
	await log_start()
	log_useage.start()
	print("Now keeping guess useage logs")
	await client.change_presence(activity=discord.Game(name="Have a suggestion or bug? Contact TemmieGamerGuy#3754"))
	guild_ids=[]
	for guild in client.guilds:
		guild_ids.append(guild.id)
	# print("Changed presence")
	save.start()
	suggestions.start()
	print("Now Auto Saving")


"""	
@client.event
async def on_member_join(member):
	print(f"{member} has joined the server")
	
@client.event
async def on_member_remove(member):
	print(f"{member} has left the server")
"""


@client.command()
async def help(ctx, *, command=None):
	thumb = ["https://i.imgur.com/javeshe.gif", "https://i.imgur.com/BiaSHWW.jpg", "https://i.imgur.com/7nCvHVq.jpg",
			 "https://i.imgur.com/eMmTjJy.jpg", "https://i.imgur.com/gY9g699.jpg", "https://i.imgur.com/fitJnaz.png"]

	if command is None:
		embed = discord.Embed(
			title="Sakuya Bot Help Page",
			colour=discord.Color.from_rgb(0, 255, 255),
			description="Need Links? https://top.gg/bot/717160348502982729\nType +help [command/category] to see more "
						"information about them "
		)
		embed.add_field(name="Help Categories",
						value="• Touhou Cards\n• Trading\n• PvP\n• Combat\n• Rewards\n• Misc\n• New")
		embed.set_footer(
			text="[*] symbol means everything including spaces are included in that parameter. [= x] means that "
				 "parameter defaults to that value and does not need an input from the user")

	else:
		command = command.lower()  # Set input to all lower case

		data = help_data[str(command)]  # This will crash if command does not exist
		if data[0] == 0:  # Help page is for a command
			embed = discord.Embed(
				title=data[1],
				colour=discord.Color.from_rgb(0, 255, 255),
				description=data[2]
			)
			embed.set_footer(
				text="[*] symbol means everything including spaces are included in that parameter. [= x] means that "
					 "parameter defaults to that value and does not need an input from the user")

		elif data[0] == 1:  # Help page is a module/category
			embed = discord.Embed(
				title=str(command),
				colour=discord.Color.from_rgb(0, 255, 255),
				description=data[1]
			)
			for com in data[2]:
				item = help_data[com]
				if item[0] == 0:
					try:
						if item[3] == 1:
							embed.add_field(name=com, value="See +help {command name} for full details")
							continue
					except:
						pass
					embed.add_field(name=com, value=item[2])
				elif item[0] == 2:
					try:
						words = item[2]
						embed.add_field(name=com, value=words)
					except:
						embed.add_field(name=com, value=item[1])

		elif data[0] == 2:  # Help page is not a command
			embed = discord.Embed(
				title=str(command),
				colour=discord.Color.from_rgb(0, 255, 255),
				description=data[1]
			)
		else:
			# go away error, who knows what this will do
			embed = None

	embed.set_thumbnail(url=random.choice(thumb))
	await ctx.send(embed=embed)


@help.error
async def help_error(ctx, error):
	embed = discord.Embed(
		title="",
		colour=discord.Color.from_rgb(255, 0, 0),
		description="That command does not exist. Please try a valid command or category"
	)

	await ctx.send(embed=embed)


@client.command()
async def invite(ctx):
	await ctx.send(
		"https://discord.com/api/oauth2/authorize?client_id=864237884473999382&permissions=117824&scope=bot"
		"%20applications.commands")


@client.command()
async def new(ctx):
	await help(ctx, command="new")


@client.command()
async def ns(ctx):
	# now less invasive
	print(len(client.guilds))
	glist = ""
	for guild in client.guilds:
		glist += guild.name+" - "+str(guild.member_count)+", "
	print(glist)


@client.command()
async def user_count(ctx):
	global char_info
	print(len(char_info))


@client.command()
async def load(ctx, extension):
	"""Bot owner only"""
	if ctx.message.author.id == OWNER_ID:
		client.load_extension(f'cogs.{extension}')
		await ctx.send("Loaded {} sucessfully".format(extension))


@client.command()
async def unload(ctx, extension):
	"""Bot owner only"""
	if ctx.message.author.id == OWNER_ID:
		client.unload_extension(f'cogs.{extension}')
		await ctx.send("Unloaded {} sucessfully".format(extension))


@client.command()
async def reload(ctx, extension):
	"""Bot owner only"""
	if ctx.message.author.id == OWNER_ID:
		client.unload_extension(f'cogs.{extension}')
		client.load_extension(f'cogs.{extension}')
		await ctx.send("Reloaded {} sucessfully".format(extension))


@client.command()
async def multitest(ctx):
	"""Tests stuff"""
	# await ctx.send(str(check_multi(ctx.message.content.lower())))
	pass
	'''unclear what this references for now'''


@client.command()
async def ping(ctx):
	"""Returns the bots latency to the server"""
	await ctx.send(f"Pong! {round(client.latency * 1000)}ms")


@client.command()
async def secret(ctx):
	"""oooh its a secret"""
	global player_save
	if ctx.message.content.lower() == "+secret ayylmao":
		try:
			# player_save[ctx.message.author.id] = player_save[ctx.message.author.id] + 100
			await ctx.send("Stop it")
		except Exception as e:
			player_save[ctx.message.author.id] = 100
	elif ctx.message.content.lower() == "+secret fugg":
		try:
			player_save[ctx.message.author.id] = player_save[ctx.message.author.id] - 100
		except Exception as e:
			player_save[ctx.message.author.id] = 0


@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
	"""Ask a question and you will get an answer"""
	responses = ["It is certain.",
				 "It is decidedly so.",
				 "Without a doubt.",
				 "Yes - definitely.",
				 "You may rely on it.",
				 "As I see it, yes.",
				 "Most likely.",
				 "Outlook good.",
				 "Yes.",
				 "Signs point to yes.",
				 "Reply hazy, try again.",
				 "Ask again later.",
				 "Better not tell you now.",
				 "Cannot predict now.",
				 "Concentrate and ask again.",
				 "Don't count on it.",
				 "My reply is no.",
				 "My sources say no.",
				 "Outlook not so good.",
				 "Very doubtful.",
				 "You sure you want to ask that?",
				 "Oh hell no",
				 "Ok boomer",
				 "Ok Zoomer",
				 "Based, and to answer your question YES"]
	await ctx.send(f"{random.choice(responses)}")


@client.command()
@has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
	"""Requires manage messages role for both the bot and the user. Clears out the last X messages in the channel"""
	await ctx.channel.purge(limit=amount)


@clear.error
async def clear_error(ctx, error):
	if isinstance(error, MissingPermissions):
		text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
		await ctx.send(text)


def error_embed(command, error, serious=0):
	embed = discord.Embed(
		title="Command Error",
		color=0xFF0000,
		description="{} command has failed due to the following reason.\n{}".format(command,
																					error) + "\nPlease report this on "
																							 "the Sakuya bot "
																							 "replacement support "
																							 "server or message "
																							 "TemmieGamerGuy#3754" *
					serious
	)
	return embed


@client.command()
async def give_item(ctx, ID, name, amount):
	add_playeritem(int(ID), name, int(amount))


@client.command(aliases=["upgrade"])
async def feed(ctx, ID, amount, feed_type="coin"):
	# character ID (0), file name (1), nickname (2), level (3), rarity (4), HP (5), ATK (6), SPD (7), Favourite (8),
	# Current XP (9), Hidden Identifier (10)
	"""Feeds your coins to the specified touhou card. You must specify all categories"""
	global char_info
	user_chars = char_info.get(ctx.message.author.id)
	ID = int(ID)
	amount = int(amount)
	try:
		char = user_chars[ID - 1]
	except Exception as e:
		await ctx.send("You do not have a character with the given ID")
		return None

	# basic checks
	if ID <= 0:
		await ctx.send("Please input a non-negative non-zero character ID")
		return None
	elif user_chars is None:
		await ctx.send("You do not have any characters")
		return None

	feed_type = feed_type.lower()
	if feed_type == "coin":
		await feed_coin(ctx, char, ID, amount)
	elif feed_type in ["hp", "hit points", "hitpoints", "health", "green"]:
		await feed_stat(ctx, char, ID, amount, 0)
	elif feed_type in ["atk", "attack", "pwr", "power", "might", "mel", "red"]:
		await feed_stat(ctx, char, ID, amount, 1)
	elif feed_type in ["spd", "speed", "fast", "quick", "yellow"]:
		await feed_stat(ctx, char, ID, amount, 2)
	else:
		pass


@feed.error
async def feed_error(ctx, error):
	await ctx.send(
		"You must specify a character ID and feed amount\nUse this command as follows: +feed {ID} {Amount} without the "
		"brackets")


async def feed_stat(ctx, char, ID, amount, feed_type):
	global char_info
	items = ["hp_pill", "atk_pill", "spd_pill"]

	owned = get_playeritem(ctx.author.id, items[feed_type])
	stat_cap = card_cap(char)
	feed_cap = int(stat_cap[feed_type]) - int(char[feed_type + 5])

	# item checks
	if amount > owned:
		await ctx.send(embed=error_embed("feed", "Not enough items owned"))
		return None
	elif char[feed_type + 5] >= stat_cap[feed_type]:
		await ctx.send(embed=error_embed("feed", "Card already at stat cap"))
		return None

	if amount > feed_cap: amount = feed_cap  # prevent going above cap

	char[feed_type + 5] += amount

	char_embed = discord.Embed(
		title=char[2],
		colour=discord.Color.from_rgb(144, 238, 144),
		description="{} {} has been consumed".format(amount, ["HP Pill(s) <:hp_pill:804830735982002176>",
															  "Attack Pill(s) <:attack_pill:804830653862117456>",
															  "Speed Pill(s) <:speed_pill:804830692126097429>"][
			feed_type])
	)

	char_embed.add_field(name="Level:		", value=str(char[3]), inline=False)
	char_embed.add_field(name="HP:		",
						 value=str(char[5]) + "/{}		(Current Stat/ Current Cap)".format(stat_cap[0]), inline=True)
	char_embed.add_field(name="ATK:		",
						 value=str(char[6]) + "/{}		(Current Stat/ Current Cap)".format(stat_cap[1]), inline=True)
	char_embed.add_field(name="SPD:		",
						 value=str(char[7]) + "/{}		(Current Stat/ Current Cap)".format(stat_cap[2]), inline=True)

	await ctx.send(embed=char_embed)


def card_cap(card):
	if card[1] in unique:  # unique characters
		base = unique[card[1]]
	else:  # generic characters
		base = base_stats.get(card[0])
	if base is None:
		base = [10, 10, 10]

	level = card[3]
	rarity = card[4]

	stat_cap = [(x + (rarity - 1) + 2) * level for x in base]
	# base #rarity - 1 #random
	return stat_cap


async def feed_coin(ctx, char, ID, amount):
	global char_info
	global player_coins

	coins_owned = player_coins.get(ctx.message.author.id)[0]

	# coin checks
	if coins_owned < amount:
		await ctx.send("You do not have enough coins")
		return None
	elif char[3] >= LEVEL_CAP:
		await ctx.send("This card is already at the level cap and cannot be fed points")
		return None
	elif coins_owned is None:
		await ctx.send(
			"You do not have a wallet or any characters. Please get a character using the +guess command first before "
			"you use this command")
		return None

	current_xp = char[9] + amount

	player_coins[ctx.author.id][0] -= amount

	base = None

	xp_toLvl = xp(char[3])
	lvlUp = 0
	inc_HP = 0
	inc_ATK = 0
	inc_SPD = 0

	if char[1] in unique:  # unique characters
		base = unique[char[1]]
	else:  # generic characters
		base = base_stats.get(char[0])
	if base is None:
		base = [10, 10, 10]

	# return ([character,image_name,image_name.split('.')[0],level,rarity,HP,ATK,SPD,False,0]) character ID (0),
	# file name (1), nickname (2), level (3), rarity (4), HP (5), ATK (6), SPD (7), Favourite (8), Current XP (9)
	# note: this is xp to next level not total xp

	level = char[3]

	while current_xp >= xp_toLvl and level + lvlUp < LEVEL_CAP:  # Have points to feed and is not above level cap
		current_xp -= xp_toLvl
		char[3] += 1
		lvlUp += 1
		inc_HP += base[0] + random.randint(-2, 2) + (char[4] - 1)
		inc_ATK += base[1] + random.randint(-2, 2) + (char[4] - 1)
		inc_SPD += base[2] + random.randint(-2, 2) + (char[4] - 1)
		xp_toLvl = xp(char[3])

	if level + lvlUp >= LEVEL_CAP:
		player_coins[ctx.author.id][0] += current_xp
		current_xp = 0

	char[9] = current_xp
	char[5] += inc_HP
	char[6] += inc_ATK
	char[7] += inc_SPD

	# char_info[ctx.message.author.id][ID] = char
	xp_toLvl = xp(char[3])
	bar = int((current_xp / xp_toLvl) * 10)
	xp_bar = "		[" + ("█" * bar) + ("-" * (10 - bar)) + "] " + str(current_xp) + "/" + str(
		xp_toLvl) + " (+{})".format(amount)

	char_embed = discord.Embed(
		title=char[2],
		colour=discord.Color.from_rgb(144, 238, 144),
	)
	char_embed.add_field(name="Level:		", value=str(char[3]) + "(+{})".format(lvlUp) + xp_bar, inline=False)
	char_embed.add_field(name="HP:		", value=str(char[5]) + "(+{})".format(inc_HP), inline=True)
	char_embed.add_field(name="ATK:		", value=str(char[6]) + "(+{})".format(inc_ATK), inline=True)
	char_embed.add_field(name="SPD:		", value=str(char[7]) + "(+{})".format(inc_SPD), inline=True)

	await ctx.send(embed=char_embed)


@client.command()
async def sort(ctx, option, reverse=True):
	"""Sorts your touhou characters. Type in +sort {option} {descending (true/false defaults to true if nothing is
	typed in)} to sort your characters\nOptions for sorting are {Character} {Image} {Level} {Rarity} {HP} {Attack} {
	Speed} and {Favourite} """
	global char_info
	try:
		char_info[ctx.message.author.id].sort(key=lambda x: x[
			["character", "image", "name", "level", "rarity", "hp", "attack", "speed", "favourite"].index(
				option.lower().strip())], reverse=reverse)

		await ctx.send("Sort complete")
	except Exception as e:
		await ctx.send(
			"Please follow the command with one of the following option to sort by: 'character', 'image', 'name', "
			"'level', 'rarity', 'HP', 'Attack', 'Speed', favourite")


@sort.error
async def sort_error(ctx, error):
	await ctx.send(
		"Please follow the command with one of the following option to sort by: 'character', 'image', 'name', 'level', "
		"'rarity', 'HP', 'Attack', 'Speed', favourite. You may also type (false) after the sort option to change it "
		"into ascending order. (Defaults to descending order)")


@client.command()
async def filter(ctx, *, options):
	"""Shows you a list of cards you own filtered by the options chosen


	   ALLOWED OPTERATORS: (ONLY ONE)
		>
		<
		=
		&

	   ALLOWED FILTERS:
		LEVEL
		NAME (Character)
		NICKNAME (NICK)
		RARITY
		HP
		ATK
		SPD
		FAVOURITE
	"""
	filtered_cards = get_charinfo()[ctx.author.id]

	temp = []
	for i, card in enumerate(filtered_cards):
		temp.append(card + [i])
	filtered_cards = temp

	operation_list = options.lower().split("&")  # set message to lower case and split by & symbols
	for operation in operation_list:
		operation = operation.strip()  # clean up string
		greater = operation.find(">")
		less = operation.find("<")
		equal = operation.find("=")
		if greater >= 0:
			op = operation.split(">")
			verify = filter_verify1(op)
			if type(verify) == int:
				if verify == 0 or verify == 2 or verify == 8:
					await filter_raise_error(ctx, operation, "Only equal (=) symbol allowed for this type of filter")
					return
				else:
					value = int(op[1])
					filtered_cards = [x for x in filtered_cards if x[verify] > value]  # filter the cards
			else:
				await filter_raise_error(ctx, operation, verify)
				return
		elif less >= 0:
			op = operation.split("<")
			verify = filter_verify1(op)
			if type(verify) == int:
				if verify == 0 or verify == 2 or verify == 8:
					await filter_raise_error(ctx, operation, "Only equal (=) symbol allowed for this type of filter")
					return
				else:
					value = int(op[1])
					filtered_cards = [x for x in filtered_cards if x[verify] < value]  # filter the cards
			else:
				await filter_raise_error(ctx, operation, verify)
				return
		elif equal >= 0:
			op = operation.split("=")
			verify = filter_verify1(op)
			if type(verify) == int:
				if verify == 0:  # character name
					temp = []
					for card in filtered_cards:
						char_name = card[0]
						aliases = characters.get(char_name)
						if aliases is not None:
							# Look no one but admins should have cards outside of those in the list
							# so im gonna do this poorly. Get scammed future me
							aliases = [x.lower() for x in aliases]
							if op[1] in aliases:
								temp.append(card)
					filtered_cards = temp
				elif verify == 2:  # nickname
					temp = []
					for card in filtered_cards:
						nick = card[2]
						if op[1] in nick.lower():
							temp.append(card)
					filtered_cards = temp
				elif verify == 8:  # bool
					if op[1] in ["true", "t", "y", "yes"]:
						value = True
					else:
						value = False
					filtered_cards = [x for x in filtered_cards if value == x[verify]]
				else:  # int
					value = int(op[1])
					filtered_cards = [x for x in filtered_cards if x[verify] == value]  # filter the cards
			else:
				await filter_raise_error(ctx, operation, verify)
				return
		else:
			embed = discord.Embed(
				title="Filter Error",
				colour=discord.Color.from_rgb(255, 0, 0),
				description="There was an error with the following search criteria.\n{}\n There are no comparison "
							"operators. Please use ONE of the following per filter \n- < \n- > \n- =".format(
					operation)
			)
			await ctx.send(embed=embed)

	num_cards = len(filtered_cards)

	if num_cards > 200:
		await filter_raise_error(ctx, options,
								 "Exceeded the maximum of 200 search results. Please use more constricting querries "
								 "and consider using the +sort command for more general searching")
		return
	elif num_cards <= 0:
		await filter_raise_error(ctx, options, "No cards matching the given querry were found")
		return

	page = 0
	CARDS_PER_PAGE = 15
	while len(filtered_cards) > 0:
		inv_embed = discord.Embed(
			title="Filtered Cards:",
			colour=discord.Color.from_rgb(0, 255, 253)
		)

		inv_embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author)

		cards = gen_filtered_inv(filtered_cards, CARDS_PER_PAGE)

		inv_embed.add_field(
			name="	ID	|		Nickname		|	Level	|	HP	|	ATK	|	SPD	|	Rarity	|",
			value=cards)
		inv_embed.set_footer(text="Displaying page " + str(page + 1) + " out of " + str(
			math.ceil(num_cards / CARDS_PER_PAGE)) + " page(s)")

		await ctx.send(embed=inv_embed)
		page += 1
		filtered_cards = filtered_cards[CARDS_PER_PAGE:]


def gen_filtered_inv(card_list, amount):
	cards = ""

	for i in range(amount):
		try:
			char = card_list[i]
			line = ":star: " * char[8] + str(char[11] + 1) + "	| " + str(char[2]) + "	| Lv" + str(
				char[3]) + "	| " + str(char[5]) + "	| " + str(char[6]) + "	| " + str(char[7]) + "	| " + \
				   ["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★", "★★★★★★"][char[4] - 1] + "\n"
			cards += line
		except Exception as e:
			break

	return cards


async def filter_raise_error(ctx, error_op, error_msg):
	embed = discord.Embed(
		title="Filter Error",
		colour=discord.Color.from_rgb(255, 0, 0),
		description="There was an error with the following search criteria.\n{}\n{}".format(error_op, error_msg)
	)
	await ctx.send(embed=embed)


def filter_verify1(operation):
	"""Expects a touple with a filter and a value. Confirms the given input is valid
	If input is valid returns a single integer with the index value that needs to be checked
	returns a string with the error if it is not valid"""

	filter_id = operation[0]
	value = operation[1]

	# List of accepted filter names
	lvl = ["level", "lvl", "lv"]
	name = ["name", "character", "char"]
	nick = ["nickname", "nick", "alias"]
	rarity = ["rarity", "star"]
	HP = ["hp", "health", "hitpoints"]
	ATK = ["atk", "strength", "power", "attack"]
	SPD = ["spd", "speed"]
	FAV = ["fav", "favourite", "favorite"]

	true_str = ["true", "t", "y", "yes"]
	false_str = ["false", "f", "n", "no"]
	if filter_id in lvl:
		try:  # try setting the value to an int
			value = int(value)
			return 3
		except:
			return "Please input a number when filtering by level"
	elif filter_id in name:
		return 0

	elif filter_id in nick:
		return 2

	elif filter_id in rarity:
		try:  # try setting the value to an int
			value = int(value)
			return 4
		except:
			return "Please input a number when filtering by rarity"

	elif filter_id in HP:
		try:  # try setting the value to an int
			value = int(value)
			return 5
		except:
			return "Please input a number when filtering by HP"

	elif filter_id in ATK:
		try:  # try setting the value to an int
			value = int(value)
			return 6
		except:
			return "Please input a number when filtering by Attack"

	elif filter_id in SPD:
		try:  # try setting the value to an int
			value = int(value)
			return 7
		except:
			return "Please input a number when filtering by Speed"
	elif filter_id in FAV:
		if value in true_str or value in false_str:
			return 8
		else:
			return "Please input yes/no or true/false for filtering by favourites"
	else:
		return "Could not find keyword matching filter options. Use +help filter for full list of accepted keywords"


@filter.error
async def filter_error(ctx, error):
	embed = discord.Embed(
		title="Command Error",
		colour=discord.Color.from_rgb(255, 0, 0),
		description="The following error has occured when running the filter command\n{}\nPlease message "
					"TemmieGamerGuy#3754 if this proves to be an issue".format(
			error)
	)
	await ctx.send(embed=embed)


@client.command()
async def quit(ctx):
	"""Bot owner only"""
	global player_save
	global char_save
	global char_info
	global player_coins
	global trade_count
	global achievements

	if ctx.message.author.id == OWNER_ID:
		save_obj(player_save, "Player_save")
		save_obj(char_save, "Char_save")
		save_obj(char_info, "Char_info")
		save_obj(player_coins, "Coin_info")
		save_obj(trade_count, "Trade_count")
		save_obj(achievements, "achievements")
		print("safe to restart")


@client.command()
async def edit(ctx, id, index, value):
	"""Bot owner only"""
	global char_info
	if ctx.message.author.id == OWNER_ID:
		char_info[ctx.message.author.id][int(id) - 1][int(index)] = int(value)
		await ctx.send("Edit complete")
	else:
		await ctx.send("I don't think so buddy")


@client.command(aliases=["nick", "name"])
async def rename(ctx, id, *, name):
	"""Rename your touhou cards with this command. +rename {ID} {Name}"""
	global char_info
	if len(name) > 30:
		await ctx.send("Nickname is over the 30 character limit. Please use a shorter name")
		return None
	try:
		char_info[ctx.message.author.id][int(id) - 1][2] = name
		await ctx.send("Character has been sucessfully renamed")
	except Exception as e:
		await ctx.send(
			"You do not have a character with the same ID\nYou must use this command as follows +rename <id (number)> "
			"<name (you can have spaces)> without the brackets")


def generate_char(character, image_name, identifier, level=0, weights=[70, 20, 7, 2, 1]):
	# Character refers to character code and image_name is the file name (make sure to strip the extension)
	rarities = [1, 2, 3, 4, 5]

	if image_name in unique:  # unique characters
		base = unique[image_name]
	else:  # generic characters
		base = base_stats.get(character)

	if level == 0:
		level = random.randint(1, 40)  # generate random number from (and including) 1 to 40
	rarity = random.choices(rarities, weights=weights)[0]
	HP = 0
	ATK = 0
	SPD = 0
	if base is None:
		base = [10, 10, 10]
	for i in range(level):
		HP += base[0] + random.randint(-2, 2) + (rarity - 1)
		ATK += base[1] + random.randint(-2, 2) + (rarity - 1)
		SPD += base[2] + random.randint(-2, 2) + (rarity - 1)

	return [character, image_name, characters[character][0], level, rarity, HP, ATK, SPD, False, 0, identifier]


# character ID (0), file name (1), nickname (2), level (3), rarity (4), HP (5), ATK (6), SPD (7), Favourite (8),
# Current XP (9), Hidden Identifier (10)

@client.command()
async def create(ctx, user, folder, rarity, lvl, hp, atk, spd, *, img):
	"""Bot owner only"""
	global char_info
	if ctx.message.author.id == OWNER_ID:
		max = 0
		for char in char_info[int(user)]:
			if char[10] > max:
				max = char[10]
		char_info[int(user)].append(
			[folder, img, characters[folder][0], int(lvl), int(rarity), int(hp), int(atk), int(spd), False, 0, max + 1])
		await ctx.send("Character created")
	else:
		await ctx.send("No")


@create.error
async def create_error(ctx, error):
	print(error)
	await ctx.send("An error occurred")


def create_card(user, character, image, lvl,
				weights=[70, 20, 7, 2, 1]):  # Non command version of create (kinda?). Used for rewards from shop
	global char_info
	max = 0
	if int(user) in char_info:
		for char in char_info[int(user)]:
			if char[10] > max:
				max = char[10]
	card = generate_char(character, image, max + 1, lvl, weights)
	try:
		char_info[int(user)].append(card)
	except:
		char_info[int(user)] = [card]
	return len(char_info[int(user)])


async def check_trading(ctx, sender, target):
	"""returns true if the 2 given users can trade"""
	global trade_inst

	for trades in trade_inst:
		for i in range(2):
			if trades[i][0] == sender:
				await ctx.send(
					"You are already in a trade. Please finish your current trade session before starting a new one")
				return False
			elif trades[i][0] == target:
				await ctx.send(
					"The person you are trying to trade with is currently trading with someone. Please wait until they "
					"finish before starting a new trade")
				return False
	return True


def solve_font(draw, text, width, start_size=32, font="8-bit Arcade In.ttf"):
	size = (width + 1, 0)
	font_size = start_size + 1
	while size[0] > width:  # figure out best fit for font
		font_size -= 1
		font = ImageFont.truetype("8-bit Arcade In.ttf", font_size)
		size = draw.textsize(text, font=font)

	return font, size


def generate_trade_img(img1=None, img2=None):  # generates trade image with sprites
	bg = Image.open(bg_dir + "//" + "shit_trade_2x.png")
	bgDraw = ImageDraw.Draw(bg)
	font_XL = ImageFont.truetype("8-bit Arcade In.ttf", 32)
	font_LL = ImageFont.truetype("8-bit Arcade In.ttf", 24)
	font_L = ImageFont.truetype("8-bit Arcade In.ttf", 16)
	font_M = ImageFont.truetype("8-bit Arcade In.ttf", 12)
	font_S = ImageFont.truetype("8-bit Arcade In.ttf", 8)

	if img1 != None:
		# Draw Image
		im1 = Image.open(char_dir + "//" + img1[0] + "//" + img1[1])
		im1_fit = im1.resize((159, 180))  # size =159x180

		try:  # seriously find a better place to put these images cause i just eyeballed these and they're not centered
			# left,top,right,bottom
			bg.paste(im1_fit, (52, 99, 211, 279), im1_fit)  # transparent image
		except Exception as e:
			bg.paste(im1_fit, (52, 99, 211, 279))  # non transparent image

		rarity = Image.open(rarity_dir + "//" + str(img1[4]) + ".png")
		rarity = rarity.resize((38, 40))
		bg.paste(rarity, (32, 10, 70, 50), rarity)
		# Draw Text

		font, size = solve_font(bgDraw, img1[2], 157, 48)
		bgDraw.text((70, 30 - int(size[1] / 2)), img1[2], (255, 255, 255), font=font)

		bgDraw.text((38, 50), "Lvl " + str(img1[3]), (255, 255, 255), font=font_XL)
		bgDraw.text((38, 302), "Stats", font=font_XL)

		font, size = solve_font(bgDraw, "HP {}  ATK {}  SPD {}".format(img1[5], img1[6], img1[7]), 188, 48)

		bgDraw.text((38, 349 - int(size[1] / 2)), "HP {}  ATK {}  SPD {}".format(img1[5], img1[6], img1[7]), font=font)

	if img2 is not None:
		im2 = Image.open(char_dir + "//" + img2[0] + "//" + img2[1])
		im2_fit = im2.resize((159, 180))  # size =159x180

		try:
			bg.paste(im2_fit, (310, 99, 469, 279), im2_fit)  # transparent image
		except Exception as e:
			bg.paste(im2_fit, (310, 99, 469, 279))  # non transparent image

		rarity2 = Image.open(rarity_dir + "//" + str(img2[4]) + ".png")
		rarity2 = rarity2.resize((38, 40))
		bg.paste(rarity2, (290, 10, 328, 50), rarity2)
		# Draw Text

		font, size = solve_font(bgDraw, img2[2], 157, 48)
		bgDraw.text((328, 30 - int(size[1] / 2)), img2[2], (255, 255, 255), font=font)

		bgDraw.text((296, 50), "Lvl " + str(img2[3]), (255, 255, 255), font=font_XL)
		bgDraw.text((296, 302), "Stats", font=font_XL)

		font, size = solve_font(bgDraw, "HP {}  ATK {}  SPD {}".format(img2[5], img2[6], img2[7]), 188, 48)

		bgDraw.text((296, 349 - int(size[1] / 2)), "HP {}  ATK {}  SPD {}".format(img2[5], img2[6], img2[7]), font=font)

	return bg


@client.command()
async def test_img(ctx, id1, id2):
	global char_info
	im = generate_trade_img(char_info[ctx.message.author.id][int(id1) - 1],
							char_info[ctx.message.author.id][int(id2) - 1])
	imgByteArr = io.BytesIO()
	im.save(imgByteArr, format='PNG')
	imgByteArr.seek(0)

	await ctx.send(file=discord.File(imgByteArr, filename="image.png"))


@client.command()
async def trade(ctx, user: discord.Member):
	"""trade your touhou cards with other users"""
	sender = ctx.message.author
	if ctx.guild.get_member(user.id) is None:
		# That's how you check if someone's on the server
		await ctx.send("User you are trying to trade with someone who is not in the server")
		return

	if user is sender:
		await ctx.send("You cannot trade with your self")
		return
	elif user.id == BOT_ID:
		await ctx.send("You cannot trade with the Bot")
		return
	if not await check_trading(ctx, sender.id, user.id): return

	trade_embed = discord.Embed(
		title="Start Trade",
		colour=discord.Color.from_rgb(254, 255, 0),
		description="<@{}>, <@{}> has requested to trade with you. React with \u2705 to start trading.".format(user.id,
																											   sender.id)
	)

	msg = await ctx.send(embed=trade_embed)
	await msg.add_reaction(u'\u2705')


@trade.error
async def trade_error(ctx, error):
	print(error)
	await ctx.send("Please enter a valid member in the server")


@client.command()
async def offer(ctx, id=0):
	global char_info
	global trade_inst

	trade_info = []
	i=0
	for trades in trade_inst:
		for i in range(2):
			if trades[i][0] == ctx.message.author.id:
				trade_info = trades
				break

	# checks
	if not trade_info:
		await ctx.send(
			"You are not currently in a trade. Use +trade user to start a trade with someone before using this command")
		return

	if id <= 0:
		await ctx.send("Please specify a non-negative non-zero ID")
		return

	char = char_info[ctx.message.author.id][id - 1]
	trade_info[i][1] = [id - 1, char]

	# removes any confirms
	trade_info[0][2] = False
	trade_info[1][2] = False

	im = generate_trade_img(trade_info[0][1][1], trade_info[1][1][1])
	imgByteArr = io.BytesIO()
	im.save(imgByteArr, format='PNG')
	imgByteArr.seek(0)

	new_img = discord.File(imgByteArr, filename="image.png")

	new_embed = discord.Embed(
		title="Trade Window",
		colour=discord.Color.from_rgb(253, 255, 0),
		description="Type in +offer {ID} to put a card up for trade. Press \u2705 when you have confirmed that you are "
					"ok with the contents being traded. If there is a change in the offer, you must reconfirm the "
					"offer. Press :x: to cancel the trade. Note that you must either complete the trade or cancel it "
					"to start a new trade. Trade sessions do not expire "
	)
	if trade_info[0][1][1] is None:
		line1 = "Nothing"
	else:
		line1 = "Name: " + str(trade_info[0][1][1][2]) + "	| Lv: " + str(
			trade_info[0][1][1][3]) + "	| HP: " + str(trade_info[0][1][1][5]) + "	| ATK: " + str(
			trade_info[0][1][1][6]) + "	| SPD: " + str(trade_info[0][1][1][7]) + "	| Rarity: " + \
				["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★", "★★★★★★"][trade_info[0][1][1][4] - 1]

	if trade_info[1][1][1] is None:
		line2 = "Nothing"
	else:
		line2 = "Name: " + str(trade_info[1][1][1][2]) + "	| Lv: " + str(
			trade_info[1][1][1][3]) + "	| HP: " + str(trade_info[1][1][1][5]) + "	| ATK: " + str(
			trade_info[1][1][1][6]) + "	| SPD: " + str(trade_info[1][1][1][7]) + "	| Rarity: " + \
				["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★", "★★★★★★"][trade_info[1][1][1][4] - 1]

	new_embed.add_field(name=str(client.get_user(int(trade_info[0][0]))), value=line1, inline=False)
	new_embed.add_field(name="--------------------------------------------------------------",
						value="--------------------------------------------------------------", inline=False)
	new_embed.add_field(name=str(client.get_user(int(trade_info[1][0]))), value=line2, inline=False)

	new_embed.set_image(url="attachment://image.png")

	try:
		await trade_info[2].delete()
	except:  # If it can't delete the message stop the trade
		trade_inst.remove(trade_info)  # deletes trade instance

		new_embed = discord.Embed(
			title="Trade Canceled",
			colour=discord.Color.from_rgb(255, 0, 0),
			description="The trade has been canceled because the message could not be deleted or was removed by another user."
		)
		await ctx.send(embed=new_embed)
		return

	trade_info[2] = await ctx.send(file=new_img, embed=new_embed)
	await trade_info[2].add_reaction(u'\u2705')  # check mark
	await trade_info[2].add_reaction(u"\u274C")  # X mark


@offer.error
async def offer_error(ctx, error):
	await ctx.send("Please specify a valid ID")
	print(error)


@client.event
async def on_raw_reaction_add(payload):
	global char_info
	global player_coins
	global trade_inst
	global trade_count
	try:
		channel = client.get_channel(payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		author = message.author.id
		user = payload.member
		reaction = payload.emoji
		if author == BOT_ID:
			embed = message.embeds[0]
			color = embed.color
			owner = embed.author.name
		else:
			return
		if (color == discord.Colour(65534)) and owner == str(user):  # inventory scrolling
			footer = embed.footer.text
			current_page = int(footer.split(" ")[2])
			total_pages = int(footer.split(" ")[5])
			if str(reaction) == u"\u25C0":  # Left
				current_page -= 1
			elif str(reaction) == u"\u25B6":  # Right
				current_page += 1

			# loop page around
			if current_page > total_pages:
				current_page = 1
			elif current_page < 1:
				current_page = total_pages

			current_page -= 1  # fix page to start from 0

			new_embed = discord.Embed(
				title="Your Touhou Cards:",
				colour=discord.Color.from_rgb(0, 255, 254),
				description="Points: {} <:point:795490918563840011>\nVouchers: {} :tickets:".format(
					player_coins[user.id][0], player_coins[user.id][1])
			)

			new_embed.set_author(icon_url=user.avatar_url, name=user)

			user_chars = char_info.get(user.id)

			cards = gen_inv(user_chars, current_page)  # generates text display for all characters in the current page

			if cards == "":
				await channel.send("You do not have any characters on that page")
				return None

			new_embed.add_field(
				name="	ID	|		Nickname		|	Level	|	HP	|	ATK	|	SPD	|	Rarity	|",
				value=cards)
			new_embed.set_footer(text="Displaying page " + str(current_page + 1) + " out of " + str(
				math.ceil(len(user_chars) / 12)) + " page(s)")

			await message.edit(embed=new_embed)
		elif color == discord.Colour(16711424) and str(reaction) == u'\u2705':  # trade start menu
			target = embed.description.split(",")[0]
			target = target.replace("<@", "").replace(">", "")
			if target == str(user.id):  # person who reacted is the person being requested
				sender = embed.description.split(" ")[1]
				sender = sender.replace("<@", "").replace(">", "")

				if await check_trading(channel, int(sender), int(target)):
					new_embed = discord.Embed(
						title="Trade Window",
						colour=discord.Color.from_rgb(253, 255, 0),
						description="Type in +offer {ID} to put a card up for trade. Press \u2705 when you have "
									"confirmed that you are ok with the contents being traded. If there is a change in "
									"the offer, you must reconfirm the offer. Press :x: to cancel the trade. Note that "
									"you must either complete the trade or cancel it to start a new trade. Trade "
									"sessions do not expire "
					)
					new_embed.add_field(name=str(client.get_user(int(sender))), value="Nothing",
										inline=False)  # god this is so stupid. I get the user, convert it to an id
					# and get the user info back using this command. Im too lazy to do this properly but this is just
					# getting worse and worse
					new_embed.add_field(name="--------------------------------------------------------------",
										value="--------------------------------------------------------------",
										inline=False)
					new_embed.add_field(name=str(client.get_user(int(target))), value="Nothing", inline=False)

					with open(bg_dir + "//" + "shit_trade_2x.png", "rb") as imagefile:
						img = discord.File(imagefile, "image.png")
					new_embed.set_image(url="attachment://" + "image.png")
					await message.delete()
					msg = await channel.send(file=img, embed=new_embed)

					trade_inst.append([[int(sender), [None, None], False], [int(target), [None, None], False],
									   msg])  # starts trade session
					# 0: user ID, 1: [Char ID,char data], 2: confirmation

					await msg.add_reaction(u'\u2705')  # check mark
					await msg.add_reaction(u"\u274C")  # X mark
				else:
					await message.delete()
					return
		elif color == discord.Colour(16645888):  # trade menu
			trade_info = []
			i = 0
			for trades in trade_inst:
				for i in range(2):
					if int(trades[i][0]) == int(user.id):
						trade_info = trades
						break

			if trade_info != [] and str(reaction) == u'\u2705':  # check mark (confirm trade)
				if trade_info[i][1][1] is None:
					await channel.send("You must send a card before you can confirm the trade")
					return
				trade_info[i][2] = True
				new_embed = embed
				old_fields = embed.fields
				embed.clear_fields()
				if '\u2705' in old_fields[i * 2].name:
					old_fields[i * 2].name = old_fields[i * 2].name
				else:
					old_fields[i * 2].name = u'\u2705' + old_fields[i * 2].name
				for i in old_fields:
					new_embed.add_field(name=i.name, value=i.value, inline=i.inline)

				new_embed.set_image(url="attachment://" + "image.png")

				if trade_info[0][2] and trade_info[1][2]:
					fail1 = False
					fail2 = False
					new_embed.color = discord.Color.from_rgb(0, 255, 0)
					# I swear this is going to cause problems in the future but meh. let my future self suffer for this autism
					new_embed.description = "Trade has been completed"
					trade_inst.remove(trade_info)  # deletes trade instance
					# check to see if the characters being trades are still present in inventories (done separetly so
					# no characaters are lost)
					try:  # Player 1
						char_info[int(trade_info[0][0])].remove(trade_info[0][1][1])
					except Exception as e:
						fail1 = True

					if not fail1:
						try:  # Player 2
							char_info[int(trade_info[1][0])].remove(trade_info[1][1][1])
						except Exception as e:
							fail2 = True
					else:
						new_embed.title = "Trade Canceled"
						new_embed.description = "Failed to find card belonging to {}. Trade has been canceled".format(
							str(client.get_user(int(trade_info[0][0]))))
						new_embed.color = discord.Color.from_rgb(255, 0, 0)
					if fail2:  # give back card
						char_info[int(trade_info[0][0])].append(trade_info[0][1][1])

						new_embed.title = "Trade Canceled"
						new_embed.description = "Failed to find card belonging to {}. Trade has been canceled".format(
							str(client.get_user(int(trade_info[1][0]))))
						new_embed.color = discord.Color.from_rgb(255, 0, 0)
					else:  # give each other the cards

						# create new unique identifers for the cards
						max1 = 0
						for char in char_info[int(trade_info[0][0])]:
							if char[10] > max1:
								max1 = char[10]

						max2 = 0
						for char in char_info[int(trade_info[1][0])]:
							if char[10] > max2:
								max2 = char[10]

						trade_info[1][1][1][10] = max1 + 1  # player 1 gets this card
						trade_info[0][1][1][10] = max2 + 1  # player 2 gets this card

						try:
							trade_count[int(trade_info[0][0])] += 1
						except:
							trade_count[int(trade_info[0][0])] = 1

						try:
							trade_count[int(trade_info[1][0])] += 1
						except:
							trade_count[int(trade_info[1][0])] = 1

						char_info[int(trade_info[0][0])].append(trade_info[1][1][1])
						char_info[int(trade_info[1][0])].append(trade_info[0][1][1])

				await message.edit(embed=new_embed)

			elif trade_info != [] and str(reaction) == u"\u274C":  # X mark
				if message.id == trade_info[2].id:  # compares message ids
					trade_inst.remove(trade_info)  # deletes trade instance

					new_embed = discord.Embed(
						title="Trade Canceled",
						colour=discord.Color.from_rgb(255, 0, 0),
						description="The trade has been canceled by {}.".format(str(user))
					)
					new_embed.set_image(url="attachment://" + "image.png")

					await message.edit(embed=new_embed)
	except Exception as e:
		print(e)


def gen_inv(user_chars, page):
	cards = ""

	for i in range(12):
		try:
			char = user_chars[i + (page * 12)]
			line = ":star: " * char[8] + str(i + (page * 12) + 1) + "	| " + str(char[2]) + "	| Lv" + str(
				char[3]) + "	| " + str(char[5]) + "	| " + str(char[6]) + "	| " + str(char[7]) + "	| " + \
				   ["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★", "★★★★★★"][char[4] - 1] + "\n"
			cards += line
		except Exception as e:
			break

	return cards


@client.command()
async def server(ctx):
	"""Send a link to the support server as a dm"""
	await ctx.author.send("https://discord.gg/mRpewrh")


@slash.slash(name='suggest', description='Suggest an improvement for the bot', guild_ids=guild_ids,
			 options=[
				 create_option(
					 name="suggestion",
					 description="Your suggestions",
					 option_type=3,
					 required=True,
				 )]
			 )
async def _suggest(ctx, suggestion):
	with open("suggestions.txt", "a", encoding="utf-8") as f:
		f.write(suggestion)
	await ctx.send("Suggestion recorded")


@client.command(aliases=['inv', 'characters', 'cards', 'char', 'card'])
async def inventory(ctx, page=1):
	"""Shows info about all character cards you own. Type in a number after it to display other pages (+inv {page})"""
	global char_info
	global player_coins

	page -= 1
	try:
		page = int(page)
	except:
		await ctx.send(str(page) + " is not a page number")

	user_chars = char_info.get(ctx.message.author.id)
	if user_chars is None:
		await ctx.send(
			"Sorry {} , you do not have any character cards yet. Try getting one by using the +guess command".format(
				ctx.message.author))
		return None

	inv_embed = discord.Embed(
		title="Your Touhou Cards:",
		colour=discord.Color.from_rgb(0, 255, 254),
		description="Points: {} <:point:795490918563840011>\nVouchers: {} :tickets:".format(
			player_coins[ctx.author.id][0], player_coins[ctx.author.id][1])
	)

	inv_embed.set_author(icon_url=ctx.author.avatar_url, name=ctx.author)

	cards = gen_inv(user_chars, page)

	if cards == "":
		await ctx.send("You do not have any characters on that page")
		return None

	inv_embed.add_field(
		name="	ID	|		Nickname		|	Level	|	HP	|	ATK	|	SPD	|	Rarity	|",
		value=cards)
	inv_embed.set_footer(
		text="Displaying page " + str(page + 1) + " out of " + str(math.ceil(len(user_chars) / 12)) + " page(s)")

	msg = await ctx.send(embed=inv_embed)
	await msg.add_reaction(u"\u25C0")
	await msg.add_reaction(u"\u25B6")


@client.command(aliases=['favorite', 'fav'])
async def favourite(ctx, id=0):
	"""Adds a character to your favourites so they can't be accidently sold +favourite {ID}"""
	global char_info
	if id <= 0:
		await ctx.send("You must specify a non-zero non-negative character id")
		return None
	try:
		char = char_info[ctx.message.author.id][id - 1]
	except Exception as e:
		await ctx.send("You do not have a character with this ID")
		return None

	char[8] = not char[8]
	if char[8]:  # true
		await ctx.send("Sucessfully favourited character")
	else:  # false
		await ctx.send("Sucessfully unfavourited character")


def xp(level):
	"""Returns total xp needed to reach next level"""
	# (10+(rarity-1))*(1+0.2)^level
	return level ** 3


def value(char):
	return int((char[5] + char[6] + char[7]) * (1 + 0.4 * (char[4] - 1))) * VALUE_MULTIPLIER


@client.command()
async def sell(ctx, target, *, stars=0):
	"""Sell characters\nType in the character to sell invidually (ID) or type in +sell bulk {rarity} to sell all
	characters of a certain rarity """
	global char_info
	global player_coins

	if target == "bulk":  # Bulk selling

		if stars <= 0 or stars >= 7:
			await ctx.send(
				"Please input a valid rarity. You must use the command as +sell bulk {rarity} when bulk selling")
			return None
		try:
			chars = char_info[ctx.message.author.id]
		except Exception as e:
			await ctx.send("You do not have any characters")
			return
		sell_chars = []
		keep_chars = []
		for char in chars:
			if char[4] == stars and not char[8]:
				sell_chars.append(char)
			else:
				keep_chars.append(char)
		char_info[ctx.message.author.id] = keep_chars

		total_value = 0
		for char in sell_chars:  # sums up total coins
			total_value += value(char)
		# char_info[ctx.message.author.id] = [x for x in chars if (x[4] != stars or x[8])]

		try:  # incase you didnt have a wallet yet. (unlikely and happens only with old players)
			player_coins[ctx.message.author.id][0] += total_value
		except Exception as e:
			player_coins[ctx.message.author.id] = [total_value, 0, 0]

		suc_embed = discord.Embed(
			title="Characters successfully sold:",
			colour=discord.Color.from_rgb(0, 255, 255),
			description="You have earned {} <:point:795490918563840011> from selling ".format(total_value) + str(
				len(sell_chars)) + " characters."
		)
		await ctx.send(embed=suc_embed)

	else:
		# Single selling
		target = int(target)
		try:
			char = char_info[ctx.message.author.id][target - 1]
		except Exception as e:
			await ctx.send("You do not have a character with this ID")
			return None

		if char[8]:
			await ctx.send(
				"You cannot sell characters you have favorited. Please unfavorite by typing +favorite {ID} and try "
				"selling the character again")
			return None
		else:
			char_info[ctx.message.author.id].pop(target - 1)
			coins = value(char)
			try:  # incase you didnt have a wallet yet. (unlikly and happens only with old players)
				player_coins[ctx.message.author.id][0] += coins
			except Exception as e:
				player_coins[ctx.message.author.id] = [coins, 0, 0]
			suc_embed = discord.Embed(
				title="Character successfully sold:",
				colour=discord.Color.from_rgb(0, 255, 255),
				description="You have earned {} <:point:795490918563840011> from selling ".format(coins) + char[2]
			)
			await ctx.send(embed=suc_embed)


@sell.error
async def sell_error(ctx, error):
	await ctx.send(
		"Please input a valid rarity or ID. You must use the command as +sell bulk {rarity} when bulk selling")


async def info_internal(channel, owner, id):
	global char_info

	rare_img = ["https://i.imgur.com/i9MbAc4.png", "https://i.imgur.com/VCGR1iu.png", "https://i.imgur.com/fD1E57X.png",
				"https://i.imgur.com/hohZnFi.png", "https://i.imgur.com/Sx3vB8n.png", "https://i.imgur.com/4Xe5Jg3.gif"]

	id -= 1

	user_chars = char_info[owner]

	char_embed = discord.Embed(
		title="NEW CARD\n" + user_chars[id][2],
		colour=discord.Color.from_rgb(144, 238, 144),
	)
	current_xp = user_chars[id][9]
	xp_toLvl = xp(user_chars[id][3])
	progress = (current_xp / xp_toLvl) * 100
	bar = int(progress // 10)
	xp_bar = " [" + ("█" * bar) + ("-" * (10 - bar)) + "] " + str(current_xp) + "/" + str(
		xp_toLvl) + " ({:.1f}%)".format(progress)
	char_embed.add_field(name="Rarity:	",
						value=["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★", "★★★★★★"][user_chars[id][4] - 1],
						inline=False)
	char_embed.add_field(name="Level:		", value=str(user_chars[id][3]) + "		" + xp_bar, inline=False)
	char_embed.add_field(name="HP:		", value=user_chars[id][5], inline=True)
	char_embed.add_field(name="ATK:		", value=user_chars[id][6], inline=True)
	char_embed.add_field(name="SPD:		", value=user_chars[id][7], inline=True)

	directory = char_dir + "//" + user_chars[id][0]
	with open(directory + "//" + user_chars[id][1], "rb") as imagefile:
		img = discord.File(imagefile, "image" + "." + user_chars[id][1].split(".")[-1])
	char_embed.set_image(url="attachment://" + "image" + "." + user_chars[id][1].split(".")[-1])

	char_embed.set_thumbnail(url=rare_img[user_chars[id][4] - 1])
	await channel.send(file=img, embed=char_embed)


@client.command()
async def info(ctx, id=1):
	# character ID (0), file name (1), nickname (2), level (3), rarity (4), HP (5), ATK (6), SPD (7), Favourite (8),
	# Current XP (9), Hidden Identifier (10)
	"""Shows info about a specific character card you own"""
	global char_info

	rare_img = ["https://i.imgur.com/i9MbAc4.png", "https://i.imgur.com/VCGR1iu.png", "https://i.imgur.com/fD1E57X.png",
				"https://i.imgur.com/hohZnFi.png", "https://i.imgur.com/Sx3vB8n.png", "https://i.imgur.com/4Xe5Jg3.gif"]

	id -= 1

	if id < 0:
		await ctx.send("Please use a non-negative non-zero inventory ID")
		return None

	user_chars = char_info.get(ctx.message.author.id)
	if user_chars is None:
		await ctx.send(
			"Sorry {}, you do have any character cards yet. Try getting one by using the +guess command".format(
				ctx.message.author))
		return None

	char_embed = discord.Embed(
		title=user_chars[id][2],
		colour=discord.Color.from_rgb(144, 238, 144),
	)
	current_xp = user_chars[id][9]
	xp_toLvl = xp(user_chars[id][3])
	progress = (current_xp / xp_toLvl) * 100
	bar = int(progress // 10)
	xp_bar = " [" + ("█" * bar) + ("-" * (10 - bar)) + "] " + str(current_xp) + "/" + str(
		xp_toLvl) + " ({:.1f}%)".format(progress)
	char_embed.add_field(name="Rarity:	",
						 value=["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★", "★★★★★★"][user_chars[id][4] - 1],
						 inline=False)
	char_embed.add_field(name="Level:		", value=str(user_chars[id][3]) + "		" + xp_bar, inline=False)
	char_embed.add_field(name="HP:		", value=user_chars[id][5], inline=True)
	char_embed.add_field(name="ATK:		", value=user_chars[id][6], inline=True)
	char_embed.add_field(name="SPD:		", value=user_chars[id][7], inline=True)

	try:
		card = Spell_cards[user_chars[id][0]]  # temp until spell v2 is ready
	except:
		card = ["Generic Spell Card", "single_target_dmg", 100, True, 10,
				"A spell given to characters without a spell card. Deals damage to a single target", 0.4]

	try:
		Power = "\nPower: {}".format(int(float(card[6]) * 100))
	except:
		Power = ""
	char_embed.add_field(
		name="<:card:797943200907001867> - {} - {}<:power:796499186106236960>".format(card[0], card[2]),
		value="Priority: {}".format(card[4]) + Power + "\nDesc: {}".format(card[5]), inline=False)

	try:
		art_author = user_chars[id][1]
		art_author = art_author[:art_author.rindex(".")]  # strip off .jpg / .png
		art_author = art_author[art_author.index("(") + 1:-1]  # strip off string before bracket and remove last bracket

		char_embed.set_footer(text="Author: " + art_author)  # placed here for now. If author isn't found have no footer
	except:
		# Get info from list
		# try:
		# except:
		art_author = "Unknown"

	# char_embed.set_footer(text="Author: "+art_author)

	directory = char_dir + "//" + user_chars[id][0]
	with open(directory + "//" + user_chars[id][1], "rb") as imagefile:
		img = discord.File(imagefile, "image" + "." + user_chars[id][1].split(".")[-1])
	char_embed.set_image(url="attachment://" + "image" + "." + user_chars[id][1].split(".")[-1])

	char_embed.set_thumbnail(url=rare_img[user_chars[id][4] - 1])

	# Sends msg
	sent_msg = await ctx.send(file=img, embed=char_embed)


@info.error
async def info_error(ctx, error):
	await ctx.send("You do not have a character with the given ID")


@client.command()
async def give(ctx, user: discord.Member, amount=0):
	global player_coins
	if ctx.message.author.id == OWNER_ID:  # is owner
		player_coins[user.id][0] += amount
		await ctx.send("Gave {} {} coins".format(user, amount))
	else:
		await ctx.send("How about no")


@client.command()
async def print_guess_count(ctx):
	await ctx.send(str(correct_counter) + "/" + str(guess_counter))


@client.command()
@commands.cooldown(10, 15, commands.BucketType.user)
async def guess(ctx):
	"""Guess the touhou character posted! Keeps score of successful player guesses as the guess rate of characters"""
	global guess_inst
	global player_save
	global char_save
	global char_info
	global player_coins
	global guess_counter
	global correct_counter

	if ctx.channel.id in guess_inst:  # checks if channel is in list of active guess instances
		await ctx.send(
			"Guess instance already active, please wait until previous instance ends until starting a new one.")
		return None
	else:
		guess_inst.append(ctx.channel.id)  # adds channel to list of active guess instances

	guess_counter += 1  # ran the command

	# gets some info and picks character to use
	target = random.choice(list(characters))
	sol = characters[target]
	directory = char_dir + "//" + target
	image = random.choice(os.listdir(directory))
	# print(sol)#for me to cheat.

	# Gets character guess rate. Creates new item if it doesnt exist
	try:
		score = char_save[target]
	except Exception as e:
		score = [0, 1]
		char_save[target] = score

	# create embed to send
	guess_msg = discord.Embed(
		title="Guess Character",
		description="Guess who this character is in the next 15 seconds!",
		colour=discord.Color.from_rgb(144, 238, 144)
	)
	guess_msg.set_footer(text="This character has a " + str(int(score[0] / score[1] * 100)) + "% guess rate")

	with open(directory + "//" + image, "rb") as imagefile:
		img = discord.File(imagefile, "image" + "." + image.split(".")[-1])

	guess_msg.set_image(url="attachment://" + "image" + "." + image.split(".")[-1])

	# Sends msg
	sent_msg = await ctx.send(file=img, embed=guess_msg)

	# Checks if message send is the same as an item in the solution
	def check(m):
		if m.channel == ctx.channel:
			for i in sol:
				if i.lower() in m.content.lower():
					return True

		return False

	try:
		msg = await client.wait_for('message', timeout=15, check=check)
		await ctx.send(content='<@' + str(msg.author.id) + '>' + " guessed correctly! The character name is " + sol[0])

		correct_counter += 1  # Correct guess counts

		score = [score[0] + 1, score[1] + 1]

		# create character to save

		try:
			max = 0
			for char in char_info[msg.author.id]:
				try:
					if char[10] > max:
						max = char[10]
				except Exception as e:
					pass
			new_char = generate_char(target, image, max + 1)
		except:
			new_char = generate_char(target, image, 1)

		try:  # Score
			player_save[msg.author.id] += 1
		except Exception as e:
			player_save[msg.author.id] = 1

		try:  # Coins
			player_coins[msg.author.id][0] += PTS_PER_GUESS
		except Exception as e:
			player_coins[msg.author.id] = [PTS_PER_GUESS, 0, 0]

		try:  # Cards
			char_info[msg.author.id].append(new_char)
		except Exception as e:
			char_info[msg.author.id] = [new_char]

	except Exception as e:
		# print(e)
		await ctx.send(
			content="Uh oh! Looks like you're all out of time. Better luck next time\nThe Characters name is " + sol[0])
		score = [score[0], score[1] + 1]

	# await ctx.send("This character has a " + str(int(score[0]/score[1] * 100)) +"% guess rate")

	char_save[target] = score
	while ctx.channel.id in guess_inst: guess_inst.remove(
		ctx.channel.id)  # Remove all instances of channel id in guess_inst for use next time command is called


@guess.error
async def guess_error(ctx, error):
	global guess_inst
	while ctx.channel.id in guess_inst:
		guess_inst.remove(ctx.channel.id)
	# Remove all instances of channel id in guess_inst for use next time command is called
	# print(error)
	await ctx.send("Bot has raised the error:\n`" + str(
		error) + "`\nPlease send the error message to TemmieGamerGuy#3754 if its not a cooldown error")


for filename in os.listdir('./cogs'):
	if filename.endswith(".py"):
		client.load_extension(f'cogs.{filename[:-3]}')

client.run(CLIENT_ID)
