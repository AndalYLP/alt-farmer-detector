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

GAME_ID = int(os.environ.get("GAME_ID") or os.getenv("GAME_ID"))

TRACKING_CATEGORY = int(
    os.environ.get("TRACKING_CATEGORY") or os.getenv("TRACKING_CATEGORY")
)

STATUS_CHANNEL_ID = int(
    os.environ.get("STATUS_CHANNEL_ID") or os.getenv("STATUS_CHANNEL_ID")
)
ALT_STATUS_CHANNEL_ID = int(
    os.environ.get("ALT_STATUS_CHANNEL_ID") or os.getenv("ALT_STATUS_CHANNEL_ID")
)
GAMEID_CHANNEL_ID = int(
    os.environ.get("GAMEID_CHANNEL_ID") or os.getenv("GAMEID_CHANNEL_ID")
)
GAMEID_WITH_ALTS_CHANNEL_ID = int(
    os.environ.get("GAMEID_WITH_ALTS_CHANNEL_ID")
    or os.getenv("GAMEID_WITH_ALTS_CHANNEL_ID")
)
