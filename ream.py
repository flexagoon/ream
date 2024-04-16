"""Exports important chats from your Telegram account.

Takes no arguments, since all configuration is provided through ream.toml.
"""

import logging
from pathlib import Path

import telethon  # type: ignore[import-untyped]
import tomllib
from telethon.hints import EntityLike  # type: ignore[import-untyped]

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
    print("[")
    async with client.takeout(
        users=True,
        files=True,
        max_file_size=config["export"]["max_file_size"],
    ) as takeout:
        message: telethon.types.Message
        async for message in takeout.iter_messages(chat, reverse=True):
            data = await serialize(message)
            print(data)
            print(",")
    print("]")


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
