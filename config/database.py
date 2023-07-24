from pymongo import MongoClient

db_connection = MongoClient("mongodb://localhost:27017")
db = db_connection.Demo
col_user = db["users"]
col_event = db["events"]
col_game = db["games"]
