from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
TOPGGTOKEN = os.getenv('TOPGGTOKEN')
PASSWORD = os.getenv('PASSWORD')
otherpass = os.getenv("PASSWORD2")

BOT_ID = 864237884473999382

CLIENT_ID = TOKEN


OWNER_ID = 415158701331185673
VALUE_MULTIPLIER = 5
PTS_PER_GUESS = 1000

LEVEL_CAP = 150

char_dir = ".//touhoushit"
rarity_dir = ".//Rarities"
bg_dir = ".//BGs"