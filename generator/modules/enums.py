from enum import Enum


class State(Enum):
    New = "New"
    Ready = "Ready"
    Moved = "Moved"


class StemType(Enum):
    Vocals = 'vocals'
    Other = 'other'
    Bass = 'bass'
    Drums = 'drums'


class SongSection(Enum):
    First= 0
    Start = 1
    Middle = 2
    End = 3
    Last = 4
    Any = 5
