"""Exports important chats from your Telegram account.

Takes no arguments, since all configuration is provided through ream.toml.
"""

import asyncio
import json
import logging
import tomllib
from contextlib import suppress
from pathlib import Path

import telethon
from telethon.hints import EntityLike

from serialization.serialization import serialize

log = logging.getLogger(__name__)


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

    path = Path(f"{config['export']['path']}/{entity.id}")

    export_json = path / "export.json"

    if export_json.exists():
        chat_data = json.load(export_json.open())
        last_message = chat_data["messages"][-1]["id"] if chat_data["messages"] else 0
    else:
        export_json.parent.mkdir(exist_ok=True, parents=True)
        chat_data = {
            "name": entity.first_name,
            "type": "personal_chat",
            "id": entity.id,
            "messages": [],
        }
        last_message = 0

    # Close the takeout session if one is already open. If it's not open,
    # `client.end_takeout` will raise a TypeError, so it's suppressed.
    with suppress(TypeError):
        await client.end_takeout(success=False)

    async with client.takeout(
        users=True,
        files=True,
        max_file_size=config["export"]["max_file_size"],
    ) as takeout:
        messages = takeout.iter_messages(
            chat,
            reverse=True,
            offset_id=last_message,
        )

        batch_size = config["export"]["batch_size"]
        batch = []
        async for message in messages:
            batch.append(message)

            if len(batch) >= batch_size:
                tasks = [serialize(message, path) for message in batch]

                chat_data["messages"] += await asyncio.gather(*tasks)

                export_json.write_text(
                    json.dumps(
                        chat_data,
                        indent=1,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

                batch = []


async def __main(client: telethon.TelegramClient) -> None:
    if (
        "ream" in config
        and "log_level" in config["ream"]
        and config["ream"]["log_level"]
        in {
            "NOTESET",
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }
    ):
        logging.basicConfig(level=config["ream"]["log_level"])
    else:
        logging.basicConfig(level=logging.INFO)

    await client.get_dialogs()
    for chat in config["export"]["chats"]:
        log.info("Exporting chat %s...", chat)
        await export(client, chat)


if __name__ == "__main__":
    with Path("ream.toml").open("rb") as f:
        config = tomllib.load(f)

    client = telethon.TelegramClient(
        "ream",
        config["api"]["app_id"],
        config["api"]["app_hash"],
        app_version="1.0.0",
    )

    with client:
        client.loop.run_until_complete(__main(client))
