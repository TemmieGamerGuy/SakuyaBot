import random

print("Loaded Spellcard_func.py")
#Spell in these category's have a duration
CATEGORY_1 = ["burn", "frozen", "stunned", "blind"]
CATEGORY_2 = ["vamp", "rage","phantom"]


#move => [0 = card, 1 = action, 2 = target, 3 = priority, 4 = user (owner of card) (int [0 or 1])]
#card => [#0 = hp,1 = atk, 2 = spd,3 = defending, 4 = statuses, 5 = nickname, 6 = spell card, 7 = Max hp, 8 = status value]

class Spells():
	def __init__(self):
		self.actionBar = []#List of actions to do this turn
		self.user_cards = [[],[]]#0 = player 1, 1 = player 2
		self.inst_card = [[],[]]#stores current information about cards
		#0 = HP, 1 = Atk, 2 = Spd, 3 = defending, 4 = inflicted status, 5 = nickname
		
		self.points = [0,0]#stores amount of spell card points each player has
		self.locks = [False,False]#locks actions player can take if set to true (edited during battle, keep false here)
		self.phase = 0#keep track of the current phase. 0 = prep, 1 = battle, 2 = end scene
		self.msg = []#0= player 1, 1 = player 2
		
		self.battle_msg = None#The message the battle is on
		self.card_size = [[],[]]#keeps the dimention of the card for future use
		self.battle_log = []#keeps the battle log. Will only print out the latest 10 entries
		self.image = None#image put on battle embed
		self.player_pointer = [0,0]#pointers to the current action the game is waiting on
		self.waiting_target = [None,None]#waiting for player to select target. Stores values until then cause im lazy
		self.total_hp = 0#stores max total hp of all characters in battle (used for points calculation)
		self.team_hp = [0,0]
		self.winner = None#stores who the winner of the game is
		self.turn = 1
		
		self.reload_image = False#determines if there's a need to recreate the battle image

	def spell_dmg(self,target,dmg,def_ignore=False):#target = card, dmg = well dmg u dumb dumb, def_ignore will ignore def if set to true
		
		def_ignore = not def_ignore#swaps it so it works easily with math.
		dmg_dealt = int(dmg * (1-(0.5*target[3]*def_ignore)) * random.uniform(0.8,1.2))#whole numbers only plox
		target[0] -= dmg_dealt
		percent_lost = dmg_dealt/target[7]
		target[8][0] -= percent_lost
		target[8][1] -= percent_lost
		
		if target[0] <= 0:
			target[0] = 0
			if "dead" not in target[4]:#Dont add dead again if character is already dead
				target[4].append("dead")#set status as dead
			
		return dmg_dealt

	def spell_status(self,target,effect,duration=-1,value = 0):#target = card, effect = string which holds the effect, #duration = the num of turns it lasts
		if "dead" in target[4]:#dont apply statuses to dead characters
			return False
		
		#Check if effect is in cat 1 or cat 2. Remove all other effects from the same category
		check_list = target[4].copy()
		if effect in CATEGORY_1:#Category 1 (Negative statuses)
			target[8][0] = duration
			
			#Remove all other category 1 effects
			for eff in check_list:
				if eff in CATEGORY_1:
					target[4].remove(eff)
					
		elif effect in CATEGORY_2:#Category 2 (Positive statuses)
			target[8][1] = duration
			
			#Remove all other category 2 effects
			for eff in check_list:
				if eff in CATEGORY_2:
					target[4].remove(eff)
		
		else:#Non restricted category spell
			target[8].append([duration,effect,value])
		
		#Add effect
		target[4].append(effect)
		
		return True
		
	def get_ownId(self,name,ownerid):
		for i,card in enumerate(self.inst_card[ownerid]):
			if card[5] == name:
				return i
		
		return None
		
	def multi_target(self,targets):
		#targets to hit
		if targets == 3:
			target = [0,1,2]
		if targets > 3:#If 4 or larger it allowes repeat targets
			target = []
			for i in range(targets):
				num = random.randint(0,2)
				target.append(num)
		else:#If smaller than 3 no repeats should be allowed
			target = []
			while targets > 0:#randomly select targets (assumes random if not 3)
				num = random.randint(0,2)
				if num not in target: 
					target.append(num)
					targets -= 1
		return target
		
	def any_target(self,targets):
		#targets to hit
		target = []
		for i in range(targets):
			player = random.randint(0,1)
			num = random.randint(0,2)
			target.append([player,num])
			
		return target
		
	def multi_target_dmg(self,move,combo=False):
		targets = move[0][6][7]
		power = move[0][6][6]
		try:
			ignore_def = move[0][6][8]
		except:
			ignore_def = False
		enemy = 1 - move[4]#enemy id
		
		target = self.multi_target(targets)
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		
		for i in target:
			target_card = self.inst_card[enemy][i]

			num = 0
			counter = 0
			while "dead" in target_card[4]:
				if counter > 3:
					break
				counter += 1
				num = (num+1)%3 #select next character if current selection is dead.
				target_card = self.inst_card[enemy][num]
			dmg = self.spell_dmg(target_card,move[0][1]*power,ignore_def)
			message.append("{} took {} damage".format(target_card[5],dmg))
		
		if combo:
			return message[1:]
		else:
			self.battle_log.extend(message)
	
	def single_target_dmg(self,move,combo=False):#If true there is another component to the spell and will return message instead of posting it
		target = move[2][1]
		power = move[0][6][6]
		charmed = False
		try:
			ignore_def = move[0][6][7]
		except:
			ignore_def = False
		enemy = 1-move[4]#enemy id
		
		target_card = self.inst_card[enemy][target]
		
		if "charming" in target_card[4]:#Target is charming
			target_card = move[0]#change target to self
			charmed = True
		
		dmg = self.spell_dmg(target_card,move[0][1]*power,ignore_def)
		

		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		if charmed: message.append("{} was too charming so {} attacked themselves out of guilt".format(self.inst_card[enemy][target][5],target_card[5]))
		message.append("{} took {} damage".format(target_card[5],dmg))
		
		if combo:
			return message[1:]
		else:
			self.battle_log.extend(message)
			
	def any_target_dmg(self,move,combo=False):
		targets = move[0][6][7]
		power = move[0][6][6]
		try:
			ignore_def = move[0][6][8]
		except:
			ignore_def = False
		enemy = 1 - move[4]#enemy id
		target = self.any_target(targets)
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		
		for i in target:
			target_card = self.inst_card[i[0]][i[1]]
			
			num = 0
			counter = 0
			while "dead" in target_card[4]:
				if counter > 3:#Really lazy and bad but whatever
					break
				counter += 1
				num = (num+1)%3 #select next character if current selection is dead.
				target_card = self.inst_card[i[0]][num]
				
			dmg = self.spell_dmg(target_card,move[0][1]*power,ignore_def)
			message.append("{} took {} damage".format(target_card[5],dmg))
			
		if combo:
			return message[1:]
		else:
			self.battle_log.extend(message)
	
	def single_target_status(self,move,combo=False):
		target = move[2][1]
		length = move[0][6][7]
		effect = move[0][6][6]
		enemy = 1-move[4]
		charmed = False
		try:
			value = move[0][6][8]
		except:
			value = 0
		
		target_card = self.inst_card[enemy][target]
		
		if "charming" in target_card[4]:#Target is charming
			target_card = move[0]#change target to self
			charmed = True
		
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		
		self.spell_status(target_card,effect,length,value)
		if charmed: message.append("{} was too charming so {} changed the target to themselves out of guilt".format(self.inst_card[enemy][target][5],target_card[5]))
		message.append("{} received the status effect {}".format(target_card[5],effect))
	
		if combo:
			return message[1:]
		else:
			self.battle_log.extend(message)
			
	def self_status(self,move,combo=False):
		length = move[0][6][7]
		effect = move[0][6][6]
		
		try:
			value = move[0][6][8]
		except:
			value = 0
		
		target_card = move[0]
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		
		self.spell_status(target_card,effect,length,value)
		message.append("{} received the status effect {}".format(target_card[5],effect))
		
	
		if combo:
			return message[1:]
		else:
			self.battle_log.extend(message)
	
	def multi_target_status(self,move,combo=False):
		targets = move[0][6][8]
		length = move[0][6][7]
		effect = move[0][6][6]
		enemy = 1 - move[4]#enemy id
		
		try:
			value = move[0][6][9]
		except:
			value = 0

		target = self.multi_target(targets)
		
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		for i in target:
			target_card = self.inst_card[enemy][i]
			if self.spell_status(target_card,effect,length,value):
				message.append("{} received the status effect {}".format(target_card[5],effect))
		
		if combo:
			return message[1:]
		else:
			self.battle_log.extend(message)
			
	def any_target_status(self,move,combo=False):
		targets = move[0][6][8]
		length = move[0][6][7]
		effect = move[0][6][6]
		
		try:
			value = move[0][6][9]
		except:
			value = 0
		
		target = self.any_target(targets)
		
		
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		
		for i in target:
		
			target_card = self.inst_card[i[0]][i[1]]
			
			counter = 0
			num = i[1]
			while "dead" in target_card[4]:
				if counter > 3:#Really lazy and bad but whatever
					break
				counter += 1
				num = (num+1)%3 #select next character if current selection is dead.
				target_card = self.inst_card[i[0]][num]
			
			self.spell_status(target_card,effect,length,value)
			message.append("{} received the status effect {}".format(target_card[5],effect))
			
		if combo:
			return message[1:]
		else:
			self.battle_log.extend(message)
	
	def team_buff(self,team,status,amount,time = -10):
		player = team
		
		message = []
		
		for card in self.inst_card[player]:
			if "dead" not in card[4]:#dont apply buff to dead characters
				self.spell_status(card,status,time,amount)
				#buffs
				if status == "hp_up":#increases current hp by max hp (doesnt affect max hp)
					card[0] += int(card[7] * amount)
				elif status == "atk_up":
					card[1] *= (1+amount)
				elif status == "spd_up":
					card[2] *= (1+amount)
				#debuffs
				elif status == "hp_down":#reduced max hp
					card[7] = int(card[7] * (1-amount))
					if card[0] > card[7]: card[0] = card[7]#prevent current hp from being above max hp
				elif status == "atk_down":
					card[1] *= (1-amount)
				elif status == "spd_down":
					card[2] *= (1-amount)
				
				#card[8].append([time,status,amount]) #Done in self.spell_status so dont do it here
				
				message.append("{} has been applied on {}".format(status,card[5]))
		
		return message
	
	def target_buff(self,card,status,amount,time = -10):
		if self.spell_status(card,status,time,amount):
			#buffs
			if status == "hp_up":#increases current hp by max hp (doesnt affect max hp)
				card[0] += card[7] * amount
			elif status == "atk_up":
				card[1] *= (1+amount)
			elif status == "spd_up":
				card[2] *= (1+amount)
			#debuffs
			elif status == "hp_down":#reduced max hp
				card[7] *= (1-amount)
				if card[0] > card[7]: card[0] = card[7]#prevent current hp from being above max hp
			elif status == "atk_down":
				card[1] *= (1-amount)
			elif status == "spd_down":
				card[2] *= (1-amount)
				
			#card[8].append([time,status,amount])
				
			return ["{} has been applied on {}".format(status,card[5])]
		
	
	def sin_spell(self,move):
		card = move[0]
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		message.extend(self.target_buff(card,"spd_up",0.3,4))
		message.extend(self.target_buff(card,"multihit",2,4))
		
		self.battle_log.extend(message)
	
	def sariel_spell(self,move):
		team = move[4]
		dead_list = []
		
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		
		for i in self.inst_card[team]:
			if "dead" in i[4]:
				dead_list.append(i)
		
		if len(dead_list) == 0:
			for i in self.inst_card[team]:
				heal_amount= i[7]//10
				i[0] += heal_amount

				message.append("{} was healed for {} HP".format(i[5],heal_amount))
				
		elif len(dead_list) == 1:#Kill ally revive other ally
			card_to_be_revived = dead_list[0]
			for i in self.inst_card[team]:
				if i != move[0]:
					percent_left = i[0]/i[7]#percentage of hp left on sacrifice
					i[0] = 0
					if "dead" not in i[4]:#Dont add dead again if character is already dead (shouldn't happen but im just copy pasting old code so i dont care)
						i[4].append("dead")#set status as dead
						
					revive_hp = min(1,percent_left + 0.1)#cant comeback with over max hp
					
					card_to_be_revived[0] = int(card_to_be_revived[7]*(revive_hp)) #set to remaining percentage of sacrifce + 10% hp
					card_to_be_revived[4] = []#clear status list
					
					message.append("{} has been sacrificed and {} has been revived".format(i[5],card_to_be_revived[5]))
					
		elif len(dead_list) == 2:#Kill Sariel and revive other 2 allies
		
			percent_left = move[0][0]/move[0][7]#percentage of hp left on Sariel (Sacrifice)
			revive_hp = min(1,percent_left + 0.1)#cant comeback with over max hp
			
			move[0][0] = 0
			move[0][4].append("dead")#Kill Sariel
			for i in dead_list:
				i[0] = int(i[7] * revive_hp)
				i[4] = []#clear status list
				
				message.append("{} has been sacrificed and {} has been revived".format(move[0][5],i[5]))
		
		self.battle_log.extend(message)
		
	def konn_spell(self,move):
		enemy = 1 - move[4]
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		message.extend(self.team_buff(enemy,"life_steal",move[0],-10))
		#self.get_ownId(move[0][5],move[4])
		
	def rika_spell(self,move):
		card = move[0]
		spell = ["Reload","self_status",40,False,6,"Reload Shell's for the Shrine Tank","loaded",-10]
		tank = [card[0]*3,card[1]*3,card[2] // 2, False, ["loaded"],"Shrine Tank",spell,card[7]*3,[0,0,[-10,"loaded",0]]]
		
		id = self.get_ownId(card[5],move[4])
		self.inst_card[move[4]][id] = tank#replace inst_card
		
		self.reload_image = True
		tank_card = ["Misc","TANK.png","Shrine Tank"]
		self.user_cards[move[4]][id] = tank_card#replace user_card
		
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		message.append("THE SHRINE TANK HAS BEEN SUMMONED")
		self.battle_log.extend(message)
	
	def noroi_spell(self,move):
		enemy = 1 - move[4]
		target = move[2][1]
		target_card = self.inst_card[enemy][target]
		
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		self.spell_status(target_card,"cursed",-10)
		message.append("{} has been cursed".format(target_card[5]))
		
		move[0][0] = move[0][0]//2#cut current hp in half
		
		message.extend(self.target_buff(move[0],"hp_down",0.5,-10))
		
		self.battle_log.extend(message)
	
	def maten_spell(self,move):
		enemy = 1 - move[4]
		target = move[2][1]
		duration = 4
		reduction = 0.3
		target_card = self.inst_card[enemy][target]
		
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		self.spell_status(target_card,"burn",duration)
		message.append("{} received the status effect {}".format(target_card[5],"burn"))
		message.extend(self.target_buff(target_card,"spd_down",reduction,duration))
		message.extend(self.target_buff(target_card,"atk_down",reduction,duration))
		
		self.battle_log.extend(message)


	def rikako_spell(self,move):
		enemy = 1 - move[4]
		power = move[0][6][6]
		statuses = random.sample([["burn",3],["frozen",0.3],["stunned",1.2]],3)#Randomly select who gets each status 
		target_cards = [self.inst_card[enemy][0],self.inst_card[enemy][1],self.inst_card[enemy][2]]
		
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		
		for num,card in enumerate(target_cards):
			if "dead" not in card[4]:#Card is still alive
				dmg = self.spell_dmg(card,move[0][1]*power)
				self.spell_status(card,statuses[num][0],statuses[num][1])
				
				message.append("{} took {} damage".format(card[5],dmg))
				message.append("{} received the status effect {}".format(card[5],statuses[num][0]))
		
		self.battle_log.extend(message)
		
	def sakuya_spell(self,move):
		target = move[2][1]
		enemy = 1 - move[4]
		
		target_card = self.inst_card[enemy][target]
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		message.append("{}'s time has been stopped".format(target_card[5]))
		self.spell_status(target_card,"stop_time")
		dmg = self.spell_dmg(target_card,move[0][1]*move[0][6][6],True)
		message.append("{} took {} damage".format(target_card[5],dmg))
		
		self.battle_log.extend(message)
		
	def dai_spell(self,move):
		enemy = 1 - move[4]
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		message.extend(self.team_buff(move[4],"atk_up",0.2,2))
		message.extend(self.team_buff(enemy,"spd_down",0.2,2))
		
		self.battle_log.extend(message)
		
	def koakuma_spell(self,move):
		enemy = 1 - move[4]
		target = move[2][1]
		power = move[0][6][6]
		
		target_card = self.inst_card[enemy][target]
		dmg = self.spell_dmg(target_card,move[0][1]*power)
		
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		message.append("{} took {} damage".format(target_card[5],dmg))
		
		heal_list = []
		for card in self.inst_card[move[4]]:
			if "dead" not in card[4]:#dont heal dead teammates
				heal_list.append(card)
		
		heal_amount = dmg//len(heal_list)
		for i in heal_list:
			i[0] += heal_amount
			message.append("{} recovered {} HP".format(i[5],heal_amount))
		
		self.battle_log.extend(message)
	
	def remilia_spell(self,move):
		team = move[4]
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		message.extend(self.team_buff(team,move[0][6][6],move[0][6][7]))
		
		message.extend(self.target_buff(move[0],"vamp",0,3))
		
		self.battle_log.extend(message)
	
	def flandre_spell(self,move):
		enemy = 1 - move[4]
		message = ["{} used the spell card {}".format(move[0][5],move[0][6][0])]
		message.extend(self.multi_target_dmg(move,combo = True))
		
		self.spell_status(move[0],"rage",100)
		message.append("{} has become enraged".format(move[0][5]))
		
		self.battle_log.extend(message)
		