MATCH_QUEUE = "random-match-queue"

class MessageType():
    """Known message types sent to the frontend"""
    GAME_START = "start"
    GAME_UPDATE = "update"
    GAME_CHECK = "check"
    GAME_CANCELLED = "cancelled"
    EMOJI = "emoji"
    USER_EXIT = "user_exit"