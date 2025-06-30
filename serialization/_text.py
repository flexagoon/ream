from pathlib import Path
from typing import Any

from telethon import TelegramClient
from telethon.helpers import (
    add_surrogate,
    del_surrogate,
)
from telethon.tl import functions
from telethon.tl.custom.message import Message
from telethon.tl.types import (
    MessageEntityBankCard,
    MessageEntityBlockquote,
    MessageEntityBold,
    MessageEntityBotCommand,
    MessageEntityCashtag,
    MessageEntityCode,
    MessageEntityCustomEmoji,
    MessageEntityEmail,
    MessageEntityHashtag,
    MessageEntityItalic,
    MessageEntityMention,
    MessageEntityMentionName,
    MessageEntityPhone,
    MessageEntityPre,
    MessageEntitySpoiler,
    MessageEntityStrike,
    MessageEntityTextUrl,
    MessageEntityUnderline,
    MessageEntityUnknown,
    MessageEntityUrl,
    TextWithEntities,
)

from ._helpers import MissingClientError, __download_file


async def __serialize_text(
    message: Message | TextWithEntities,
    path: Path,
    *,
    serialize_entities: bool = False,
    client_override: TelegramClient | None = None,
) -> str | list[str | dict[str, Any]]:
    client = getattr(message, "client", client_override)
    if not isinstance(client, TelegramClient):
        raise MissingClientError

    entities = message.entities
    text = message.raw_text if isinstance(message, Message) else message.text

    if not entities:
        if serialize_entities:
            return [{"type": "plain", "text": text}] if text else []
        return text or ""

    text = add_surrogate(text)

    text_entities: list[str | dict[str, Any]] = []
    last_offset = 0

    for entity in entities:
        entity_type = __entity_types[type(entity)]

        start = entity.offset
        end = start + entity.length
        if start > last_offset:
            plain = del_surrogate(text[last_offset:start])
            text_entities.append(
                {
                    "type": "plain",
                    "text": plain,
                }
                if serialize_entities
                else plain,
            )
        elif start < last_offset:
            continue

        inner_text = del_surrogate(text[start:end])
        last_offset = end
        data = {
            "type": entity_type,
            "text": inner_text,
        }

        match entity:
            case MessageEntityMentionName():
                data["user_id"] = entity.user_id
            case MessageEntityCustomEmoji():
                emoji_data = await client(
                    functions.messages.GetCustomEmojiDocumentsRequest(
                        document_id=[entity.document_id],
                    ),
                )

                match emoji_data[0].mime_type:
                    case "image/webp":
                        directory = "stickers"
                        extension = "webp"
                    case "video/webm":
                        directory = "video_files"
                        extension = "webm"
                    case "application/x-tgsticker":
                        directory = "stickers"
                        extension = "tgs"

                emoji_dir = path / directory
                emoji_dir.mkdir(parents=True, exist_ok=True)

                file = emoji_dir / f"{entity.document_id}.{extension}"

                data["document_id"] = await __download_file(
                    emoji_data[0],
                    file,
                    client=client,
                )
            case MessageEntityPre():
                data["language"] = entity.language
            case MessageEntityTextUrl():
                data["href"] = entity.url

        text_entities.append(data)

    if last_offset < len(text):
        plain = del_surrogate(text[last_offset:])
        text_entities.append(
            {
                "type": "plain",
                "text": plain,
            }
            if serialize_entities
            else plain,
        )

    text = del_surrogate(text)

    # Replicate a bug in tdesktop export where unicode in the message
    # causes an empty string to be added at the end
    if (
        len(text) != len(text.encode())
        and not isinstance(text_entities[-1], str)
        and text_entities[-1]["type"] != "plain"
    ):
        text_entities.append(
            {
                "type": "plain",
                "text": "",
            }
            if serialize_entities
            else "",
        )

    return text_entities


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
