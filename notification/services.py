import json
from utils.get_redis import get_redis

r = get_redis()


class NotificationRealtimeService:
    @staticmethod
    def send_realtime(notification):
        resp = r.xadd("notifications_stream", {"data": json.dumps(notification)})
        return resp
