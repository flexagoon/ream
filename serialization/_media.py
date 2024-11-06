from pathlib import Path
from typing import Any

from telethon.tl.types import (
    Document,
    DocumentAttributeAnimated,
    DocumentAttributeAudio,
    DocumentAttributeSticker,
    DocumentAttributeVideo,
    Message,
    MessageMediaContact,
    MessageMediaDocument,
    MessageMediaGame,
    MessageMediaGeo,
    MessageMediaGeoLive,
    MessageMediaPaidMedia,
    MessageMediaPhoto,
    MessageMediaPoll,
    MessageMediaUnsupported,
    PhotoSize,
)

from ._helpers import __download_file, __get_next_file_n, log
from ._phone import __format_phone

type MessageMedia = MessageMediaPhoto | MessageMediaDocument | MessageMediaContact
type DocumentAttribute = (
    DocumentAttributeSticker
    | DocumentAttributeAudio
    | DocumentAttributeVideo
    | DocumentAttributeAnimated
)


async def __serialize_media(message: Message, path: Path) -> dict[str, Any]:
    media = message.media
    if not media:
        return {}

    data: dict[str, Any] = {}

    match media:
        case MessageMediaPhoto():
            photo = media.photo
            data["photo"] = await __download_file(
                message,
                path / f"photos/{photo.id}{message.file.ext}",
            )
            size = photo.sizes[-1]
            data["width"] = size.w
            data["height"] = size.h
            if media.ttl_seconds:
                data["self_destruct_period_seconds"] = media.ttl_seconds
        case MessageMediaDocument():
            data |= await __serialize_document(message, path)
            if media.ttl_seconds:
                data["self_destruct_period_seconds"] = media.ttl_seconds
        case MessageMediaContact():
            data["contact_information"] = {
                "first_name": media.first_name,
                "last_name": media.last_name,
                "phone_number": __format_phone(media.phone_number),
            }
            if media.vcard:
                contacts_dir = path / "contacts"
                contacts_dir.mkdir(parents=True, exist_ok=True)

                n = __get_next_file_n(contacts_dir)
                vcard_file = contacts_dir / f"contact_{n}.vcard"
                vcard_file.write_text(media.vcard)

                data["contact_vcard"] = f"contacts/contact_{n}.vcard"
        case MessageMediaGeo():
            data["location_information"] = {
                "latitude": round(media.geo.lat, 6),
                "longitude": round(media.geo.long, 6),
            }
        case MessageMediaGeoLive():
            data["location_information"] = {
                "latitude": round(media.geo.lat, 6),
                "longitude": round(media.geo.long, 6),
            }
            data["live_location_period_seconds"] = media.period
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
        case MessageMediaPaidMedia():
            data["paid_stars_amount"] = media.stars_amount
        case MessageMediaUnsupported():
            log.warning("Unsupported media type: %s", message.media)

    return data


async def __serialize_document(message: Message, path: Path) -> dict[str, Any]:
    file = message.file
    document = message.media.document

    data: dict[str, Any] = {}

    if file.name:
        data["file_name"] = file.name

    directory = "files"

    type_attr = __document_type_attr(document)
    match type_attr:
        case DocumentAttributeSticker():
            data["media_type"] = "sticker"
            data["sticker_emoji"] = type_attr.alt
            directory = "stickers"
        case DocumentAttributeVideo():
            if type_attr.round_message:
                data["media_type"] = "video_message"
                directory = "round_video_messages"
            else:
                data["media_type"] = "video_file"
                directory = "video_files"
        case DocumentAttributeAudio():
            if type_attr.voice:
                data["media_type"] = "voice_message"
                directory = "voice_messages"
            else:
                data["media_type"] = "audio_file"
                if type_attr.performer:
                    data["performer"] = type_attr.performer
                if type_attr.title:
                    data["title"] = type_attr.title
        case DocumentAttributeAnimated():
            data["media_type"] = "animation"
            directory = "video_files"

    ext = file.ext
    if ext == ".oga":
        ext = ".ogg"

    data["file"] = await __download_file(
        message,
        path / directory / f"{document.id}{ext}",
    )

    if document.thumbs:
        for thumb in document.thumbs:
            if isinstance(thumb, PhotoSize):
                data["thumbnail"] = await __download_file(
                    message,
                    path / directory / f"{document.id}{file.ext}_thumb.jpg",
                    thumb=thumb,
                )
                break

    data["mime_type"] = document.mime_type

    if hasattr(type_attr, "duration"):
        data["duration_seconds"] = int(type_attr.duration)

    if message.file.width:
        data["width"] = message.file.width
    if message.file.height:
        data["height"] = message.file.height

    return data


def __document_type_attr(document: Document) -> DocumentAttribute | None:
    type_attr = None
    for attr in document.attributes:
        if not (
            isinstance(
                attr,
                DocumentAttributeSticker
                | DocumentAttributeVideo
                | DocumentAttributeAudio
                | DocumentAttributeAnimated,
            )
        ):
            continue

        if type_attr is None:
            type_attr = attr

        if isinstance(
            attr,
            DocumentAttributeAnimated,
        ) and isinstance(
            type_attr,
            DocumentAttributeVideo,
        ):
            duration = type_attr.duration
            type_attr = attr
            type_attr.duration = duration

        if type(attr) is not type(type_attr):
            continue

        if isinstance(attr, DocumentAttributeSticker):
            type_attr.alt = type_attr.alt or attr.alt

        if isinstance(attr, DocumentAttributeAudio):
            type_attr.voice = type_attr.voice or attr.voice
            type_attr.performer = type_attr.performer or attr.performer
            type_attr.title = type_attr.title or attr.title
            type_attr.duration = type_attr.duration or attr.duration

        if isinstance(attr, DocumentAttributeVideo):
            type_attr.round_message = type_attr.round_message or attr.round_message
            type_attr.duration = type_attr.duration or attr.duration

    return type_attr


def __fetch_media() -> str:
    return "(File not included. Change data exporting settings to download.)"


def __serialize_poll(media: MessageMediaPoll) -> dict[str, Any]:
    poll = {
        "question": media.poll.question.text,
        "closed": media.poll.closed,
        "total_voters": media.results.total_voters,
    }

    answers = []
    for poll_answer in media.poll.answers:
        answer = {
            "text": poll_answer.text.text,
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
