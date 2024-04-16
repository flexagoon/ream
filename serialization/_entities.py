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
            text_entites.append(data)

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
