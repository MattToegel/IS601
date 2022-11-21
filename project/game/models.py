from common.utils import JsonSerializable


class Score(JsonSerializable):
    def __init__(self, username: str, user_id:int, score:int, hits: int, defeated: int,spawned: int, ratio:float, created):
        # people doing arcade just need the first two below and the related dates
        self.user_id = user_id
        self.score = score
        self.hits = hits
        self.defeated = defeated
        self.spawned = spawned
        self.ratio = ratio
        self.created = created
    