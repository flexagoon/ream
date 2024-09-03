from typing import Any, TypeAlias, TypeVar

from telethon.tl.types import (  # type: ignore[import-untyped]
    Document,
    DocumentAttributeAnimated,
    DocumentAttributeAudio,
    DocumentAttributeFilename,
    DocumentAttributeImageSize,
    DocumentAttributeSticker,
    DocumentAttributeVideo,
    Message,
    MessageMediaContact,
    MessageMediaDocument,
    MessageMediaGame,
    MessageMediaGeo,
    MessageMediaPhoto,
    MessageMediaPoll,
    MessageMediaUnsupported,
)

from ._helpers import log
from ._phone import __format_phone

MessageMedia: TypeAlias = MessageMediaPhoto | MessageMediaDocument | MessageMediaContact
DocumentAttribute: TypeAlias = (
    DocumentAttributeSticker
    | DocumentAttributeAudio
    | DocumentAttributeVideo
    | DocumentAttributeAnimated
)


async def __serialize_media(message: Message) -> dict[str, Any]:
    media = message.media
    if not media:
        return {}

    data: dict[str, Any] = {}

    match media:
        case MessageMediaPhoto():
            photo = media.photo
            data["photo"] = __fetch_media()  # photo.image
            size = photo.sizes[-1]
            data["width"] = size.w
            data["height"] = size.h
            if media.ttl_seconds:
                data["self_destruct_period_seconds"] = media.ttl_seconds
        case MessageMediaDocument():
            data |= __serialize_document(media.document)
            if media.ttl_seconds:
                data["self_destruct_period_seconds"] = media.ttl_seconds
        case MessageMediaContact():
            data["contact_information"] = {
                "first_name": media.first_name,
                "last_name": media.last_name,
                "phone_number": __format_phone(media.phone_number),
            }
            if media.vcard:
                data["contact_vcard"] = media.vcard
        case MessageMediaGeo():
            data["location_information"] = {
                "latitude": media.geo.latitude,
                "longitude": media.geo.longitude,
            }
            if media.ttl_seconds:
                data["live_location_period_seconds"] = media.ttl_seconds
        case MessageMediaGame():
            game = media.game
            data["game_title"] = game.title
            data["game_description"] = game.description
            if message.via_bot_id and game.short_name:
                bot = await message.client.get_entity(message.via_bot_id)
                if bot.bot and bot.username:
                    data["game_link"] = (
                        f"https://t.me/{bot.username}?game={game.short_name}"
                    )
        case MessageMediaPoll():
            data["poll"] = __serialize_poll(media)
        # TODO: Paid media (no support in telethon)
        case MessageMediaUnsupported():
            log.warning("Unsupported media type: %s", message.media)

    return data


def __serialize_document(document: Document) -> dict[str, Any]:
    data: dict[str, Any] = {
        "file": __fetch_media(),  # document.file
    }

    file_name_attr = __document_attr(document, DocumentAttributeFilename)
    if file_name_attr:
        data["file_name"] = file_name_attr.file_name

    if document.thumbs:
        data["thumbnail"] = __fetch_media()  # document.thumb.file

    type_attr = __document_type_attr(document)
    match type_attr:
        case DocumentAttributeSticker():
            data["media_type"] = "sticker"
            data["sticker_emoji"] = type_attr.alt
        case DocumentAttributeVideo():
            data["media_type"] = (
                "video_message" if type_attr.round_message else "video_file"
            )
        case DocumentAttributeAudio():
            if type_attr.voice:
                data["media_type"] = "voice_message"
            else:
                data["media_type"] = "audio_file"
                data["performer"] = type_attr.performer
                data["title"] = type_attr.title
        case DocumentAttributeAnimated():
            data["media_type"] = "animation"

    data["mime_type"] = document.mime_type

    if hasattr(type_attr, "duration"):
        data["duration_seconds"] = int(type_attr.duration)

    if isinstance(type_attr, DocumentAttributeVideo):
        data["width"] = type_attr.w
        data["height"] = type_attr.h
    elif image_size := __document_attr(document, DocumentAttributeImageSize):
        data["width"] = image_size.w
        data["height"] = image_size.h

    return data


def __document_type_attr(document: Document) -> DocumentAttribute | None:
    if sticker := __document_attr(document, DocumentAttributeSticker):
        return sticker
    if audio := __document_attr(document, DocumentAttributeAudio):
        return audio
    if video := __document_attr(document, DocumentAttributeVideo):
        return video
    if animated := __document_attr(document, DocumentAttributeAnimated):
        return animated
    return None


_T_req = TypeVar("_T_req")


def __document_attr(document: Document, req_type: type[_T_req]) -> _T_req | None:
    for attr in document.attributes:
        if isinstance(attr, req_type):
            return attr
    return None


def __fetch_media() -> str:
    return "(File not included. Change data exporting settings to download.)"


def __serialize_poll(media: MessageMediaPoll) -> dict[str, Any]:
    poll = {
        "question": media.poll.question,
        "closed": media.poll.closed,
        "total_voters": media.results.total_voters,
    }

    answers = []
    for poll_answer in media.poll.answers:
        answer = {
            "text": poll_answer.text,
            "voters": 0,
            "chosen": False,
        }
        if media.results.results:
            votes = next(
                filter(
                    lambda voters: voters.option == poll_answer.option,
                    media.results.results,
                ),
            )
            answer["voters"] = votes.voters
            answer["chosen"] = votes.chosen
        answers.append(answer)
    poll["answers"] = answers

    return poll
