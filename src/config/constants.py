import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI") or os.getenv("MONGO_URI")
COOKIE = os.environ.get("COOKIE") or os.getenv("COOKIE")
TOKEN = os.environ.get("TOKEN") or os.getenv("TOKEN")

MONGO_CLIENT = MongoClient(MONGO_URI)
__data_base = MONGO_CLIENT["AltFarmerDetector"]

USERS_COLLECTION = __data_base["Users"]

TRACKING_CATEGORY = 1320782071097987093

STATUS_CHANNEL_ID = 1277039650401423471
ALT_STATUS_CHANNEL_ID = 1277302313949593742
GAMEID_CHANNEL_ID = 1277046568033194115
GAMEID_WITH_ALTS_CHANNEL_ID = 1277089252676472894
