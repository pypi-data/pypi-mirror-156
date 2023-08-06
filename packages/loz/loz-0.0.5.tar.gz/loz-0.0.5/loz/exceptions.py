class LozException(Exception):
    "Generic loz exception."
    pass


class LozIncompatibleFileVersion(LozException):
    "Current loz version does not support existing lozfile version."
    pass


class LozFileDoesNotExist(LozException):
    "Lozfile not found."
    pass
