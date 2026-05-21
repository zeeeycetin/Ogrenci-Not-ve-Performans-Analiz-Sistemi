from datetime import datetime
from bson import ObjectId


class Message:
    def __init__(
        self,
        sender_id,
        receiver_id,
        subject: str,
        body: str,
        sender_name: str = "",
        receiver_name: str = "",
        is_read: bool = False,
        _id=None,
        created_at: datetime = None,
    ):
        self._id = _id or ObjectId()
        self.sender_id = ObjectId(sender_id) if not isinstance(sender_id, ObjectId) else sender_id
        self.receiver_id = ObjectId(receiver_id) if not isinstance(receiver_id, ObjectId) else receiver_id
        self.subject = subject
        self.body = body
        self.sender_name = sender_name
        self.receiver_name = receiver_name
        self.is_read = is_read
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "subject": self.subject,
            "body": self.body,
            "sender_name": self.sender_name,
            "receiver_name": self.receiver_name,
            "is_read": self.is_read,
            "created_at": self.created_at,
        }
