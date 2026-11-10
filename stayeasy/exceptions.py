class StayEasyError(Exception):
    pass

class InvalidGuestError(StayEasyError):
    pass

class InvalidRoomError(StayEasyError):
    pass

class RoomNotAvailableError(StayEasyError):
    pass

class InvalidBookingError(StayEasyError):
    pass

class InvalidBookingStatusError(StayEasyError):
    pass