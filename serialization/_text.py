from typing import Any

from telethon.tl.types import (  # type: ignore[import-untyped]
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
)
from telethon.utils import (  # type: ignore[import-untyped]
    add_surrogate,
    del_surrogate,
)


def __serialize_text(
    entities: list[Any] | None,
    text: str,
    *,
    serialize_entities: bool = False,
) -> str | list[str | dict[str, Any]]:
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
                data["document_id"] = entity.document_id  # TODO download
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

    # Replicate a bug in tdesktop export where a surrogate in the message
    # causes an empty string to be added at the end
    if (
        text != del_surrogate(text)
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
