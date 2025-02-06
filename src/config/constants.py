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
