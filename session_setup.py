from telethon import TelegramClient
from telethon.sessions import StringSession
import os

async def create_session():
    api_id = int(input("أدخل API ID: "))
    api_hash = input("أدخل API HASH: ")
    
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.start()
    
    print("\n" + "="*50)
    print("SESSION STRING (احفظ هذا في GitHub Secrets):")
    print(client.session.save())
    print("="*50)

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_session())
