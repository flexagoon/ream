import json
from pathlib import Path
from typing import Any

from telethon.tl.types import (
    Message,
    MessageActionContactSignUp,
    MessageActionGameScore,
    MessageActionGeoProximityReached,
    MessageActionGiftPremium,
    MessageActionGiftStars,
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

__currencies_path = Path(__file__).parent / "currencies.json"
__currencies = json.loads(__currencies_path.read_text(encoding="utf-8"))


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
            data["action"] = "joined_telegram"
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
        case MessageActionGiftStars():
            data["action"] = "send_stars_gift"

            currency = __currencies[action.currency]
            amount = action.amount / (10 ** currency["exp"])
            amount_string = (
                f"{amount:,}".replace(",", "^")
                .replace(".", currency["decimal_sep"])
                .replace("^", currency["thousands_sep"])
            )

            separator = " " if currency["space_between"] else ""
            data["cost"] = (
                f"{currency['symbol']}{amount_string}{separator}"
                if currency["symbol_left"]
                else f"{amount_string}{separator}{currency['symbol']}"
            )

            data["stars"] = action.stars
        # TODO: stargift, not in telethon yet
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
