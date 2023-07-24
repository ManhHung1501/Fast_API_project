def user_serializer(user) -> dict:
    return {
        "device": user["device"],
        "user_first_touch_timestamp": user["user_first_touch_timestamp"],
        "current_sequence": user["current_sequence"],
        "user_properties": user["user_properties"]
    }


def users_serializer(users) -> list:
    return [user_serializer(user) for user in users]
