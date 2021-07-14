#Note this is temporary (PERMANENT). Later make spell cards work by storing it in the char data. Do this until we have a decent amount of cards so that its worth the effort
"""
0 -> Spell Name
1 -> Function called
2 -> Points needed
3 -> Targeting spell (False = multi hit/random/self)
4 -> Priority
5 -> Description

----DMG SPELL---
6 -> power multiplier
7 -> number of targets (only for any / multi target_dmg)
8 -> ignore def (7 if it's a single target spell) (defaults to False is left empty [this means you don't need to put False in there unless its True])

---STATUS SPELL---
6 -> spell effects
7 -> spell duration
8 -> number of targets (only for any / multi target_dmg)
8/9 -> spell values (If Single target (ex. Self_status, single_status) this will be index 8. It just wont be read)

---BUFF SPELL---
6 -> buff type
7 -> buff percentage
"""
#["Generic Spell Card","single_target_dmg",100,True,10,"A spell given to characters without a spell card. Deals damage to a single target",0.4]
Spell_cards = {
	"1-0-1": ["Fantasy Heaven","single_target_dmg",75,True,8,"A fast attack that deals big damage to a single target",0.55],
	"1-0-2": ["Master Spark","multi_target_dmg",120,False,11,"A powerful attack that deals large damage to all enemies. Takes long time to fire",0.4,3],
	"1-1"  : ["Gatekeeper 'Yin and Yang - The Positive and Negative'","sin_spell",80,False,10,"Gain 30% speed and multihit2 (Attacks hit twice) for 4 turns"],
	"1-2-A": ["Angel’s Legend “Evil Eyes”","self_status",100,False,10,"Gain phantom status for 4 turns. A 50% chance of dodging attacks and ignores guards","phantom",4],
	"1-2-B": ["Reincarnation “Complete Darkness”","self_status",30,False,5,"Revives back to 50% HP if Mima dies this turn","life",1],
	"1-3-A": ["Magic Mirror “Innocent Devil”","self_status",70,False,10,"Gains vamp status for duration of the battle","vamp",9999],
	"1-3-B": ["Magic Mirror “Hellish Moon”","self_status",70,False,10,"Gains 5% HP regen for the duration of the battle","hp_regen",-10,0.05],
	"1-4-A": ["Civilization of Magic “Angel of Death - Now, Until the Moment You Die”","sariel_spell",120,False,10,"Kills a living teammate and revives the other dead teammate. If both teammates are dead, sacrifice herself to revive both. (HP of the card revived is the remaining % of HP of the sacrificed card + 10%) If no teammates are dead, heal all allies by 10% HP instead (can over heal)"],
	"1-4-B": ["Astral Knight “Iris - Angel of a Distant Star”","konn_spell",120,False,10,"For the rest of the battle give enemies life drain status. Deal 5% hp per turn, damage dealt heals the caster"],
	"2-1":   ["Shrine Tank “She's in a Temper!!“","rika_spell",200,False,6,"Summon the Shrine Tank!. Replaces Rika, 3x Power and HP, but ½ speed of Rika. The Shrine Tank cannot attack unless it is loaded (Starts loaded with one shot). Spell card is replaced with “Reload“ Which reloads the tank for 40 <:power:796499186106236960>. When the shrine tank is defeated Rika is defeated along with it"],
	"2-2":	 ["Power of Darkness","self_status",120,False,10,"For the next 6 turns (including this one), attacking an enemy will give them blind status for 3 turns (including the turn you attacked them), attacking an enemy with blind, stun or sleep status will double the damage you deal","darkness_power",6],
	"2-2-2": ["End of Daylight","noroi_spell",100,True,10,"Curses 1 target enemy. Cursed target receives random negative status at the end of each turn. This status lasts for 1 turn. When casting this spell card Noroiko's current and Max HP is reduced by half","cursed",-10],
	"2-4-2": ["Himorogi, Burn in Violet","maten_spell",90,True,10,"Target receives burn status, also reduces the target's speed and attack stat by 30%. Both last 4 turns"],
	"3-1"  : ["Tabula Rasa - The Empty Girl","self_status",65,False,9,"She becomes irresistibly charming. Anyone attempting to attack Ellen this turn will instead be caused to attack themselves (Note: Applies to basic attacks and targeting type spell cards only. If a spell card deals dmg or statuses in a non-targeting (Attacks randomly or to all enemies) way the attack will not be reflected)","charming",1],
	"3-2"  : ["Maniacal Princess","self_status",90,False,10,"For the next 6 turns (including this one), attacking an enemy will give them Stun status (Note: Stun recoveres after 2 turns or faster if they are attacked (depends on how much dmg they take). The two turn duration includes the turn the spell card was used), attacking an enemy with blind, stun or sleep status will double the damage you deal","stun_power",6],
	"3-3"  : ["Vanishing Dream - Lost Dream","multi_target_status",70,False,10,"All enemies do 25% less damage for 4 turns.","atk_down",4,3,0.25],
	"3-4"  : ["Visionary Game - Dream War","rikako_spell",100,False,10,"Throws a powerful fire, ice and a lightning bomb that each hits an enemy. Deals large damage and applies the corresponding negative status to them (Fire - burn, Ice - Frozen (takes little damage to remove), Lightning - Stun (takes lots of damage to remove)) for 3 turns each",0.3],
	"3-5"  : ["Sailor of Time - GUN","single_target_dmg",100,True,0,"Stops time and shoots a target with her gun. Guns are way more fun than using magic. Deals massive damage to a single target",0.60],
	"3-6"  : ["Strawberry Crisis!!","self_status",120,False,9,"Gain double the <:power:796499186106236960> when attacking or defending. Deal 30% more damage and take 15% less damage. Stacks and lasts for the entire duration of the fight","strawberry",-10],
	"4-1"  : ["Decoration Battle","self_status",70,False,10,"Increases atk by 3x but takes 3x more dmg. I-I'm not going to let you get past me","orange",-10],
	"4-2"  : ["Scarlet Symphony - Scarlet Phoneme","kurumi_spell",70,False,10,"Permanently increase speed by 20%, gain vamp status for 3 turns, speed buff stacks",0.2],
	"4-3"  : ["Bad Apple!!","elly_spell",120,False,10,"Gives all Teammates and herself Regen and Vamp status for 3 turns",3],
	"4-4"  : ["Alice Maestra","hikrariko_spell",75,True,10,"A powerful light shines from Hikariko. Deal moderate damage and blind one target. Blind lasts 3 turns.",0.3],
	"4-5"  : ["Double Spark “Sleeping Terror”","yuuka_spell",150,False,11,"Her signature move from old era, she temporarily clones herself and shoots two giant lasers at once, dealing massive damage to all targets. Targets hit have life drain status for 3 turns, taking 5% hp per turn which heals the caster. She also gets sleep status for 3 turns",0.5],
	"4-6-1": ["Illusion of a Maid - Icemilk Magic","XXXXXXX",50,True,10,"Gain a large HP-Regen for 5 turns, 10% HP recovered per turn","hp_regen",5,0.1],
	"4-6-2": ["Cute Devil - Innocence","XXXXXXXX",50,True,10,"Gains vamp status for the next 5 turns","vamp",5],#Should target one ally
	"6-1"  : ['Darkness Sign "Demarcation"',"multi_target_status",70,False,10,"Weaving circle spreads followed by aimed waves of bullets. Blinds all enemies for 2 turns","blind",2,3],
	"6-2"  : ['Freeze Sign "Perfect Freeze"',"any_target_status",9,False,10,"Cirno's signature move. Freezing lively moments is her hobby, it seems. Freezes 1 random target (For 3 turns, or less if they take damage). This includes Cirno and her team.","frozen",0.30,1],
	"6-2-2": ["Lunate Elf","dai_spell",60,False,10,"Decreases all enemies speed by 20%, Increase teammates attack by 20% for 2 turns"],
	"6-3"  : ['Colorful Sign "Dazzling Color Typhoon"',"multi_target_dmg",90,False,10,"A swirling hurricane of colorful shards. All bullets curve in different directions. Ignores any defence",0.3,2,True],
	"6-4"  : ['Wood & Fire Sign "Forest Blaze"',"multi_target_status",95,False,10,"A wind filled of burning leaves and flame. Only you can prevent forest fires. But aren't we in a library? Leaves an afterburn on all enemies for 3 turns","burn",3,3],
	"6-4-2": ["Voile, the Magic Library","koakuma_spell",90,True,10,"Does a big damaging attack and gain hp from it, hp is shared between all living teammates and herself",0.4],
	"6-5"  : ['Illusion World "The World"',"sakuya_spell",60,True,0,"Stops time for 1 enemy. The selected target can't do anything until the end of the turn. Also sends a barrage of knives towards the target for large damage",0.35],
	"Raid" : ['Illusion World "The World"',"sakuya_spell",60,True,0,"Stops time for 1 enemy. The selected target can't do anything until the end of the turn. Also sends a barrage of knives towards the target for large damage",0.35],
	"6-6"  : ["Scarlet Gensokyo","remilia_spell",120,False,10,"Increases the attack stat of all allies by 25% for the duration of the battle. Gives her self vamp status for 3 turns","atk_up",0.25],
	"6-7"  : ['Q.E.D. "Ripples of 495 Years"',"flandre_spell",200,False,10,"The pent-up frustrations of 495 years' worth of imprisonment. The final attack always is the hardest. This is a final attack. Q.E.D. Deal huge amount of damage to all enemies and gain the rage status for the rest of the battle",0.5,3]
}
	