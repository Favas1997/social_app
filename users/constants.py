class RequestStatus:
    Pending = "pending"
    Accepted = "accepted"
    Rejected = "rejected"
    Blocked = 'blocked'


MAX_REQUEST_COUNT = 3

FRIEND_REQUEST_COOLDOWN_HOURS = 24
FRIEND_REQUEST_CACHE_TIMEOUT = 60
FRIEND_REQUEST_INC = 1
FRIEND_LIST_CACHE_TIMEOUT = 60 * 15

DATA_PER_PAGE = 10