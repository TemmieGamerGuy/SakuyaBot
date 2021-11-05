import discord, asyncio, io, random, os, math, sys
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from bot import put_class, get_tradeinst, get_charsave, get_playersave, get_charinfo, get_playercoins, add_playercoins, \
	load_obj, save_obj, get_achievements, new_pve_user, set_completion, SlashCommand, SlashContext, ComponentContext, \
	create_button, create_actionrow, ButtonStyle
from PIL import Image, ImageFont, ImageDraw
from importlib import reload
from urllib.request import Request, urlopen
from spellcards import *
from settings import *
import PvE
import spellcard_func
import discord_slash

bg = "./BGs/Battle"
pve_bg = "./BGs/PvE"
char_folder = "./touhoushit"
hud = "./Hud"

# move => [card, action, target, priority, user (owner of card)]
# card => [#0 = hp,1 = atk, 2 = spd,3 = defending, 4 = statuses, 5 = nickname, 6 = spell card, 7 = Max hp, 8 = status value]


# TO DO
# IF PVP MESSAGE IS DELETED STOP (END) THE FIGHT

TAKEN_MOD = 2  # multiplies the points gained when taking dmg
GIVEN_MOD = 1  # multiplies the points gained when dishing out dmg
DMG_MOD = 10  # divides damage by this value

ACTION_DELAY = 0.3  # time in seconds between each move before being calculated and displayed on the battle log
LOG_SIZE = 10  # amount of messages to be displayed in battle log
REWARD_MOD = 10  # multiplies the amount of coins won by this amount

PVE_REWARD_MOD = 5  # multiplies the amount of coins won by this amount durring PvP (Multiplier is on top of REWARD_MOD so, its REWARD_MOD * PVE_REWARD_MOD)

# Emoji's for statuses
# add blind
STATUS_EMOJI = {"dead": "\u2620",
				"burn": "\U0001F525",  # Dmg over time
				"frozen": "\u2744",  # Cant move
				"hp_up": "\U0001F49A",
				"atk_up": "\U0001F4AA",
				"spd_up": "\U0001F45F",
				"vamp": "\U0001FA78",  # Recover HP when attacking
				"rage": "\U0001F621",  # Must attack. Will pick random target
				"phantom": "\U0001F47B",  # X% chance of dodging attack. Cant defend
				"stunned": "\u2B50",  # Can't select action
				"spell_seal": "\U0001F6AB",  # Cant use spell cards
				"blind": "<:blind:797940907625545758>",  # Selected target may not be hit
				"stop_time": "\u23F1",  # Sakuya only
				"hp_down": "\U0001F53B",
				"atk_down": "\U0001F53B",
				"spd_down": "\U0001F53B",
				"multihit": "\U0001F500",  # Will attack the target X times
				"life": "<:revive:797941194700357672>",  # revive if dead
				"hp_regen": "<:heal:797942849102282762>",  # gain hp
				"life_steal": "<:potion:804202826757570610>",  # steal hp from target
				"loaded": "<:bullet:804553414926401597>",  # for shrine tank
				"cursed": "<:curse:804596434254430248>",
				"weak_power": "<:lowenergy:804597335510220830>",  # reduced power gain
				"darkness_power": "<:darkness:804829531575550022>",  # give others blind
				"charming": "<:charming:804829506916319252>",
				"stun_power": "<:stun_power:855618685846159361>",  # gives others stun
				"strawberry": "\U0001F353",
				None: ""
				}

NEGATIVE_EFFECTS = ["burn", "frozen", "blind", "stunned"]  # ,"spell_seal","weak_power"]

STUNNED_VALUE = 0.75  # 75% hp loss. value reduces by 0.5 each turn
STUN_RECOVERY = 0.5

FROZEN_VALUE = 0.4  # 40% hp loss. value reduces by 0.1 each turn
FROZEN_RECOVERY = 0.1

SLEEP_VALUE = 0.1  # 10% hp loss. value reduced by 0.02 each turn
SLEEP_RECOVERY = 0.03

BLIND_VALUE = 3
BLIND_RECOVERY = 1

BURNED_VALUE = 3
BURNED_RECOVERY = 1

QUEST_LIST = [["training", 6, "Dojo.jpeg"],
			  ["fumo", 1],
			  ["mansion", 5, "Touhou.full.1222554.jpg"],
			  ["shrine_n", 6, "Hakurei.Shrine.jpg"],
			  ["shrine_ex", 7, "Hakurei.Shrine.jpg"],
			  ["myouren", 6, "Myouren_Temple.png"]
			  ]


class PvP(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.battles = []
		self.fight_count = load_obj("Fight_count")
		self.update = False
		self.save_count.start()

	# reload(Spells)
	# @commands.Cog.listener() #events

	async def end_battle(self, battle, winner):
		# for battle in self.battles:#remove all fight instances with this player (Just in case someone made multiple fight instances, note: this would be a bug)
		if winner.id == battle.user1.id or winner.id == battle.user2.id:
			if winner.id == battle.user1.id:
				coins = battle.team_hp[1] * REWARD_MOD  # user 1 won. calculate player 2 power
			else:
				coins = battle.team_hp[0] * REWARD_MOD  # user 2 won. calculate player 1 power

			if battle.pve == True and winner.id == battle.user1.id:
				set_completion(battle.user1.id, QUEST_LIST[battle.quest][0], battle.stage + 1)
				coins *= PVE_REWARD_MOD
			# ldict = {"winner":0,"level":battle.stage}
			# exec("a = PvE."+QUEST_LIST[battle.quest][0]+"_end(winner,level)",globals(),ldict)
			elif battle.pve == True and winner.id == battle.user2.id:
				embed = discord.Embed(
					title="Game Over",
					colour=0xFF0000,
					description="Game Over {}, you have lost the fight".format(battle.user1)
				)

			embed = discord.Embed(
				title="{} has won the fight".format(winner),
				colour=discord.Color.from_rgb(0, 255, 0),
				description="Congratulations you have won {} <:point:865682560490012713>".format(coins)
			)

			await battle.channel.send(embed=embed)
			self.battles.remove(battle)

		# send rewards to player participating
		self.update = True

		add_playercoins(winner.id, coins)

		try:
			self.fight_count[winner.id] += 1
		except:
			self.fight_count[winner.id] = 1

	@tasks.loop(seconds=30.0)
	async def save_count(self):
		if self.update:  # Only save if theres been a change
			self.update = False
			save_obj(self.fight_count, "Fight_count")

	@commands.command()
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def surrender(self, ctx):
		"""Surrender from the PvP match. Only works in you are in a PvP fight.\nYou may only surrender once every 5 minutes. This is to prevent abuse"""
		battle, user_num = self.return_battle(ctx.author)

		if battle == None:
			await ctx.send("You are not in a battle")
		else:
			winner = battle.users[1 - (user_num - 1)]
			await self.end_battle(battle, winner)

	@surrender.error
	async def surrender_error(self, ctx, error):
		embed = discord.Embed(
			title="Command Error",
			colour=discord.Color.from_rgb(255, 0, 0),
			description="The following error has occured when running the surrender command\n{}\nPlease message TemmieGamerGuy#3754 if this proves to be an issue".format(
				error)
		)

		await ctx.send(embed=embed)

	@commands.command()
	async def pingas(self, ctx):
		"""PINGAS"""
		await ctx.send("PINGAS")

	def check_battles(self, user):  # returns true if the user is not in a battle
		for battle in self.battles:
			if user.id == battle.user1.id or user.id == battle.user2.id:
				return False
		return True

	# look im sorry for writing litterally the same thing twice but im so lazy and I dont give enough shit to just make 1 good function
	def return_battle(self, user):
		for battle in self.battles:
			if user.id == battle.user1.id:
				return battle, 1
			elif user.id == battle.user2.id:
				return battle, 2
		return None, None

	@commands.command()
	async def give_pts(self, ctx):
		"""Bot owner only"""
		if ctx.author.id == OWNER_ID or BOT_ID == 739617028964483082:
			battle, id = self.return_battle(ctx.author)
			battle.points[id - 1] += 100

	@commands.Cog.listener()
	async def on_component(self, ctx: ComponentContext):
		channel = ctx.channel
		message = ctx.origin_message
		author = message.author.id
		user = ctx.author
		compid = ctx.component_id
		if author == BOT_ID and user.id != BOT_ID:
			if not message.embeds:
				print("no embed")
				return
			embed = message.embeds[0]
			color = embed.color
			owner = embed.author.name
			if color == discord.Colour(16776961) and compid == 'fightcheck':  # react to fight request
				await ctx.edit_origin()
				target = embed.description.split(",")[0]
				target = target.replace("<@", "").replace(">", "")
				if target == str(user.id):  # person who reacted is the person being requested
					await message.delete()
					sender = embed.description.split(" ")[1]
					sender = sender.replace("<@", "").replace(">", "")
					if self.check_battles(user):
						fight = Battle(await self.client.fetch_user(int(sender)), user, channel,
									   self)  # save both users so I dont have to do anymore of that retarded shit
						self.battles.append(fight)
						fightEmbed = discord.Embed(
							title="Choose Cards for PvP",
							colour=discord.Color.from_rgb(120, 120, 120),
							description="Select 3 cards to fight with.\nUse +select {ID} to pick a card.\nUse +remove to clear previous card selection"
						)

						msg1 = await fight.user1.send(embed=fightEmbed)
						msg2 = await fight.user2.send(embed=fightEmbed)

						fight.msg = [msg1, msg2]
					else:
						await channel.send("One of the users involved in the battle is already in a battle.")
						return None

			elif color == discord.Colour(65281) and compid == 'fightcheck':  # lock character choices
				await ctx.edit_origin()
				battle, id = self.return_battle(user)
				battle.locks[id - 1] = True
				new_embed = battle.msg[id - 1].embeds[0]
				new_embed.description = "Selection has been locked. Please wait until the other player has selected their cards.\nThe battle will begin automatically end in 180 seconds if the other player does not select all 3 cards"

				await battle.msg[id - 1].edit(embed=new_embed)

				if battle.locks[0] == battle.locks[1]:  # both are true
					await battle.start()

				else:
					if not battle.pve:
						await battle.users[1 - (id - 1)].send(
							"The other user has completed their character selection. You have 180 seconds before the selection period ends. If you do not choose your cards before this time period expires you will automatically lose")
						await asyncio.sleep(180)  # wait 3min
						if battle.phase == 0:  # if fight has not started force end battle
							await battle.channel.send("Fight has prematurely ended due to a time out")
							await self.end_battle(battle, battle.users[(id - 1)])

			elif color == discord.Colour(7895161) or color == discord.Colour(7895162) or color == discord.Colour(
					7895163):  # Select move for char 1, 2 and 3
				# checks
				await ctx.edit_origin()
				battle, id = self.return_battle(user)

				if compid.startswith("attack"):  # attack
					card = battle.inst_card[id - 1][int(compid[-1])]

					if card[6] == ["Reload", "self_status", 40, False, 6, "Reload Shell's for the Shrine Tank",
								   "loaded", -10] and "loaded" not in card[4]:
						await user.send("The Shrine Tank can't attack without being loaded")
						return  # im going to regret putting this here in the future but i dont care for now. Sorry to me in advance jk enjoy fixing this mess lmao

					battle.waiting_target[id - 1][int(compid[-1])] = [card, "atk", None, 10, id - 1]
					embed, targets = battle.select_target(id - 1)
					complist = []
					msgcomplist = message.components
					for emoji in targets:  # Add only buttons for characters alive
						complist.append(create_button(style=ButtonStyle.grey, emoji=emoji, custom_id=emoji+compid[-1]))
					msgcomplist[int(compid[-1])] = create_actionrow(*complist)
					await message.edit(components=msgcomplist)

					# msg.add_reaction(u"\U0001F1E6")#A
					# msg.add_reaction(u"\U0001F1E7")#B
					# msg.add_reaction(u"\U0001F1E8")#C
					battle.msg[id - 1] = message

				elif compid.startswith('shield'):  # defend
					card = battle.inst_card[id - 1][int(compid[-1])]
					battle.actionBar.append([card, "def", None, 5, id - 1])

					complist = message.components
					complist[(int(compid[-1]))] = create_actionrow(create_button(style=ButtonStyle.green, label='  '),
																	   create_button(style=ButtonStyle.green, label='  '),
																	   create_button(style=ButtonStyle.green, label='  '))
					await message.edit(components=complist)
					await battle.next_command(id - 1, complist, message)

				elif compid.startswith("spell"):  # spell card
					card = battle.inst_card[id - 1][int(compid[-1])]
					spell = card[6]
					points = battle.points[id - 1]
					if points >= spell[2]:  # cost of spell
						battle.points[id - 1] -= spell[2]  # remove cost of spell from points

						if spell[3]:  # is a targeting spell
							battle.waiting_target[id - 1][int(compid[-1])] = [card, "spell", None, spell[4], id - 1]
							embed, targets = battle.select_target(id - 1)
							complist = []
							msgcomplist = message.components
							for emoji in targets:  # Add only buttons for characters alive
								complist.append(create_button(style=ButtonStyle.grey, emoji=emoji, custom_id=emoji + str(int(compid[-1]))))
							msgcomplist[int(compid[-1])] = create_actionrow(*complist)
							await message.edit(components=msgcomplist)

							battle.msg[id - 1] = message

						else:  # is not a targeting spell
							battle.actionBar.append([card, "spell", None, spell[4], id - 1])
							complist = message.components
							complist[(int(compid[-1]))] = create_actionrow(
								create_button(style=ButtonStyle.green, label='  '),
								create_button(style=ButtonStyle.green, label='  '),
								create_button(style=ButtonStyle.green, label='  '))
							await message.edit(components=complist)
							await battle.next_command(id - 1, complist, message)

					else:
						await user.send("You don't have enough power to cast this spell")

				elif compid.startswith("🇦") or compid.startswith("🇧") or compid.startswith("🇨"):
					battle, id = self.return_battle(user)
					try:
						pointer = int(compid[-1]) # What character are we currently talking about
					except:
						return
					action = battle.waiting_target[id - 1][pointer]

					if compid.startswith("🇦"):
						action[2] = (pointer, 0)
					elif compid.startswith("🇧"):
						action[2] = (pointer, 1)
					elif compid.startswith("🇨"):
						action[2] = (pointer, 2)

					complist = message.components
					complist[pointer] = create_actionrow(create_button(style=ButtonStyle.green, label='  '),
														 create_button(style=ButtonStyle.green, label='  '),
														 create_button(style=ButtonStyle.green, label='  '))
					await message.edit(components=complist)

					# Add code to Check If this is an attack move check for speed to calc how many times you attack. Note to self. Priority exists
					battle.actionBar.append(action)

					# send new msgtry:
					# try:
					await battle.next_command(id - 1, complist, message)
					"""except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print(exc_type, fname, exc_tb.tb_lineno)
                    """

			elif color == discord.Colour(7895164):  # select target for attack
				print("depreciated")

			elif color == discord.Colour(16776962):  # select quest for pve
				await ctx.edit_origin()
				num = int(compid[-1]) - 1  # number of reaction clicked

				level_data = get_achievements(user.id)

				ldict = {"user": user, "level_data": level_data}
				exec("a = PvE." + QUEST_LIST[num][0] + "_display(user,level_data)", globals(),
					 ldict)  # I love and hate this so much

				componentlist = [[]]
				for i in range(QUEST_LIST[num][1]):  # add reactions
					if len(componentlist[0]) < 5:
						componentlist[0].append(create_button(style=ButtonStyle.grey, emoji=str(i + 1) + "\u20E3", custom_id="fight" + str(i + 1)))
					elif len(componentlist[0]) == 5:
						componentlist.append([create_button(style=ButtonStyle.grey, emoji=str(i + 1) + "\u20E3", custom_id="fight" + str(i + 1))])
					else:
						componentlist[1].append(create_button(style=ButtonStyle.grey, emoji=str(i + 1) + "\u20E3", custom_id="fight" + str(i + 1)))
				componentlist2=[]
				componentlist2.append(create_actionrow(*componentlist[0]))
				if len(componentlist) > 1:
					componentlist2.append(create_actionrow(*componentlist[1]))
				await channel.send(embed=ldict["a"], components=componentlist2)
				# await msg.edit(components=componentlist2)

			elif color == discord.Colour(16776963):  # select stage for pve (from a quest)
				await ctx.edit_origin()
				num = int(compid[-1]) - 1  # number of reaction clicked
				level_data = get_achievements(user.id)
				if level_data == None:
					level_data = new_pve_user(user.id)
				quest_num = int(embed.footer.text)  # get quest id

				ldict = {"level": num, "user": user, "level_data": level_data}
				exec("a = PvE." + QUEST_LIST[quest_num][0] + "_prereqs(level,user,level_data)", globals(), ldict)

				if ldict["a"] == False:
					embed = discord.Embed(
						title="Prereqs not met",
						color=0xFF0000,
						description="Sorry {}, you do not meet the prerequisites for this stage. Please try a different stage or make sure you meet the prerequisites".format(
							user)
					)
					await channel.send(embed=embed)
					return

				# User does meet prereqs (Im not doing an else cause i dont want to indent again ok. shut up its already bad enough with all the ifs and elifs)
				exec("a = PvE." + QUEST_LIST[quest_num][0] + "_preview(level,user)", globals(), ldict)
				if type(ldict["a"]) != discord.Embed:
					await channel.send(str(ldict["a"]))
				else:
					msg = await channel.send(embed=ldict["a"], components=[create_actionrow(create_button(style=ButtonStyle.grey, emoji='✅', custom_id='fightcheck'),
												create_button(style=ButtonStyle.grey, emoji='❌', custom_id='fightcross'))])
				# await msg.add_reaction(u'\u2705')
				# await msg.add_reaction(u'\u274C')

			elif color == discord.Colour(16776964):  # reaction on confirmation screen
				await ctx.edit_origin()
				target = embed.description.split(" ")[0]
				target = target.replace("<@", "").replace(">", "")

				stage, quest = embed.footer.text.split(":")

				if str(user.id) == target:  # Person who clicked is indeed the intented user

					if compid == 'fightcheck':  # Check mark
						await message.delete()  # delete old message
						if self.check_battles(
								user):  # user is not in another battle (this includes pvp and other pve levels)
							# start (atleast try to start) pve
							fight = Battle(user, await self.client.fetch_user(BOT_ID), channel, self, True, int(quest),
										   int(stage))
							self.battles.append(fight)
							fightEmbed = discord.Embed(
								title="Choose Cards for PvP",
								colour=discord.Color.from_rgb(120, 120, 120),
								description="Select 3 cards to fight with.\nUse +select {ID} to pick a card.\nUse +remove to clear previous card selection"
							)

							msg = await channel.send(embed=fightEmbed)
							fight.msg = [msg, None]

							ldict = {"level": int(stage)}
							exec("a = PvE." + QUEST_LIST[int(quest)][0] + "_cards(level)", globals(), ldict)
							for card in ldict["a"]:
								fight.user_cards[1].append(card)
							fight.locks[1] = True
						else:
							await channel.send(
								"You are already involved in another battle. Please finish the other battle first. If you are somehow stuck try +surrender and if you are still stuck message TemmieGamerGuy#3754")
							return None

					elif compid == 'fightcross':  # X mark
						embed = discord.Embed(
							title="Fight Cancelled",
							color=0xFF0000,
							description="The fight has been cancelled")

						await message.edit(embed=embed)

	@commands.command(aliases=["Select"])
	async def select(self, ctx, ID):
		"""choose card for pvp. Only usuable when prompted by bot to use it"""
		ID = int(ID)
		if ID <= 0:  # ID must be greater than 0
			await ctx.send("Please input a valid ID")
			return

		battle, user = self.return_battle(ctx.message.author)

		# checks
		if battle == None:
			await ctx.send("You are not currently in a battle")
			return
		elif battle.phase != 0:
			await ctx.send("You are currently in battle and cannot change cards")
			return
		elif len(battle.user_cards[user - 1]) >= 3:
			await ctx.send(
				"You already have 3 characters selected. Use +remove to take a card off of the selection before trying to add another card")
			return
		elif battle.locks[user - 1]:
			await ctx.send("You can not change your selection after locking it in")
			return

		# add new character to list
		char_list = get_charinfo()
		new_char = char_list[ctx.message.author.id][ID - 1]

		if battle.check_duplicate(new_char, user):  # returns true if there is a duplicate card
			await ctx.send("This character is already selected")
			return

		await battle.add_char(new_char, user)

	@select.error
	async def select_error(self, ctx, error):
		embed = discord.Embed(
			title="Command Error",
			colour=discord.Color.from_rgb(255, 0, 0),
			description="The following error has occured when running the select command\n{}\nPlease message TemmieGamerGuy#3754 if this proves to be an issue".format(
				error)
		)

		await ctx.send(embed=embed)

	@commands.command()
	async def remove(self, ctx):
		battle, user = self.return_battle(ctx.message.author)
		if battle == None:
			await ctx.send("You are not currently in a battle")
			return
		elif battle.phase != 0:
			await ctx.send("You are currently in battle and cannot change cards")
			return
		elif len(battle.user_cards[user - 1]) <= 0:
			await ctx.send("You don't have any cards to remove")
			return
		elif battle.locks[user - 1]:
			await ctx.send("You can not change your selection after locking it in")
			return

		await battle.del_char(user)

	@commands.command(aliases=["PvE", "pve", "quest", "Quest"])
	async def adventure(self, ctx, page=0):
		player = ctx.author
		cards = None
		try:
			cards = get_charinfo()[player.id]
		except:
			card = None

		if cards is None or len(cards) < 3:
			await ctx.send("You can't start a fight if you don't have at least 3 cards")
			return

		embed = discord.Embed(
			title="Select Quest",
			color=0xFFFF02,
			description="Click on the corresponding reaction to start a Quest"
		)

		# add fields with adventures
		embed.add_field(name=":one: Sakuya's Dojo - Selectable difficulty", value="First Time Completion Bonus: None",
						inline=False)
		embed.add_field(name="---------------------------", value="---------------------------", inline=False)
		embed.add_field(name=":three: Scarlet Devil Mansion - Hard", value="First Time Completion Bonus: WIP",
						inline=False)
		embed.add_field(name=":four: Hakurei Shrine - Normal", value="First Time Completion Bonus: WIP", inline=False)
		embed.add_field(name=":five: Hakurei Shrine EX - Extra", value="First Time Completion Bonus: WIP", inline=False)
		embed.add_field(name=":six: Myouren Temple - Hard", value="First Time Completion Bonus: WIP", inline=False)

		msg = await ctx.send(embed=embed)
		components = [create_actionrow(create_button(style=ButtonStyle.grey, emoji='1\u20E3', custom_id='fight1'),
					   create_button(style=ButtonStyle.grey, emoji='3\u20E3', custom_id='fight3'),
					   create_button(style=ButtonStyle.grey, emoji='4\u20E3', custom_id='fight4'),
					   create_button(style=ButtonStyle.grey, emoji='5\u20E3', custom_id='fight5'),
					   create_button(style=ButtonStyle.grey, emoji='6\u20E3', custom_id='fight6'))]
		await msg.edit(components=components)

	# await msg.add_reaction("1\u20E3")
	# await msg.add_reaction("2\u20E3")
	# await msg.add_reaction("3\u20E3")
	# await msg.add_reaction("4\u20E3")
	# await msg.add_reaction("5\u20E3")
	# await msg.add_reaction("6\u20E3")

	@commands.command(aliases=['PvP', 'challenge', 'battle', "pvp"])
	async def fight(self, ctx, user: discord.Member):
		"""Start a fight with another player by typing +fight @user"""
		sender = ctx.message.author
		cards = get_charinfo()
		trades = get_tradeinst()
		if user is sender:
			await ctx.send("You cannot fight against your self")
			return
		elif user.id == BOT_ID:
			await self.adventure(ctx)
			return

		owned_cards = cards.get(user.id)
		your_cards = cards.get(ctx.author.id)

		if your_cards == None or len(your_cards) < 3:
			await ctx.send("You can't start a fight if you don't have at least 3 cards")
			return

		if owned_cards == None or len(owned_cards) < 3:
			await ctx.send("Your requested opponent does not have 3 cards")
			return

		# add before fight checks (fight on going..etc.)

		trade_embed = discord.Embed(
			title="Start Fight",
			colour=discord.Color.from_rgb(255, 255, 1),
			description="<@{}>, <@{}> has requested to fight against you. React with \u2705 to start the battle.".format(
				user.id, sender.id)
		)

		msg = await ctx.send(embed=trade_embed)
		components = [create_actionrow(create_button(style=ButtonStyle.grey, emoji='✅', custom_id='fightcheck'))]
		await msg.edit(components=components)

	# await msg.add_reaction(u'\u2705')

	@fight.error
	async def fight_error(self, ctx, error):
		embed = discord.Embed(
			title="Command Error",
			colour=discord.Color.from_rgb(255, 0, 0),
			description="Failed to start fight due to following error\n{}\nPlease send the error message to @TemmieGamerGuy#3754 if it is a serious issue".format(
				error)
		)

		await ctx.send(embed=embed)

	@commands.command()
	async def fight_test(self, ctx, user: discord.Member):
		if ctx.message.author.id != OWNER_ID:
			await ctx.send("Test command for bot owner only")
			return
		sender = ctx.message.author
		cards = get_charinfo()
		battle = Battle(sender, user, ctx.channel, self)
		self.battles.append(battle)

		p1_chars = [cards[sender.id][0], cards[sender.id][1], cards[sender.id][2]]
		p2_chars = [cards[user.id][0], cards[user.id][1], cards[user.id][2]]

		fightEmbed = discord.Embed(
			title="Choose Cards for PvP",
			colour=discord.Color.from_rgb(120, 120, 120),
			description="Select 3 cards to fight with.\nUse +select {ID} to pick a card.\nUse +remove to clear previous card selection"
		)

		msg1 = await battle.user1.send(embed=fightEmbed)
		msg2 = await battle.user2.send(embed=fightEmbed)

		battle.msg = [msg1, msg2]

		for i in p1_chars:
			await battle.add_char(i, 1)

		for i in p2_chars:
			await battle.add_char(i, 2)

		battle.locks[0] = True
		battle.locks[1] = True

		await battle.start()


class Battle(spellcard_func.Spells):
	def __init__(self, user1, user2, channel, PvP, PvE=False, quest=0, stage=0):
		"""ngl I just kept adding stuff on and it ended up being this mess. Sorry to my future self"""
		# I hate this
		self.user1 = user1
		self.user2 = user2
		self.users = [self.user1, self.user2]

		self.channel = channel  # The channel the battle was started in
		self.PvP = PvP  # PvP Class

		if PvE:
			self.bg = Image.open(pve_bg + "//" + QUEST_LIST[quest][2])
		else:
			self.bg = Image.open(bg + "//" + random.choice(os.listdir(bg)))

		# Only used in pve
		self.pve = PvE
		self.quest = quest
		self.stage = stage

		super().__init__()  # sets up all other non discord related variables

	def check_duplicate(self, char, id):
		for card_id in self.user_cards[id - 1]:
			if char[10] == card_id[10]:
				return True
		return False

	async def add_char(self, char, id):
		self.user_cards[id - 1].append(char)
		new_embed = self.msg[id - 1].embeds[0]
		new_embed.add_field(name="Character {}: ".format(len(new_embed.fields) + 1),
							value=str(char[2]) + "	| Lv" + str(char[3]) + "	| " + str(char[5]) + "	| " + str(
								char[6]) + "	| " + str(char[7]) + "	| " +
								  ["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★", "★★★★★★"][char[4] - 1], inline=False)

		if len(self.user_cards[id - 1]) >= 3:  # Check if user has 3 cards selected
			new_embed.color = discord.Color.from_rgb(0, 255, 1)
			new_embed.description = "Press the \u2705 reaction to confirm your card choice"

			await self.msg[id - 1].delete()

			if id == 1:
				msg = await self.user1.send(embed=new_embed)
			else:
				msg = await self.user2.send(embed=new_embed)

			self.msg[id - 1] = msg
			components = [create_actionrow(create_button(style=ButtonStyle.grey, emoji='✅', custom_id='fightcheck'))]
			await msg.edit(components=components)

		else:
			await self.msg[id - 1].edit(embed=new_embed)

	async def del_char(self, id):
		del self.user_cards[id - 1][-1]
		new_embed = self.msg[id - 1].embeds[0]
		new_embed.remove_field(-1)
		new_embed.description = "Select 3 cards to fight with.\nUse +select {ID} to pick a card.\nUse +remove to clear previous card selection\nUse +surrender to quit the fight (This can be used durring the fight as well)"
		new_embed.color = discord.Color.from_rgb(120, 120, 120)
		await self.msg[id - 1].edit(embed=new_embed)

	async def start(self):
		self.locks = [False, False]  # reset locks
		self.phase = 1  # battle phase

		img = self.generate_battle_img()
		self.image = img
		imgByteArr = io.BytesIO()
		img.save(imgByteArr, format='PNG')
		imgByteArr.seek(0)

		img_file = discord.File(imgByteArr, filename="image.png")

		if self.pve:
			embed = discord.Embed(
				title="{} vs Encounter".format(self.user1),
				colour=discord.Color.from_rgb(255, 165, 0),
				description="Either user may use +surrender to quit the fight at anytime"
			)
		else:
			embed = discord.Embed(
				title="{} vs {}".format(self.user1, self.user2),
				colour=discord.Color.from_rgb(255, 165, 0),
				description="Either user may use +surrender to quit the fight at anytime"
			)
		embed.set_image(url="attachment://image.png")

		i = 0
		for player in self.user_cards:
			if self.pve and i == 1:
				embed.add_field(name="Encounter", value="---------------------", inline=False)
			else:
				embed.add_field(name=self.users[i], value="---------------------", inline=False)
			for card in player:  # creates instance of card
				if card is None:
					self.inst_card[i].append([0, 0, 0, False, ["dead"], 0, 0, 0, [0, 0]])
					continue
				try:
					spell = Spell_cards[card[0]]  # temp until spell v2 is ready
				except:
					spell = ["Generic Spell Card", "single_target_dmg", 100, True, 10,
							 "A spell given to characters without a spell card. Deals damage to a single target", 0.4]
				self.inst_card[i].append([card[5], card[6], card[7], False, [], card[2], spell, card[5], [0, 0]])
				# 0 = hp,1 = atk, 2 = spd,3 = defending, 4 = statuses, 5 = nickname, 6 = spell card, 7 = Max hp, 8 = status value
				embed.add_field(name=card[2], value="{}/{}".format(card[5], card[5]), inline=True)
				self.total_hp += card[5]
				self.team_hp[i] += card[5]
			i += 1

		embed.add_field(name="Battle Log: ", value="Battle Started", inline=False)
		self.battle_log.append("Battle Started")

		msg = await self.channel.send(file=img_file, embed=embed)
		self.battle_msg = msg

		# battle command

		await self.next_command(0)
		if not self.pve:  # only send msg to user 2 if its not a pve battle
			await self.next_command(1)

	def select_target(self, id):
		enemy = 1 - id
		enemy_cards = self.user_cards[enemy]
		enemy_cards_inst = self.inst_card[enemy]
		reactions = ["🇦", "🇧", "🇨"]
		return_reactions = []

		embed = discord.Embed(
			title="Select Target",
			description="React to the corresponding emoji to select the target",
			color=discord.Colour(7895164)
		)
		for i, card in enumerate(enemy_cards_inst):
			if "dead" not in card[4]:  # Character is not dead
				return_reactions.append(reactions[i])
				embed.add_field(name=reactions[i], value=card[5], inline=False)

		return embed, return_reactions

	async def next_command(self, id, numcomp=None, message=None):
		cards = self.inst_card[id]

		'''try:
			while "dead" in cards[self.player_pointer[id]][4]:
				# keep incrementing until pointed char is not dead or we go beyond the list (No chars alive left to do actions)
				self.player_pointer[id] += 1
		except Exception as e:
			pass'''
		if numcomp is not None:
			if numcomp[0]['components'][0]['style'] in (3, 4) and numcomp[1]['components'][0]['style'] in (3, 4) and numcomp[2]['components'][0]['style'] in (3, 4):  # third command already chosen
				self.locks[id] = True
				self.msg[id] = message

				if self.locks[0] == self.locks[1]:  # both player have selected all their moves
					await self.act_turn()  # starts turn
					await self.end_turn()  # ends turn

					if self.winner is not None:  # there is a winner
						await self.PvP.end_battle(self, self.users[self.winner])

					else:  # Fight is still ongoing

						# send next set of commands
						embed = self.generate_command_embed(0)
						complist = []
						cards = self.inst_card[0]

						for i, card in enumerate(cards):
							if "dead" in card[4]:
								complist.append(create_actionrow(create_button(style=ButtonStyle.red, label='  '),
																 create_button(style=ButtonStyle.red, label='  '),
																 create_button(style=ButtonStyle.red, label='  ')))
							else:
								complist.append(create_actionrow(
									create_button(style=ButtonStyle.grey, emoji='⚔', custom_id='attack' + str(i)),
									create_button(style=ButtonStyle.grey, emoji='🛡', custom_id='shield' + str(i)),
									create_button(style=ButtonStyle.grey,
												  emoji=self.PvP.client.get_emoji(865682533236080652),
												  custom_id='spell1' + str(i))))
						if self.msg[0] is not None:
							await self.msg[0].edit(embed=embed, components=complist)
							self.msg[0] = message
						else:
							msg = await self.users[0].send(embed=embed)
							self.msg[0] = msg
						if not self.pve:
							embed = self.generate_command_embed(1)
							complist = []
							cards = self.inst_card[1]

							for i, card in enumerate(cards):
								if "dead" in card[4]:
									complist.append(create_actionrow(create_button(style=ButtonStyle.red, label='  '),
																	 create_button(style=ButtonStyle.red, label='  '),
																	 create_button(style=ButtonStyle.red, label='  ')))
								else:
									complist.append(create_actionrow(
										create_button(style=ButtonStyle.grey, emoji='⚔', custom_id='attack' + str(i)),
										create_button(style=ButtonStyle.grey, emoji='🛡', custom_id='shield' + str(i)),
										create_button(style=ButtonStyle.grey,
													  emoji=self.PvP.client.get_emoji(865682533236080652),
													  custom_id='spell1' + str(i))))
							if self.msg[1] is not None:
								await self.msg[1].edit(embed=embed, components=complist)
								self.msg[1] = message
							else:
								msg = await self.users[1].send(embed=embed)
								self.msg[1] = msg

						return

				if self.pve:
					await self.users[id].send("Waiting for AI")
					ldict = {"moves": self.actionBar, "level": int(self.stage), "chars": self.inst_card,
							 "points": self.points}
					exec("a = PvE." + QUEST_LIST[int(self.quest)][0] + "_AI(moves,level,points,chars)", globals(), ldict) #wtf is this bs
					self.actionBar.extend(ldict["a"])

					await self.act_turn()  # starts turn
					await self.end_turn()  # ends turn

					if self.winner is not None:  # there is a winner
						await self.PvP.end_battle(self, self.users[self.winner])

					else:  # Fight is still ongoing

						# send next set of commands

						embed = self.generate_command_embed(0)
						complist = []

						for i, card in enumerate(cards):
							if "dead" in card[4]:
								complist.append(create_actionrow(create_button(style=ButtonStyle.red, label='  '),
																 create_button(style=ButtonStyle.red, label='  '),
																 create_button(style=ButtonStyle.red, label='  ')))
							else:
								complist.append(create_actionrow(
									create_button(style=ButtonStyle.grey, emoji='⚔', custom_id='attack' + str(i)),
									create_button(style=ButtonStyle.grey, emoji='🛡', custom_id='shield' + str(i)),
									create_button(style=ButtonStyle.grey,
												  emoji=self.PvP.client.get_emoji(865682533236080652),
												  custom_id='spell1' + str(i))))
						if message is not None:
							await message.edit(embed=embed, components=complist)
							self.msg[0] = message
						else:
							msg = await self.users[0].send(embed=embed)
							self.msg[0] = msg

						return
				else:
					await self.users[id].send("Waiting for other player")

				# await self.users[1-id].send("The other player have finished their selection")
				return

		if numcomp is None and message is None:
			embed = self.generate_command_embed(id)
			complist = []

			for i, card in enumerate(cards):
				if "dead" in card[4]:
					complist.append(create_actionrow(create_button(style=ButtonStyle.red, label='  '),
													 create_button(style=ButtonStyle.red, label='  '),
													 create_button(style=ButtonStyle.red, label='  ')))
				else:
					complist.append(create_actionrow(
						create_button(style=ButtonStyle.grey, emoji='⚔', custom_id='attack' + str(i)),
						create_button(style=ButtonStyle.grey, emoji='🛡', custom_id='shield' + str(i)),
						create_button(style=ButtonStyle.grey,
									  emoji=self.PvP.client.get_emoji(865682533236080652),
									  custom_id='spell1' + str(i))))
			if message is not None:
				await message.edit(embed=embed, components=complist)
				self.msg[id] = message
			else:
				msg = await self.users[id].send(embed=embed, components=complist)
				self.msg[id] = msg

	def generate_command_embed(self, id):
		# prompt for turn choice (attack, defend, spellcard)
		command_embed = discord.Embed(
			title="Choose actions",
			description="Power: {} <:power:865682549543141437>".format(self.points[id]),
			color=discord.Color.from_rgb(120, 120, 121 + self.player_pointer[id])  # change later
		)

		command_embed.add_field(name="\u2694 - Attack", value="A simple attack against an opponents card", inline=False)
		command_embed.add_field(name="\U0001F6E1 - Defend",
								value="Defend against enemy attacks. You take half the damage and gain double the power",
								inline=False)
		for inst_card in self.inst_card[id]:
			if "dead" in inst_card[4]:
				continue
			command_embed.add_field(
				name=inst_card[5] + ": <:card:865682533236080652> - {} - {}<:power:865682549543141437>.".format(
					inst_card[6][0],
					inst_card[6][2]),
				value=inst_card[6][5], inline=False)
		return command_embed

	def generate_battle_img(self):
		im_bg = self.bg
		im_bg = im_bg.resize((1000, 800))  # fuck img ratios am i rite

		hp_bar = Image.open(hud + "//Bar2.png")
		# fill = Image.open(hud+"//fill.png")
		# fill = fill.resize((154,19))

		fill = Image.new("RGBA", (156, 19), (0, 0, 0, 255))

		new_width = 174
		m = 156 / new_width
		xshift = abs(m) * 156
		coeffs = (1, m, -18, 0, 1, 0)
		fill = fill.transform((new_width, 19), Image.AFFINE, coeffs)

		# hp_bar.paste(fill,(39,3,213,22),fill)

		y = 50
		for i, player in enumerate(self.user_cards):
			x = 100
			for j, card in enumerate(player):
				try:
					if not card[1].startswith('http'):
						im = Image.open(char_folder + "//" + card[0] + "//" + card[1])
					else:
						req = Request(card[1], headers={'User-Agent': 'Mozilla/5.0'})
						im = Image.open(urlopen(req))
				except:
					x += 300
					continue
				width, height = im.size
				new_height = int(200 * (height / width))
				if new_height > 300:
					new_height = 300
				im = im.resize((200, new_height))

				# create hp bar for character
				"""
				hp_bar_new = hp_bar.copy()
				fill_new = fill.copy()
				
				try:
					hp = self.inst_card[i][j][0]
				except Exception:
					hp = card[5]
				
				percent = 1 - (hp / card[5])
				size = min(math.ceil(percent * new_width),174)
				"""

				# fill_new = fill_new.crop((174-size,0,174,19))#crops image
				# hp_bar_new.paste(fill_new,((39+174)-size,3,213,22),fill_new)#pastes image

				if y != 50:  # could potentially cause problems if theres a super long image but wow I do not care enough to add another variable in to make sure this never happens
					# only on second outer loop
					y = 800 - (new_height + 50)
					self.card_size[1].append([width, height])

				# HP bar removed since not used anymore
				# im_bg.paste(hp_bar_new,(x-10,y+new_height,x+210,y+new_height+25),hp_bar_new)#paste below

				else:  # only on first outer loop
					self.card_size[0].append([width, height])

				# HP bar removed since not used anymore
				# im_bg.paste(hp_bar_new,(x-10,y-25,x+210,y),hp_bar_new)#paste above

				try:
					im_bg.paste(im, (x, y, x + 200, y + new_height), im)  # transparent image
				except Exception as e:
					im_bg.paste(im, (x, y, x + 200, y + new_height))  # non transparent image

				x += 300
			y = -1

		return im_bg

	async def act_turn(self):
		self.actionBar = sorted(self.actionBar, key=lambda x: (x[3], -x[0][2]))
		# sorts by priority first. Than speed
		for action in self.actionBar:
			await asyncio.sleep(ACTION_DELAY)
			await self.act_move(action)

	async def end_turn(self):
		self.actionBar = []  # reset action bar

		if self.is_game_over(0):  # check if all characters of a single player are dead
			self.winner = 1  # sets player as the winner of the game
		elif self.is_game_over(1):
			self.winner = 0  # sets player as the winner of the game

		for player in self.inst_card:
			for card in player:
				card[3] = False  # reset defending status

				if "stop_time" in card[4]:
					card[4].remove("stop_time")

				# category 1 status
				if "burn" in card[4]:
					card[0] -= card[7] // 10  # lose 10% of max hp
					self.battle_log.append("{} took {} burn damage".format(card[5], card[7] // 10))
					card[8][0] -= 1
					if card[8][0] <= 0:
						card[4].remove("burn")
						self.battle_log.append("{} is no longer burning".format(card[5]))

				elif "frozen" in card[4]:
					card[8][0] -= FROZEN_RECOVERY
					if card[8][0] <= 0:
						card[4].remove("frozen")
						self.battle_log.append("{} is no longer frozen".format(card[5]))

				elif "stunned" in card[4]:
					card[8][0] -= STUN_RECOVERY
					if card[8][0] <= 0:
						card[4].remove("stunned")
						self.battle_log.append("{} is no longer stunned".format(card[5]))

				elif "blind" in card[4]:
					card[8][0] -= 1
					if card[8][0] <= 0:
						card[4].remove("blind")
						self.battle_log.append("{} is no longer blind".format(card[5]))

				# category 2 status
				if "vamp" in card[4]:
					card[8][1] -= 1
					if card[8][1] <= 0:
						card[4].remove("vamp")
						self.battle_log.append("{} no longer has vamp".format(card[5]))

				elif "rage" in card[4]:
					card[8][1] -= 1
					if card[8][1] <= 0:
						card[4].remove("rage")
						self.battle_log.append("{} is no longer enraged".format(card[5]))
					else:
						atkup = int(card[2] * 0.1)
						card[2] += atkup
						self.battle_log.append(
							"{}s attack went up by {}[10%] due to rage status".format(card[5], atkup))

				elif "phantom" in card[4]:
					card[8][1] -= 1
					if card[8][1] <= 0:
						card[4].remove("phantom")
						self.battle_log.append("{} no longer has the status phantom".format(card[5]))

				# reduce timers on non restricted categories
				remove_list = []
				add_list = []
				for i in card[8][2:]:  # loop through all timed effects not in main categories

					# non main statuses [time, name, effect]

					# effects not in restriction categories
					if i[1] == "hp_regen":
						hp_regen = int(card[7] * i[2])
						if card[0] + hp_regen > card[7]:  # hp regen cant overheal but shouldnt remove overheal hp
							hp_regen = card[7] - card[1]
							if hp_regen < 0: hp_regen = 0
						card[0] += hp_regen

						if hp_regen > 0:
							self.battle_log.append("{} regained {} HP".format(card[5],
																			  hp_regen))  # Dont show this message if no healing is done

					elif i[1] == "life_steal":
						caster = i[2]
						dmg = card[7] // 20
						if "dead" in caster[4]:  # If the character who casted life_steal is dead. Remove the status
							try:
								card[4].remove(i[1])  # remove status emoji
							except:
								pass
							remove_list.append(i)
							self.battle_log.append("{} no longer has the status life steal".format(card[5]))
						else:
							card[0] -= dmg
							caster[0] += dmg
							self.battle_log.append("{} stole {} HP from {}".format(caster[5], dmg, card[5]))

					elif i[1] == "cursed":
						effect = random.choice(NEGATIVE_EFFECTS)
						add_list.append([card, effect, 0, 0])

					i[0] -= 1  # subtract from turn counter
					if i[0] <= 0 and i[0] > -10:  # remove status if its at 0 (-10 and below means its permanent)
						try:
							card[4].remove(i[1])  # remove status emoji
						except:
							pass
						remove_list.append(i)  # add to remove list
						self.battle_log.append("{} no longer has the status {}".format(card[5], i[1]))

				for j in remove_list:
					try:
						card[8].remove(j)  # remove status from timed list
					except:
						print("Failed to remove status: {}".format(j))
					# Undo status effect

					# buffs
					if j[1] == "hp_up":  # dont remove bonus hp
						pass
					elif j[1] == "atk_up":
						card[1] /= (1 + j[2])
					elif j[1] == "spd_up":
						card[1] /= (1 + j[2])
					# debuffs
					elif j[1] == "hp_down":
						card[7] /= (1 - j[2])
					elif j[1] == "atk_down":
						card[1] /= (1 - j[2])
					elif j[1] == "spd_down":
						card[2] /= (1 - j[2])

				for k in add_list:
					self.spell_status(k[0], k[1], k[2], k[3])

				if card[0] <= 0:  # has no hp left (dies)
					card[0] = 0  # set hp to 0 (Shouldnt be displayed as a negative)
					if "dead" not in card[4]:  # Dont add dead again if character is already dead
						if "life" in card[4]:
							card[0] = int(card[7] * 0.5)
							self.battle_log.append("{} came back to life due to the status life".format(card[5]))
						else:
							# clear statuses and set as dead
							card[4] = ["dead"]
							card[8] = [0, 0]
							self.battle_log.append("{} has died".format(card[5]))

		# any end of turn actions go here
		if self.is_game_over(0):
			self.winner = 1
		elif self.is_game_over(1):
			self.winner = 0

		"""
		img = self.generate_battle_img()
		self.image = img
		imgByteArr = io.BytesIO()
		img.save(imgByteArr, format='PNG')
		imgByteArr.seek(0)
		
		img_file=discord.File(imgByteArr,filename="image.png")
		"""

		self.turn += 1
		self.battle_log.append("----------Turn {}----------".format(self.turn))

		if self.reload_image:  # only update image when necessary
			self.reload_image = False

			img = self.generate_battle_img()
			imgByteArr = io.BytesIO()
			img.save(imgByteArr, format='PNG')
			imgByteArr.seek(0)

			img_file = discord.File(imgByteArr, filename="image.png")
			await self.update_log(img_file)
		else:
			await self.update_log()  # removed updating image cause it seems to cause problems

		# remove locks
		self.locks[0] = False
		self.locks[1] = False

		# resets pointers after turn
		self.player_pointer[0] = 0
		self.player_pointer[1] = 0

	async def act_move(self, move):
		# move => [card, action, target, priority, user (owner of card)]
		# card => [#0 = hp,1 = atk, 2 = spd,3 = defending, 4 = statuses, 5 = nickname, 6 = spell card, 7 = Max hp, 8 = status value]

		# check statuses

		if "stop_time" in move[0][4]:
			if move[3] == 69420:
				move[0][4].remove("stop_time")
			else:
				move[3] = 69420
				self.actionBar.append(move)  # add it back to the end
				self.battle_log.append("{}'s time is stopped and cannot do anything".format(move[0][5]))
				await self.update_log()
				return

		if "frozen" in move[0][4]:  # character is frozen
			if move[0][8][0] <= 0:  # No longer frozen
				move[0][4].remove("frozen")
				move[0][8][0] = 0
				self.battle_log.append("{} took too much damage and is no longer frozen".format(move[0][5]))
			else:
				self.battle_log.append("{} is frozen and can not move".format(move[0][5]))
				move[0][3] = True
		elif "stunned" in move[0][4]:  # character is stunned
			if move[0][8][0] <= 0:  # No longer stunned
				move[0][4].remove("stunned")
				move[0][8][0] = 0
				self.battle_log.append("{} took too much damage and is no longer stunned".format(move[0][5]))
			else:
				self.battle_log.append("{} is stunned and can't attack".format(move[0][5]))

		elif "dead" in move[0][4]:  # skip action if dead
			# clear all other buffs
			move[0][4] = ["dead"]
			move[0][8] = [0, 0]

		else:  # No move attack preventing statuses

			if "blind" in move[0][4] and move[1] != "def":  # character is blind (and not defending)
				move[2] = (move[2][0], random.randint(0, 2))  # chose random target (not player)
				self.battle_log.append("{} is blind and cannot see where they're attacking".format(move[0][5]))
			elif "rage" in move[0][4]:
				move[1] = "atk"  # Force player to attack
				move[2] = (1 - move[4], random.randint(0, 2))  # chose random enemy target
				self.battle_log.append("{} is enraged and is attacking randomly".format(move[0][5]))

			if move[1] == "atk":  # attack

				if "multihit" in move[0][4]:
					for i in move[0][8][2:]:
						if i[1] == "multihit":  # find multihit in list
							for j in range(i[2]):  # loop effect amount of times
								dmg, target = self.attack_target(move)  # Attack more times for multihit
				else:
					dmg, target = self.attack_target(move)

				if "loaded" in move[0][4]:
					for i in move[0][8][2:]:
						if i[1] == "loaded":  # Find loaded in list
							move[0][4].remove("loaded")
							move[0][8].remove(i)
							break

			elif move[1] == "def":  # defend
				move[0][3] = True
				self.battle_log.append("{} has taken a defensive position".format(move[0][5]))

			elif move[1] == "spell":  # spell (Just in case I add another move later on)
				exec("self." + move[0][6][1] + "(move)")
			else:
				pass

		await self.update_log()

	async def update_log(self, img=None):  # Updates battle log to whats currently in the Battle_log list
		# create new embed for updating
		if self.pve == True:
			embed = discord.Embed(
				title="{} vs Encounter".format(self.user1),
				colour=discord.Color.from_rgb(255, 165, 0)
			)
		else:
			embed = discord.Embed(
				title="{} vs {}".format(self.user1, self.user2),
				colour=discord.Color.from_rgb(255, 165, 0)
			)

		embed.set_image(url="attachment://image.png")
		i = 0
		for player in self.inst_card:
			if self.pve == True and i == 1:
				embed.add_field(name="Encounter", value="---------------------", inline=False)
			else:
				embed.add_field(name=self.users[i], value="---------------------", inline=False)
			j = 0
			for card in player:
				if card[6] == 0:  # invalid empty character. Dont display
					continue
				emojis = ""
				for emote in card[4]:
					emojis += STATUS_EMOJI[emote]
				embed.add_field(name=emojis + card[5], value="{}/{}".format(card[0], card[7]), inline=True)
				j += 1
			i += 1

		log = ""
		for line in self.battle_log[
					-LOG_SIZE:]:  # get last x values of battle_log and loop through them where x is LOG_SIZE (started off as 10)
			log += line + "\n"
		embed.add_field(name="Battle Log: ", value=log, inline=False)

		if img == None:
			await self.battle_msg.edit(embed=embed)
		else:
			msg = await self.channel.send(embed=embed, file=img)
			await self.battle_msg.delete()
			self.battle_msg = msg

	def is_game_over(self, target):
		for card in self.inst_card[target]:
			if "dead" not in card[4]:  # return False if any character is alive
				return False
		return True

	def attack_target(self, move):
		# move => [0 = card, 1 = action, 2 = target, 3 = priority, 4 = user (owner of card) (int [0 or 1])]
		# card (pvp) => [#0 = hp,1 = atk, 2 = spd,3 = defending, 4 = statuses, 5 = nickname, 6 = spell card, 7 = Max hp, 8 = status value]

		target_player = 1 - move[4]  # get other player

		target_card = self.inst_card[target_player][move[2][1]]

		card = move[0]  # card of attacker

		if "charming" in target_card[4]:  # Target is charming
			target_card = move[0]  # change target to self

		# calculates dmg to be dealt. multiplied by Random value between 0.8 and 1.2
		if "phantom" in target_card[4]:
			if random.random() > 0.5:  # 50% change to dodge if status phantom is on target. Guarding is ignored when phantom status is on
				dmg = 0
			else:  # If def user have phantom and attack hits apply def as usual (This also applies when both users have phantom)
				dmg = int((move[0][1] / DMG_MOD) * (1 - 0.5 * target_card[3]) * random.uniform(0.8, 1.2))
		elif "phantom" in move[0][4]:  # If attacking user has phantom ignore their def
			dmg = int((move[0][1] / DMG_MOD) * random.uniform(0.8, 1.2))
		else:  # Normal attack
			dmg = int((move[0][1] / DMG_MOD) * (1 - 0.5 * target_card[3]) * random.uniform(0.8, 1.2))

		if "darkness_power" in card[4]:  # attacker has darkness power status
			if "blind" in target_card[4] or "stunned" in target_card[4] or "sleep" in target_card[4]:
				dmg *= 2  # double the damage
			self.spell_status(target_card, "blind", 3)  # Apply blind status

		elif "stun_power" in card[4]:
			if "blind" in target_card[4] or "stunned" in target_card[4] or "sleep" in target_card[4]:
				dmg *= 2  # double the damage
			self.spell_status(target_card, "stunned", 0.75)  # Apply stun status

		Attacker_multiplier = 1
		Defender_multiplier = 1

		if "strawberry" in card[4]:
			for status in card[4]:
				if status == "strawberry":
					Attacker_multiplier += 1
					dmg *= 1.3

		if "strawberry" in target_card[4]:
			for status in card[4]:
				if status == "strawberry":
					Defender_multiplier += 1
					dmg *= 0.85

		target_card[0] -= dmg
		try:
			percent_lost = dmg / target_card[7]
		except:
			percent_lost = 0
		target_card[8][0] -= percent_lost
		target_card[8][1] -= percent_lost

		if dmg == 0:
			self.battle_log.append("{} has dodged the attack from {}".format(target_card[5], move[0][5]))
		else:
			self.battle_log.append("{} has dealt {} damage to {}".format(move[0][5], dmg, target_card[5]))

		if target_card[0] <= 0:  # has no hp left (dies)
			target_card[0] = 0  # set hp to 0 (Shouldnt be displayed as a negative)
			if "dead" not in target_card[4]:  # Dont add dead again if character is already dead
				if "life" in target_card[4]:
					target_card[0] = int(target_card[7] * 0.5)
					self.battle_log.append("{} came back to life due to the status life".format(target_card[5]))
				else:
					target_card[4].append("dead")  # set status as dead
					self.battle_log.append("{} has died".format(target_card[5]))
			if self.is_game_over(target_player):  # check if all characters of the player are now dead
				self.actionBar = []  # remove all other actions. This makes the action go to self.end_turn
				self.winner = move[4]  # sets player as the winner of the game

		self.points[move[4]] += int(
			(dmg / self.total_hp) * 600 * GIVEN_MOD * Attacker_multiplier)  # attacker gains points
		self.points[target_player] += int((dmg / self.total_hp) * 600 * (1 + 1 * target_card[
			3]) * TAKEN_MOD * Defender_multiplier)  # defender gains points (double points if player was defending)

		if "vamp" in card[4]:  # Attacker has vamp status
			hp_regen = dmg // 4
			if card[0] + hp_regen > card[7]:  # regen cant overheal but shouldnt remove overheal hp
				hp_regen = card[7] - card[1]
				if hp_regen < 0: hp_regen = 0
			card[0] += hp_regen
			if hp_regen > 0:
				self.battle_log.append("{} regained {} HP from vamp".format(card[5],
																			hp_regen))  # Dont show this message if no healing is done

		return dmg, target_card


def setup(client):
	class_obj = PvP(client)
	client.add_cog(class_obj)
	put_class(class_obj)
