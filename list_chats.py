#!/usr/bin/env python3
"""List all available Telegram chats with their IDs for backup configuration."""

import asyncio
import tomllib
from pathlib import Path

import telethon


async def list_chats(client: telethon.TelegramClient) -> None:
    """List all available chats with their IDs and basic info."""
    print("📱 Getting your Telegram chats...\n")
    
    dialogs = await client.get_dialogs()
    
    print("Available chats for backup:")
    print("=" * 60)
    
    personal_chats = []
    groups = []
    channels = []
    
    for dialog in dialogs:
        entity = dialog.entity
        entity_type = type(entity).__name__
        
        try:
            if hasattr(entity, 'first_name'):  # User/Personal chat
                name = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
                username = f"@{entity.username}" if hasattr(entity, 'username') and entity.username else ""
                personal_chats.append({
                    'id': entity.id,
                    'name': name,
                    'username': username,
                    'type': entity_type,
                })
            elif hasattr(entity, 'title'):  # Group or Channel
                is_group = (hasattr(entity, 'megagroup') and entity.megagroup) or \
                          (hasattr(entity, 'gigagroup') and entity.gigagroup) or \
                          entity_type in ['Chat', 'ChatForbidden']
                
                chat_info = {
                    'id': entity.id,
                    'name': entity.title,
                    'username': f"@{entity.username}" if hasattr(entity, 'username') and entity.username else "",
                    'type': entity_type,
                }
                
                if is_group:
                    groups.append(chat_info)
                else:
                    channels.append(chat_info)
        except Exception as e:
            print(f"   ⚠️  Skipped entity {entity.id} ({entity_type}): {e}")
    
    # Display personal chats
    if personal_chats:
        print("👤 Personal Chats:")
        for chat in personal_chats:
            print(f"   ID: {chat['id']:>12} | {chat['name']:<30} {chat['username']:<20} ({chat['type']})")
    
    # Display groups
    if groups:
        print(f"\n👥 Groups:")
        for group in groups:
            print(f"   ID: {group['id']:>12} | {group['name']:<30} {group['username']:<20} ({group['type']})")
    
    # Display channels
    if channels:
        print(f"\n📢 Channels:")
        for channel in channels:
            print(f"   ID: {channel['id']:>12} | {channel['name']:<30} {channel['username']:<20} ({channel['type']})")
    
    print("\n" + "=" * 60)
    print("💡 To backup chats, copy the IDs you want and add them to ream.toml")
    print("   Example: chats = [1234567890, -1001234567890]")
    print("\n📝 Note: Negative IDs are normal for groups and channels")


async def main():
    """Main function to list chats."""
    try:
        with Path("ream.toml").open("rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        print("❌ Error: ream.toml file not found!")
        print("   Make sure you're running this from the correct directory.")
        return
    except Exception as e:
        print(f"❌ Error reading ream.toml: {e}")
        return
    
    client = telethon.TelegramClient(
        "ream",
        config["api"]["app_id"],
        config["api"]["app_hash"],
        app_version="1.0.0",
    )
    
    try:
        async with client:
            await list_chats(client)
    except Exception as e:
        print(f"❌ Error connecting to Telegram: {e}")
        print("   Make sure your API credentials in ream.toml are correct.")


if __name__ == "__main__":
    asyncio.run(main()) 