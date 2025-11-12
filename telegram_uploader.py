#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Media Uploader
رفع الأفلام والمسلسلات على قناة Telegram
"""

import os
import sys
import asyncio
import requests
import warnings
from pathlib import Path
from pyrogram import Client
from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument

# تعطيل تحذيرات SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TelegramUploader:
    def __init__(self, session_string, api_id, api_hash):
        """
        تهيئة العميل
        :param session_string: Session String من Telegram
        :param api_id: API ID من my.telegram.org
        :param api_hash: API Hash من my.telegram.org
        """
        self.app = Client(
            "media_uploader",
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string
        )
        
    async def download_file(self, url, filename):
        """
        تحميل الملف من الرابط مع تخطي SSL verification
        """
        print(f"📥 جاري تحميل: {filename}")
        print(f"🔗 من: {url}")
        
        try:
            # تحميل مع تخطي SSL verification
            response = requests.get(
                url, 
                stream=True, 
                verify=False,  # تخطي SSL verification
                timeout=30,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r⏳ التقدم: {progress:.1f}%", end='')
            
            print(f"\n✅ تم التحميل: {filename}")
            return filename
            
        except requests.exceptions.SSLError as e:
            print(f"\n⚠️ خطأ SSL: {e}")
            print("🔄 محاولة التحميل بدون SSL verification...")
            # محاولة ثانية بدون SSL
            response = requests.get(url, stream=True, verify=False, timeout=60)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"✅ تم التحميل: {filename}")
            return filename
            
        except Exception as e:
            print(f"\n❌ خطأ في التحميل: {e}")
            raise
    
    async def upload_movie(self, channel, video_url, logo_path, custom_name=None, caption=""):
        """
        رفع فيلم (صورة + فيديو في بوست واحد)
        :param channel: رابط أو ID القناة
        :param video_url: رابط تحميل الفيديو
        :param logo_path: مسار لوجو الفيلم
        :param custom_name: اسم مخصص للفيديو (اختياري)
        :param caption: وصف البوست
        """
        async with self.app:
            # تحميل الفيديو
            video_filename = custom_name if custom_name else "movie.mp4"
            if not os.path.exists(video_filename):
                await self.download_file(video_url, video_filename)
            
            print(f"📤 جاري رفع الفيلم إلى القناة...")
            
            # إنشاء media group (صورة على اليسار + فيديو على اليمين)
            media_group = [
                InputMediaPhoto(logo_path, caption=caption),
                InputMediaVideo(video_filename)
            ]
            
            # رفع Media Group
            await self.app.send_media_group(
                chat_id=channel,
                media=media_group
            )
            
            print(f"✅ تم رفع الفيلم بنجاح!")
            
            # حذف الملف المؤقت
            if os.path.exists(video_filename):
                os.remove(video_filename)
    
    async def upload_series(self, channel, video_urls, logo_path, custom_names=None, caption=""):
        """
        رفع مسلسل (حتى 10 حلقات في بوست واحد)
        :param channel: رابط أو ID القناة
        :param video_urls: قائمة بروابط تحميل الحلقات (حتى 10)
        :param logo_path: مسار لوجو المسلسل
        :param custom_names: قائمة بأسماء مخصصة للحلقات (اختياري)
        :param caption: وصف البوست
        """
        async with self.app:
            if len(video_urls) > 10:
                print("⚠️ تحذير: يمكن رفع 10 حلقات كحد أقصى. سيتم رفع أول 10 حلقات فقط.")
                video_urls = video_urls[:10]
            
            media_group = []
            downloaded_files = []
            
            # إضافة اللوجو أولاً
            media_group.append(InputMediaPhoto(logo_path, caption=caption))
            
            # تحميل ورفع الحلقات
            for idx, video_url in enumerate(video_urls, start=1):
                video_filename = custom_names[idx-1] if custom_names and len(custom_names) >= idx else f"episode_{idx}.mp4"
                
                if not os.path.exists(video_filename):
                    await self.download_file(video_url, video_filename)
                
                downloaded_files.append(video_filename)
                media_group.append(InputMediaVideo(video_filename))
            
            print(f"📤 جاري رفع المسلسل ({len(video_urls)} حلقة) إلى القناة...")
            
            # رفع Media Group
            await self.app.send_media_group(
                chat_id=channel,
                media=media_group
            )
            
            print(f"✅ تم رفع المسلسل بنجاح!")
            
            # حذف الملفات المؤقتة
            for filename in downloaded_files:
                if os.path.exists(filename):
                    os.remove(filename)


def main():
    """
    الدالة الرئيسية
    """
    print("=" * 60)
    print("🎬 Telegram Media Uploader")
    print("=" * 60)
    
    # قراءة المتغيرات من GitHub Secrets أو البيئة
    SESSION_STRING = os.getenv('SESSION_STRING')
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    
    # التحقق من وجود المتغيرات الأساسية
    if not all([SESSION_STRING, API_ID, API_HASH]):
        print("❌ خطأ: يجب تعيين SESSION_STRING و API_ID و API_HASH في Secrets!")
        sys.exit(1)
    
    # قراءة المعلومات من GitHub Actions Inputs
    CONTENT_TYPE = os.getenv('CONTENT_TYPE', 'movie')  # movie أو series
    CHANNEL = os.getenv('CHANNEL')
    LOGO_PATH = os.getenv('LOGO_PATH')
    CAPTION = os.getenv('CAPTION', '')
    CUSTOM_NAME = os.getenv('CUSTOM_NAME', '')
    
    # التحقق من القناة واللوجو
    if not CHANNEL:
        print("❌ خطأ: يجب تحديد رابط القناة!")
        sys.exit(1)
    
    if not LOGO_PATH or not os.path.exists(LOGO_PATH):
        print("❌ خطأ: يجب تحديد مسار اللوجو الصحيح!")
        sys.exit(1)
    
    # إنشاء المُرفع
    uploader = TelegramUploader(SESSION_STRING, int(API_ID), API_HASH)
    
    # رفع حسب النوع
    if CONTENT_TYPE.lower() == 'movie':
        VIDEO_URL = os.getenv('VIDEO_URL')
        if not VIDEO_URL:
            print("❌ خطأ: يجب تحديد رابط الفيديو!")
            sys.exit(1)
        
        asyncio.run(uploader.upload_movie(
            channel=CHANNEL,
            video_url=VIDEO_URL,
            logo_path=LOGO_PATH,
            custom_name=CUSTOM_NAME if CUSTOM_NAME else None,
            caption=CAPTION
        ))
    
    elif CONTENT_TYPE.lower() == 'series':
        # قراءة روابط الحلقات (حتى 10)
        video_urls = []
        custom_names = []
        
        for i in range(1, 11):
            url = os.getenv(f'VIDEO_URL_{i}')
            if url:
                video_urls.append(url)
                custom_name = os.getenv(f'CUSTOM_NAME_{i}', '')
                if custom_name:
                    custom_names.append(custom_name)
        
        if not video_urls:
            print("❌ خطأ: يجب تحديد رابط حلقة واحدة على الأقل!")
            sys.exit(1)
        
        asyncio.run(uploader.upload_series(
            channel=CHANNEL,
            video_urls=video_urls,
            logo_path=LOGO_PATH,
            custom_names=custom_names if custom_names else None,
            caption=CAPTION
        ))
    
    else:
        print(f"❌ خطأ: نوع المحتوى غير صحيح: {CONTENT_TYPE}")
        print("يجب أن يكون: movie أو series")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✨ تمت العملية بنجاح!")
    print("=" * 60)


if __name__ == "__main__":
    main()
