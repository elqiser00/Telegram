#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Telegram Session String
توليد Session String لـ Telegram
"""

from pyrogram import Client
import asyncio

print("=" * 60)
print("🔑 Telegram Session String Generator")
print("=" * 60)
print()
print("للحصول على API ID و API Hash:")
print("1. اذهب إلى: https://my.telegram.org")
print("2. سجل دخول برقم هاتفك")
print("3. اختر 'API development tools'")
print("4. أنشئ تطبيق جديد")
print()
print("=" * 60)
print()

# طلب البيانات من المستخدم
API_ID = input("أدخل API ID: ").strip()
API_HASH = input("أدخل API Hash: ").strip()

if not API_ID or not API_HASH:
    print("\n❌ خطأ: يجب إدخال API ID و API Hash")
    exit(1)

try:
    API_ID = int(API_ID)
except ValueError:
    print("\n❌ خطأ: API ID يجب أن يكون رقم")
    exit(1)


async def generate_session():
    """
    توليد Session String
    """
    print("\n📱 سيتم طلب رقم الهاتف ورمز التحقق...")
    print("=" * 60)
    
    try:
        async with Client("temp_session", api_id=API_ID, api_hash=API_HASH) as app:
            session_string = await app.export_session_string()
            
            print("\n" + "=" * 60)
            print("✅ تم التوليد بنجاح!")
            print("=" * 60)
            print()
            print("📋 Session String الخاص بك:")
            print("=" * 60)
            print(session_string)
            print("=" * 60)
            print()
            print("⚠️ احفظ هذا النص في مكان آمن!")
            print("⚠️ لا تشاركه مع أي شخص!")
            print()
            print("🔹 استخدمه في GitHub Secrets باسم: SESSION_STRING")
            print()
            
            # حفظ في ملف
            with open("session_string.txt", "w") as f:
                f.write(session_string)
            
            print("💾 تم حفظ Session String في ملف: session_string.txt")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        print("\nتأكد من:")
        print("- صحة API ID و API Hash")
        print("- إدخال رقم الهاتف بشكل صحيح (مع رمز الدولة)")
        print("- إدخال رمز التحقق الصحيح")


# تشغيل الدالة
if __name__ == "__main__":
    print("🚀 جاري التوليد...")
    asyncio.run(generate_session())
