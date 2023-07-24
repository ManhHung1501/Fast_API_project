from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    user_first_touch_timestamp: int
    current_sequence: int
    user_properties: dict
