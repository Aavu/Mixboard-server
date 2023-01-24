class NoBoundsError(Exception):
    pass


class InvalidBoundsError(Exception):
    pass


class SongNotFoundError(Exception):
    code = 1


class IllegalArgumentError(Exception):
    code = 2
