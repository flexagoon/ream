"""Exports important chats from your Telegram account.

Takes no arguments, since all configuration is provided through ream.toml.
"""

import json
import logging
import tomllib
from pathlib import Path

import telethon
from telethon.hints import EntityLike

from serialization.serialization import serialize


async def export(client: telethon.TelegramClient, chat: EntityLike) -> None:
    """Export data from a Telegram chat.

    Parameters
    ----------
    client : telethon.TelegramClient
        The Telegram client.
    chat : EntityLike
        The chat to export.

    """
    entity = await client.get_entity(chat)
    chat_data = {
        "name": entity.first_name,
        "type": "personal_chat",
        "id": entity.id,
    }
    async with client.takeout(
        users=True,
        files=True,
        max_file_size=config["export"]["max_file_size"],
    ) as takeout:
        chat_data["messages"] = [
            await serialize(message)
            async for message in takeout.iter_messages(
                chat,
                reverse=True,
            )
        ]

    Path("out.json").write_text(
        json.dumps(
            chat_data,
            indent=1,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


async def __main(client: telethon.TelegramClient) -> None:
    for chat in config["export"]["chats"]:
        logging.info("Exporting chat %s...", chat)
        await export(client, chat)


if __name__ == "__main__":
    with Path("ream.toml").open("rb") as f:
        config = tomllib.load(f)

    client = telethon.TelegramClient(
        "ream",
        config["api"]["app_id"],
        config["api"]["app_hash"],
    )

    with client:
        client.loop.run_until_complete(__main(client))
