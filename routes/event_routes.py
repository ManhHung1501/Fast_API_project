import base64
import hashlib
from bson import ObjectId
from Crypto.Cipher import AES
from fastapi import APIRouter, HTTPException
from config.database import col_event, col_game, col_user
from models.event_model import Event
from schemas.event_schema import events_serializer
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad
import json
from datetime import datetime, timedelta

event_router = APIRouter()


# Find missing sequence func
def find_missing_sequence(message):
    sequence_numbers = [event["i"] for event in message]
    missing_numbers = []
    previous_sequence = sequence_numbers[0]
    for current_sequence in sequence_numbers[1:]:
        if current_sequence != previous_sequence + 1:
            # Found a gap in the sequence numbers
            missing_range = range(previous_sequence + 1, current_sequence)
            missing_numbers.extend(missing_range)
        previous_sequence = current_sequence

    return missing_numbers


# Create decrypt function
salt = bytes([18, 169, 83, 22, 135, 111, 7, 220, 148, 128, 192, 223, 75, 56, 29, 112, 171])
iv = bytes([38, 40, 181, 21, 130, 224, 94, 10, 116, 81, 133, 220, 226, 249, 38, 193])


# Create AES key
def create_key(p):
    iterations = 1024
    key = PBKDF2(p, salt, dkLen=16, count=iterations)
    return key


# Decrypt and unpad
def decrypt(msg, p=None):
    cipher_text = base64.b64decode(msg)
    cipher = AES.new(create_key(p), AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(cipher_text)
    plain_text = unpad(decrypted_data, AES.block_size)
    return plain_text.decode('utf-8')


# Router
@event_router.post("/events")
async def create_event(event: Event):
    data = dict(event)

    # CHECK EXIST GAME_ID
    if data["gi"] not in [i.get("gi") for i in col_game.find()]:
        return {"status": "failed", "msg": "Game id not found"}

    # CHECK PASSWORD
    # Get password from db
    password = col_game.find_one({"gi": data["gi"]})["pw"]

    # Encode data password
    # data_password = hashlib.md5(data["pw"].encode()).hexdigest()
    if data["pw"] != password:
        return {"status": "failed", "msg": "Invalid password"}

    # DECRYPT MESSAGE
    # Create AES encryption key
    key = data["pw"] + data["s"]["a"] + data["s"]["b"] + data["s"]["c"]
    p = hashlib.md5(key.encode('utf-8')).hexdigest()
    # Decrypt message
    try:
        plain_text = decrypt(data["m"], p)
        data["m"] = json.loads(plain_text)
    except Exception as e:
        return {"status": "failed", "msg": "Invalid message"}

    # CHECK NEW USER
    users = col_user.find({}, {"_id": 0, "u": 1})
    lst_user_id = [user["u"] for user in users]
    if data["u"] not in lst_user_id:
        col_user.insert_one(
            {
                "u": data["u"],
                "gi": data["gi"],
                "cs": 0,
                "inst": (datetime.now() + timedelta(hours=7)).timestamp() * 1000,
                "mdft": (datetime.now() + timedelta(hours=7)).timestamp() * 1000
            }
        )

    # CHECK SEQUENCE
    # Rename system (s) to sy
    data["sy"] = data.pop("s")

    # Get current sequence
    filter_user = {"u": data["u"]}
    current_sequence = col_user.find_one(filter_user)["cs"]

    # Get event in message with sequence > current sequence of user
    data["m"] = [event for event in data["m"] if event["i"] > current_sequence]
    if len(data["m"]) < 1:
        return {"status": "failed", "msg": "Invalid message"}

    # Sort message by sequence
    data["m"] = sorted(data["m"], key=lambda x: x["i"])

    # Get min sequence of message
    min_message_sequence = data["m"][0]["i"]

    # Check min sequence is greater than current sequence + 1
    if min_message_sequence > current_sequence + 1:
        missing_sequence = find_missing_sequence(data["m"])
        missing_sequence.extend([i for i in range(current_sequence + 1, min_message_sequence)])
        return {"status": "failed", "msg": f"missing sequence {missing_sequence}"}
    else:
        # Separate message into many event documents
        message = data.pop("m")
        documents = []
        for event in message:
            if event["i"] == current_sequence + 1:
                document = data.copy()
                document.update(event)
                document["inst"] = (datetime.now() + timedelta(hours=7)).timestamp() * 1000
                document["mdft"] = (datetime.now() + timedelta(hours=7)).timestamp() * 1000
                documents.append(document)
                current_sequence = event["i"]

            # If duplicate sequence continue the loop
            elif event["i"] == current_sequence:
                continue

            # If missing sequence break the loop
            else:
                break

        # Update current sequence of user
        col_user.update_one(
            filter_user,
            {"$set": {
                "cs": current_sequence,
                "mdft": (datetime.now() + timedelta(hours=7)).timestamp() * 1000
            }
            }
        )

        # Insert into db
        col_event.insert_many(documents)

        # If message have missing sequence
        missing_sequence = find_missing_sequence(message)
        if len(missing_sequence) != 0:
            return {"status": "failed", "msg": f"missing sequence {missing_sequence}"}

    return {"status": "OK", "current_sequence": current_sequence}


# Retrieve all events
@event_router.get("/events")
async def find_all_events():
    events = events_serializer(col_event.find())
    return {"status": "Ok", "data": events}


# Retrieve an events
@event_router.get("/events/{event_id}")
async def get_one_event(event_id: str):
    event = events_serializer(col_event.find({"_id": ObjectId(event_id)}))
    if len(event) == 0:
        raise HTTPException(status_code=404, detail="event id not found")
    return {"status": "Ok", "data": event}


# Update a event
@event_router.put("/events/{event_id}")
async def update_event(event_id: str, event: Event):
    col_event.find_one({"_id": ObjectId(event_id)})
    if len(event) == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    col_event.update_one(
        {
            "_id": ObjectId(event_id)
        },
        {
            "$set": dict(event)
        }
    )
    event = events_serializer(col_event.find({"_id": ObjectId(event_id)}))

    return {"status": "Ok", "data": event}


# Delete an event
@event_router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    event_delete = events_serializer(col_event.find({"_id": ObjectId(event_id)}))
    if len(event_delete) == 1:
        data = event_delete[0]
        col_event.delete_one({"_id": ObjectId(event_id)})
        return {"status": "Ok", "Data_deleted": data}
    raise HTTPException(status_code=404, detail="Event not found")
