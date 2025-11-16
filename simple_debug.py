#!/usr/bin/env python3
import os
import sys
import asyncio

print("🚀 SIMPLE DEBUG STARTED!")
print("=" * 50)

async def test_telegram():
    print("🔧 Testing Telegram connection...")
    
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        
        print("✅ Telethon imported successfully")
        
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        session_string = os.getenv('TELEGRAM_SESSION_STRING')
        
        print(f"📋 Credentials check:")
        print(f"   API_ID: {api_id}")
        print(f"   API_HASH: {'*' * 8 if api_hash else 'NOT SET'}")
        print(f"   SESSION: {'*' * 8 if session_string else 'NOT SET'}")
        
        if not all([api_id, api_hash, session_string]):
            print("❌ Missing credentials")
            return False
        
        print("🔌 Creating Telegram client...")
        client = TelegramClient(
            StringSession(session_string),
            int(api_id),
            api_hash
        )
        
        print("📞 Starting client...")
        await client.start()
        print("✅ Client started successfully!")
        
        me = await client.get_me()
        print(f"✅ Logged in as: {me.first_name}")
        
        print("📋 Getting dialogs...")
        count = 0
        async for dialog in client.iter_dialogs(limit=10):
            print(f"   💬 {dialog.name} (ID: {dialog.id})")
            count += 1
        
        print(f"✅ Found {count} dialogs")
        
        await client.disconnect()
        print("✅ Disconnected successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🎯 MAIN STARTED")
    success = await test_telegram()
    print("🎯 MAIN COMPLETED")
    return success

if __name__ == "__main__":
    print("⭐ SCRIPT STARTING")
    try:
        success = asyncio.run(main())
        print(f"⭐ SCRIPT COMPLETED: {'SUCCESS' if success else 'FAILED'}")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 SCRIPT CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
