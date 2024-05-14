from typing import Any

from telethon.tl.types import (  # type: ignore[import-untyped]
    Message,
    MessageActionContactSignUp,
    MessageActionGameScore,
    MessageActionGeoProximityReached,
    MessageActionGiftPremium,
    MessageActionHistoryClear,
    MessageActionPhoneCall,
    MessageActionPinMessage,
    MessageActionScreenshotTaken,
    MessageActionSetChatTheme,
    MessageActionSetChatWallPaper,
    MessageActionSetMessagesTTL,
    MessageActionSuggestProfilePhoto,
    PhoneCallDiscardReasonBusy,
    PhoneCallDiscardReasonDisconnect,
    PhoneCallDiscardReasonHangup,
    PhoneCallDiscardReasonMissed,
)

from ._helpers import __serialize_peer, __serialize_reply


async def __serialize_action(message: Message) -> dict[str, Any]:
    action = message.action
    data: dict[str, Any] = {}
    add_actor = True
    match action:
        case MessageActionPinMessage():
            data = __serialize_reply(message, "message_id")
            data["action"] = "pin_message"
        case MessageActionHistoryClear():
            data["action"] = "clear_history"
        case MessageActionGameScore():
            data = __serialize_reply(message, "game_message_id")
            data["score"] = action.score
            data["action"] = "score_in_game"
        case MessageActionPhoneCall():
            data = {}
            if action.duration:
                data["duration_seconds"] = action.duration
                data["discard_reason"] = ""
            if action.reason:
                reason = type(action.reason)
                data["discard_reason"] = __call_discard_reasons[reason]
            data["action"] = "phone_call"
        case MessageActionScreenshotTaken():
            data["action"] = "take_screenshot"
        case MessageActionContactSignUp():
            data["action"] = "join_telegram"
        case MessageActionGeoProximityReached():
            add_actor = False
            data = {"distance": action.distance}
            if action.from_id:
                peer_data = await __serialize_peer(
                    message.client,
                    action.from_id,
                    "from",
                )
                data |= peer_data
            if action.to_id:
                peer_data = await __serialize_peer(
                    message.client,
                    action.to_id,
                    "to",
                )
                data |= peer_data
            data["distance"] = action.distance
            data["action"] = "proximity_reached"
        case MessageActionSetMessagesTTL():
            data = {"period": action.period}
            data["action"] = "set_messages_ttl"
        case MessageActionSetChatTheme():
            data = {}
            if action.emoticon:
                data["emoticon"] = action.emoticon
            data["action"] = "edit_chat_theme"
        case MessageActionGiftPremium():
            data = {}
            if action.amount:
                data["cost"] = action.amount
            if action.months:
                data["months"] = action.months
            data["action"] = "send_premium_gift"
        case MessageActionSuggestProfilePhoto():
            # TODO: Implement photo
            data["action"] = "suggest_profile_photo"
        case MessageActionSetChatWallPaper():
            data = __serialize_reply(message, "message_id")
            data["action"] = (
                "set_same_chat_wallpaper" if action.same else "set_chat_wallpaper"
            )
        case _:
            data["action"] = "unknown"
            add_actor = False

    if add_actor:
        data |= await __serialize_peer(message.client, message.from_id, "actor")

    return data


__call_discard_reasons = {
    PhoneCallDiscardReasonBusy: "busy",
    PhoneCallDiscardReasonDisconnect: "disconnect",
    PhoneCallDiscardReasonHangup: "hangup",
    PhoneCallDiscardReasonMissed: "missed",
}
