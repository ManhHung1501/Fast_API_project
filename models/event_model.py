from pydantic import BaseModel
from typing import Union


class Event(BaseModel):
    u: str
    gi: str
    dt: int
    st: int
    s: dict
    pw: str
    m: str
    cmd: Union[str, None] = None
    cv: Union[int, None] = None
    ut: Union[int, None] = None
    ud: Union[float, None] = None
    cs: Union[int, None] = None
    bs: Union[int, None] = None
    chs: Union[int, None] = None
