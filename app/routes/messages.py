from flask import Blueprint, render_template, session, redirect, url_for, request, current_app, flash
from bson import ObjectId
from datetime import datetime
from app.utils.auth import login_required
from app.utils.helpers import serialize_doc
from app.models.message import Message

messages_bp = Blueprint("messages", __name__)


def _uid():
    return ObjectId(session["user"]["id"])


@messages_bp.route("/", methods=["GET"])
@login_required
def inbox():
    db = current_app.db
    uid = _uid()
    msgs = serialize_doc(list(db.messages.find({"receiver_id": uid}).sort("created_at", -1).limit(50)))
    unread = db.messages.count_documents({"receiver_id": uid, "is_read": False})
    return render_template("messages/inbox.html", messages=msgs, unread=unread, user=session["user"])


@messages_bp.route("/sent", methods=["GET"])
@login_required
def sent():
    db = current_app.db
    uid = _uid()
    msgs = serialize_doc(list(db.messages.find({"sender_id": uid}).sort("created_at", -1).limit(50)))
    return render_template("messages/sent.html", messages=msgs, user=session["user"])


@messages_bp.route("/<msg_id>", methods=["GET"])
@login_required
def view_message(msg_id: str):
    db = current_app.db
    uid = _uid()
    msg = db.messages.find_one({"_id": ObjectId(msg_id)})
    if not msg:
        flash("Mesaj bulunamadı.", "danger")
        return redirect(url_for("messages.inbox"))
    if msg["receiver_id"] == uid and not msg.get("is_read"):
        db.messages.update_one({"_id": ObjectId(msg_id)}, {"$set": {"is_read": True}})
        msg["is_read"] = True
    return render_template("messages/view.html", msg=serialize_doc(msg), user=session["user"])


@messages_bp.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    db = current_app.db
    user = session["user"]
    uid = _uid()

    if request.method == "POST":
        receiver_id = request.form.get("receiver_id", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()

        if not receiver_id or not subject or not body:
            flash("Tüm alanları doldurun.", "warning")
            return redirect(url_for("messages.compose"))

        receiver = db.users.find_one({"_id": ObjectId(receiver_id)})
        if not receiver:
            flash("Alıcı bulunamadı.", "danger")
            return redirect(url_for("messages.compose"))

        msg = Message(
            sender_id=uid,
            receiver_id=ObjectId(receiver_id),
            subject=subject,
            body=body,
            sender_name=user["full_name"],
            receiver_name=receiver["full_name"],
        )
        db.messages.insert_one(msg.to_dict())
        flash("Mesaj gönderildi.", "success")
        return redirect(url_for("messages.sent"))

    # Alıcı listesi: öğrenciler ve öğretmenler
    reply_to = request.args.get("reply_to")
    preselect = None
    if reply_to:
        orig = db.messages.find_one({"_id": ObjectId(reply_to)})
        if orig:
            preselect = str(orig["sender_id"])

    if user["role"] == "student":
        recipients = serialize_doc(list(db.users.find({"role": {"$in": ["teacher", "admin"]}, "is_active": True})))
    else:
        recipients = serialize_doc(list(db.users.find({"role": {"$in": ["student", "teacher", "admin"]}, "_id": {"$ne": uid}, "is_active": True})))

    return render_template("messages/compose.html", recipients=recipients, preselect=preselect, user=user)


@messages_bp.route("/<msg_id>/delete", methods=["POST"])
@login_required
def delete_message(msg_id: str):
    db = current_app.db
    uid = _uid()
    db.messages.delete_one({"_id": ObjectId(msg_id), "$or": [{"sender_id": uid}, {"receiver_id": uid}]})
    flash("Mesaj silindi.", "success")
    return redirect(url_for("messages.inbox"))


@messages_bp.route("/api/unread-count", methods=["GET"])
@login_required
def unread_count():
    from app.utils.helpers import success_response
    db = current_app.db
    uid = _uid()
    count = db.messages.count_documents({"receiver_id": uid, "is_read": False})
    return success_response({"count": count})
