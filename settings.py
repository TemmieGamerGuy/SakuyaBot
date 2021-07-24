from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
TOPGGTOKEN = os.getenv('TOPGGTOKEN')

BOT_ID = 864237884473999382#Replace this with your bot's ID


CLIENT_ID = TOKEN


OWNER_ID = 415158701331185673#Replace this with Owners discord ID
VALUE_MULTIPLIER = 5 #value of cards when sold
PTS_PER_GUESS = 1000 #amount of points earned after a successful guess

LEVEL_CAP = 150

char_dir = ".//touhoushit"
rarity_dir = ".//Rarities"
bg_dir = ".//BGs"