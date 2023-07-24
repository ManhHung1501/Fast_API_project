def event_serializer(event) -> dict:
    return {
        "user_id": event["user_id"],
        "game_id": event["game_id"],
        "device_type": event["device_type"],
        "event_device_timestamp": event["event_device_timestamp"],
        "device_system": event["device_system"],
        "password": event["password"],
        "sequence": event["sequence"],
        "event_name": event["event_name"],
        "event_timestamp": event["event_timestamp"],
        "event_parameters": event["event_parameters"]
    }


def events_serializer(events) -> list:
    return [event_serializer(event) for event in events]
