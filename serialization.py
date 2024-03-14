from datetime import datetime
from typing import Any

from telethon.hints import EntitiesLike  # type: ignore
from telethon import TelegramClient  # type: ignore
from telethon.tl.types import (  # type: ignore
    Message,
    MessageService,
    MessageEntityUnknown,
    MessageEntityMention,
    MessageEntityHashtag,
    MessageEntityBotCommand,
    MessageEntityUrl,
    MessageEntityEmail,
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityCode,
    MessageEntityPre,
    MessageEntityTextUrl,
    MessageEntityMentionName,
    MessageEntityPhone,
    MessageEntityCashtag,
    MessageEntityUnderline,
    MessageEntityStrike,
    MessageEntityBlockquote,
    MessageEntityBankCard,
    MessageEntitySpoiler,
    MessageEntityCustomEmoji,
    MessageActionPinMessage,
    MessageActionHistoryClear,
    MessageActionGameScore,
    MessageActionPhoneCall,
    PhoneCallDiscardReasonBusy,
    PhoneCallDiscardReasonDisconnect,
    PhoneCallDiscardReasonHangup,
    PhoneCallDiscardReasonMissed,
    MessageActionScreenshotTaken,
    MessageActionContactSignUp,
    MessageActionGeoProximityReached,
    MessageActionSetMessagesTTL,
    MessageActionGiftPremium,
    MessageActionSetChatTheme,
    MessageActionSuggestProfilePhoto,
    MessageActionSetChatWallPaper,
)


async def serialize(message: Message) -> dict[str, Any]:
    if type(message) is MessageService:
        message_type = "service"
        from_key = "actor"
    else:
        message_type = "message"
        from_key = "from"
    from_id_key = from_key + "_id"

    if message.from_id:
        from_entity = await message.client.get_entity(message.from_id)
    else:
        return {}

    date, date_unixtime = __format_time(message.date)

    data = {
        "id": message.id,
        "type": message_type,
        "date": date,
        "date_unixtime": date_unixtime,
        from_key: " ".join(
            filter(
                None,
                [from_entity.first_name, from_entity.last_name],
            ),
        ),
        from_id_key: f"user{from_entity.id}",
    }

    if message.edit_date:
        edit_date, edit_date_unixtime = __format_time(message.edit_date)
        data["edited"] = edit_date
        data["edited_unixtime"] = edit_date_unixtime

    if message_type == "service":
        data["action"] = __serialize_action(message)
    else:
        if forward := message.fwd_from:
            data["forwarded_from"] = (
                forward.from_id if forward.from_id else forward.from_name
            )

        if message.reply_to and message.reply_to.reply_to_msg_id:
            reply = message.reply_to
            data["reply_to_message_id"] = reply.reply_to_msg_id
            if reply.reply_to_peer_id:
                data["reply_to_peer_id"] = reply.reply_to_peer_id

        if message.via_bot_id:
            bot = await message.client.get_entity(message.via_bot_id)
            if bot.username and bot.username != "":
                data["via_bot"] = bot.username

    data["text"] = message.raw_text
    data["text_entities"] = __serialize_text_entities(
        message.entities,
        message.raw_text,
    )

    return data


def __format_time(time: datetime) -> tuple[str, int]:
    return time.strftime("%Y-%m-%dT%H:%M:%S"), int(time.timestamp())


__call_discard_reasons = {
    PhoneCallDiscardReasonBusy: "busy",
    PhoneCallDiscardReasonDisconnect: "disconnect",
    PhoneCallDiscardReasonHangup: "hangup",
    PhoneCallDiscardReasonMissed: "missed",
}


async def __serialize_action(
    message: Message,
) -> tuple[str, dict[str, Any], bool]:
    action = message.action
    data: dict[str, Any]
    match action:
        case MessageActionPinMessage():
            data = __serialize_reply(message, "message_id")
            return "pin_message", data, True
        case MessageActionHistoryClear():
            return "clear_history", {}, True
        case MessageActionGameScore():
            data = __serialize_reply(message, "game_message_id")
            data["score"] = action.score
            return "score_in_game", data, True
        case MessageActionPhoneCall():
            data = {}
            if action.duration:
                data["duration_seconds"] = action.duration
                data["discard_reason"] = ""
                if action.reason:
                    reason = type(action.reason)
                    data["discard_reason"] = __call_discard_reasons[reason]
            return "phone_call", data, True
        case MessageActionScreenshotTaken():
            return "take_screenshot", {}, True
        case MessageActionContactSignUp():
            return "joined_telegram", {}, True
        case MessageActionGeoProximityReached():
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
            return "proximity_reached", data, False
        case MessageActionSetMessagesTTL():
            data = {"period": action.period}
            return "set_messages_ttl", data, True
        case MessageActionSetChatTheme():
            data = {}
            if action.emoticon:
                data["emoticon"] = action.emoticon
            return "set_chat_theme", data, True
        case MessageActionGiftPremium():
            data = {}
            if action.amount:
                data["cost"] = action.amount
            if action.months:
                data["months"] = action.months
            return "send_premium_gift", data, True
        case MessageActionSuggestProfilePhoto():
            # TODO: Implement photo
            return "suggest_profile_photo", {}, True
        case MessageActionSetChatWallPaper():
            data = __serialize_reply(message, "message_id")
            if action.same:
                return "set_same_chat_wallpaper", data, True
            return "set_chat_wallpaper", data, True
        case _:
            return "unknown", {}, False


async def __serialize_peer(
    client: TelegramClient,
    peer: EntitiesLike,
    prefix: str,
) -> dict[str, str | int]:
    entity = await client.get_entity(peer)
    return {
        prefix: " ".join(
            filter(
                None,
                [entity.first_name, entity.last_name],
            ),
        ),
        prefix + "_id": f"user{entity.id}",
    }


def __serialize_reply(
    message: Message,
    label: str = "reply_to_message_id",
) -> dict[str, int]:
    data = {}
    reply = message.reply_to
    data[label] = reply.reply_to_msg_id
    if reply.reply_to_peer_id:
        data["reply_to_peer_id"] = reply.reply_to_peer_id
    return data


__entity_types = {
    MessageEntityUnknown: "unknown",
    MessageEntityMention: "mention",
    MessageEntityHashtag: "hashtag",
    MessageEntityBotCommand: "bot_command",
    MessageEntityUrl: "link",
    MessageEntityEmail: "email",
    MessageEntityBold: "bold",
    MessageEntityItalic: "italic",
    MessageEntityCode: "code",
    MessageEntityPre: "pre",
    MessageEntityTextUrl: "text_link",
    MessageEntityMentionName: "mention_name",
    MessageEntityPhone: "phone",
    MessageEntityCashtag: "cashtag",
    MessageEntityUnderline: "underline",
    MessageEntityStrike: "strikethrough",
    MessageEntityBlockquote: "blockquote",
    MessageEntityBankCard: "bank_card",
    MessageEntitySpoiler: "spoiler",
    MessageEntityCustomEmoji: "custom_emoji",
}


def __serialize_text_entities(
    entities: list[Any] | None,
    text: str,
) -> list[dict[str, str]]:
    if not entities:
        return []

    text_entites = []
    last_offset = 0

    for entity in entities:
        entity_type = __entity_types[type(entity)]

        start = entity.offset
        end = start + entity.length
        if start > last_offset:
            data = {
                "type": "plain",
                "text": text[last_offset:start],
            }
            last_offset = end
            data = {
                "type": entity_type,
                "text": text[start:end],
            }

        match entity:
            case MessageEntityMentionName():
                data["user_id"] = entity.user_id
            case MessageEntityCustomEmoji():
                data["document_id"] = entity.document_id
            case MessageEntityPre():
                data["language"] = entity.language
            case MessageEntityTextUrl():
                data["href"] = entity.url

        text_entites.append(data)

    return text_entites
    return text_entites

    return text_entites
    return text_entites
    return text_entites
