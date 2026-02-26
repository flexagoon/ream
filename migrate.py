"""Updates your exports to match the latest format version."""
# ruff: noqa: PLR2004

import asyncio
import json
import logging
import shutil
import tomllib
from contextlib import suppress
from pathlib import Path
from typing import Any, cast

from telethon import TelegramClient
from telethon.tl.custom.message import Message

log = logging.getLogger(__name__)

LAST_VERSION = 2


def __v2_update_send_premium_gift(message: dict[str, Any]) -> dict[str, Any]:
    if "action" in message and message["action"] == "send_premium_gift":
        log.info("Updating send_premium_gift message %s...", message["id"])
        months = message.pop("months", None)
        if months:
            message["days"] = months * 30
    return message


async def __v2_add_fwd_from_id(
    client: TelegramClient,
    chat_id: int,
    message: dict[str, Any],
) -> dict[str, Any]:
    if "forwarded_from" in message and "forwarded_from_id" not in message:
        log.info("Adding forwarded_from_id to message %s...", message["id"])
        tg_message = cast(
            Message | None,
            await client.get_messages(chat_id, ids=message["id"]),
        )
        if not tg_message:
            return message

        if forward := tg_message.forward:
            if sender := forward.sender:
                message["forwarded_from_id"] = sender.id
            elif chat := forward.chat:
                message["forwarded_from_id"] = chat.id

    return message


async def migrate_message(
    client: TelegramClient,
    chat_id: int,
    message: dict[str, Any],
    from_version: int,
) -> dict[str, Any]:
    if from_version < 2:
        message = __v2_update_send_premium_gift(message)
        message = await __v2_add_fwd_from_id(client, chat_id, message)
    return message


async def migrate(client: TelegramClient, config: dict[str, Any], chat_id: int) -> None:
    """Update the export of a chat to match the latest format version.

    Parameters
    ----------
    config : dict[str, Any]
        The configuration dictionary (see ream.toml).
    chat_id : int
        The ID of the chat to update.

    """
    log.info("Migrating chat %s to latest version...", chat_id)

    path = Path(f"{config['export']['path']}/{chat_id}")

    version_file = path / "version"
    version = int(version_file.read_text()) if version_file.exists() else 1

    if version >= LAST_VERSION:
        return

    export_json = path / "export.json"
    if not export_json.exists():
        return

    shutil.copy(export_json, path / "export.json.bak")

    chat_data = json.load(export_json.open())

    batch_size = config["export"]["batch_size"]
    batch = []

    for i in range(len(chat_data["messages"])):
        batch.append(i)

        if len(batch) >= batch_size:
            tasks = [
                migrate_message(client, chat_id, chat_data["messages"][msg_id], version)
                for msg_id in batch
            ]

            new_messages = await asyncio.gather(*tasks)

            for msg_id, new_message in zip(batch, new_messages, strict=True):
                chat_data["messages"][msg_id] = new_message

            export_json.write_text(
                json.dumps(
                    chat_data,
                    indent=1,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            batch = []
    if batch:
        tasks = [
            migrate_message(client, chat_id, chat_data["messages"][msg_id], version)
            for msg_id in batch
        ]

        new_messages = await asyncio.gather(*tasks)

        for msg_id, new_message in zip(batch, new_messages, strict=True):
            chat_data["messages"][msg_id] = new_message

        export_json.write_text(
            json.dumps(
                chat_data,
                indent=1,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    version_file.write_text(str(LAST_VERSION))


async def __main(client: TelegramClient, config: dict[str, Any]) -> None:
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

    with suppress(TypeError):
        await client.end_takeout(success=False)

    async with client.takeout(users=True) as takeout:
        for chat in config["export"]["chats"]:
            await migrate(takeout, config, chat)


if __name__ == "__main__":
    with Path("ream.toml").open("rb") as f:
        config = tomllib.load(f)

    client = TelegramClient(
        "ream",
        config["api"]["app_id"],
        config["api"]["app_hash"],
        app_version="1.0.0",
    )

    with client:
        client.loop.run_until_complete(__main(client, config))
