import tomllib

import serialization

import telethon  # type: ignore
from telethon.hints import EntityLike  # type: ignore


async def export(client: telethon.TelegramClient, chat: EntityLike) -> None:
    print("[")
    async with client.takeout(
        users=True,
        files=True,
        max_file_size=config["export"]["max_file_size"],
    ) as takeout:
        message: telethon.types.Message
        async for message in takeout.iter_messages(chat, reverse=True):
            data = await serialization.serialize(message)
            print(data)
            print(",")
    print("]")


async def main(client: telethon.TelegramClient) -> None:
    for chat in config["export"]["chats"]:
        print(f"Exporting chat {chat}...")
        await export(client, chat)


if __name__ == "__main__":
    with open("ream.toml", "rb") as f:
        config = tomllib.load(f)

    client = telethon.TelegramClient(
        "ream",
        config["api"]["app_id"],
        config["api"]["app_hash"],
    )

    with client:
        client.loop.run_until_complete(main(client))
