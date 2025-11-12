# Telegram Uploader Bot

بوت لرفع الأفلام والمسلسلات إلى قناة تليجرام مع إضافة لوجو وتنسيق البوستات.

## المميزات

- ✅ رفع الأفلام مع لوجو
- ✅ رفع المسلسلات مع روابط متعددة  
- ✅ إعادة تسمية الملفات
- ✅ تخطي SSL verification
- ✅ تنسيق البوستات بشكل احترافي

## الإعداد

1. أضف Secrets في GitHub:
   - `TELEGRAM_API_ID`
   - `TELEGRAM_API_HASH` 
   - `TELEGRAM_SESSION_STRING`

2. إنشاء Session String:
   ```bash
   python session_setup.py
