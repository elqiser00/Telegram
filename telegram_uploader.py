#!/usr/bin/env python3
import os
import sys
import asyncio
import aiohttp
import requests
from telethon import TelegramClient
from telethon.sessions import StringSession
import subprocess
import ssl
import urllib3
import time
import re

# تعطيل التحقق من SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

print("🚀 SCRIPT STARTED - DEBUG MODE")
print(f"✅ Python: {sys.version}")
print(f"✅ Working dir: {os.getcwd()}")

# فحص الـ imports
try:
    print("🔍 Testing imports...")
    import asyncio
    print("✅ asyncio")
    import aiohttp
    print("✅ aiohttp")
    import requests
    print("✅ requests")
    from telethon import TelegramClient
    print("✅ telethon")
    from telethon.sessions import StringSession
    print("✅ StringSession")
    print("✅ All imports successful!")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class TelegramUploader:
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.session_string = os.getenv('TELEGRAM_SESSION_STRING')
        self.client = None
        self.last_update_time = 0
        
        print("🔧 TelegramUploader initialized")
        print(f"   API_ID: {'SET' if self.api_id else 'NOT SET'}")
        print(f"   API_HASH: {'SET' if self.api_hash else 'NOT SET'}")
        print(f"   SESSION: {'SET' if self.session_string else 'NOT SET'}")
        
    async def init_client(self):
        """تهيئة العميل التليجرام"""
        try:
            print("🔌 جاري الاتصال بتليجرام...")
            
            if not all([self.api_id, self.api_hash, self.session_string]):
                print("❌ معلومات تليجرام ناقصة!")
                return False
                
            self.client = TelegramClient(
                StringSession(self.session_string), 
                int(self.api_id), 
                self.api_hash,
                device_model="Python Uploader",
                system_version="Linux",
                app_version="1.0"
            )
            
            # إعدادات لمنع التجميد
            self.client.flood_sleep_threshold = 60
            
            print("   📞 جاري بدء العميل...")
            await self.client.start()
            print("✅ تم الاتصال بتليجرام بنجاح")
            
            # اختبار الاتصال
            me = await self.client.get_me()
            print(f"   👤 مسجل الدخول كـ: {me.first_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ فشل الاتصال بتليجرام: {e}")
            return False
        
    async def download_file(self, url, filename):
        """تحميل الملف مع تعطيل SSL verification"""
        try:
            print(f"📥 جاري تحميل {filename}...")
            print(f"   📍 الرابط: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=False, timeout=300) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded_size = 0
                        
                        with open(filename, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                if not chunk:
                                    break
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                
                                # تحديث الـ progress كل 10 ثواني فقط
                                current_time = time.time()
                                if current_time - self.last_update_time >= 10:
                                    if total_size > 0:
                                        percent = (downloaded_size / total_size) * 100
                                        print(f"   📥 التحميل: {percent:.1f}%")
                                    else:
                                        print(f"   📥 تم تحميل: {downloaded_size} bytes")
                                    self.last_update_time = current_time
                        
                        print(f"✅ تم تحميل {filename} بنجاح - {downloaded_size} bytes")
                        return True
                    else:
                        print(f"❌ فشل التحميل: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ خطأ في التحميل: {e}")
            return False
    
    def add_logo_to_video(self, video_path, logo_path, output_path):
        """إضافة لوجو إلى الفيديو"""
        try:
            print("🎨 جاري إضافة اللوجو إلى الفيديو...")
            
            if not os.path.exists(video_path):
                print(f"❌ ملف الفيديو غير موجود: {video_path}")
                return False
                
            if not os.path.exists(logo_path):
                print(f"❌ ملف اللوجو غير موجود: {logo_path}")
                return False
            
            cmd = [
                'ffmpeg', '-i', video_path, '-i', logo_path,
                '-filter_complex', '[1]scale=150:150[logo];[0][logo]overlay=10:10',
                '-codec:a', 'copy', output_path, '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ تم إضافة اللوجو بنجاح")
                return True
            else:
                print("❌ خطأ في إضافة اللوجو")
                if result.stderr:
                    print(f"   📝 تفاصيل: {result.stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في إضافة اللوجو: {e}")
            return False
    
    def rename_file(self, file_path, new_name):
        """إعادة تسمية الملف"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ الملف غير موجود: {file_path}")
                return file_path
                
            directory = os.path.dirname(file_path)
            extension = os.path.splitext(file_path)[1]
            new_path = os.path.join(directory, f"{new_name}{extension}")
            os.rename(file_path, new_path)
            print(f"✏️ تم إعادة التسمية إلى: {new_name}{extension}")
            return new_path
        except Exception as e:
            print(f"⚠️ خطأ في إعادة التسمية: {e}")
            return file_path

    async def find_channel_entity(self, channel_input):
        """البحث عن القناة بطرق مختلفة"""
        try:
            print(f"   🔍 جاري البحث عن القناة: {channel_input}")
            
            # تنظيف المدخل
            channel_input = channel_input.strip()
            
            # المحاولة 1: رابط دعوة
            if '+_' in channel_input or 't.me/+' in channel_input:
                print(f"   🔍 المحاولة 1: رابط دعوة")
                try:
                    invite_hash = channel_input.split('t.me/+')[-1] if 't.me/+' in channel_input else channel_input
                    invite_hash = invite_hash.replace('+', '').strip()
                    
                    print(f"   🔑 جاري الانضمام برابط الدعوة: {invite_hash}")
                    result = await self.client.import_chat_invite(invite_hash)
                    
                    if result and hasattr(result, 'chats') and result.chats:
                        entity = await self.client.get_entity(result.chats[0].id)
                        print(f"   ✅ تم الانضمام للقناة: {getattr(entity, 'title', 'Unknown')}")
                        return entity
                except Exception as e:
                    print(f"   ⚠️ فشل رابط الدعوة: {e}")
            
            # المحاولة 2: البحث برقم القناة
            try:
                print(f"   🔍 المحاولة 2: البحث برقم القناة")
                numbers = re.findall(r'-?\d+', channel_input)
                for number in numbers:
                    if len(str(abs(int(number)))) > 8:
                        try:
                            entity = await self.client.get_entity(int(number))
                            print(f"   ✅ تم العثور بالرقم: {number}")
                            return entity
                        except:
                            continue
            except Exception as e:
                print(f"   ⚠️ فشل البحث بالرقم: {e}")
            
            # المحاولة 3: البحث في الدردشات
            try:
                print(f"   🔍 المحاولة 3: البحث في الدردشات")
                async for dialog in self.client.iter_dialogs(limit=50):
                    if hasattr(dialog.entity, 'id'):
                        if str(dialog.entity.id) in channel_input:
                            print(f"   ✅ تم العثور في الدردشات")
                            return dialog.entity
            except Exception as e:
                print(f"   ⚠️ فشل البحث في الدردشات: {e}")
            
            print(f"   ❌ لم يتم العثور على القناة")
            return None
            
        except Exception as e:
            print(f"❌ خطأ في البحث عن القناة: {e}")
            return None
    
    async def upload_to_telegram(self, file_paths, channel_input, post_type, title=None, links=None):
        """رفع الملفات إلى قناة التليجرام"""
        try:
            print(f"📤 جاري الرفع إلى القناة: {channel_input}")
            
            entity = await self.find_channel_entity(channel_input)
            
            if not entity:
                print(f"❌ لا يمكن العثور على القناة")
                return False
            
            print(f"   ✅ تم العثور على القناة: {getattr(entity, 'title', 'Unknown')}")
            
            if post_type == 'movie':
                image_files = [f for f in file_paths if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                video_files = [f for f in file_paths if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
                
                if image_files and video_files:
                    caption = f"🎬 **{title}**\n\n" if title else "🎬 **فيلم جديد**\n\n"
                    
                    print("   🖼️ رفع الصورة...")
                    uploaded_photo = await self.client.upload_file(image_files[0])
                    
                    print("   🎬 رفع الفيديو...")
                    uploaded_video = await self.client.upload_file(video_files[0])
                    
                    await self.client.send_file(entity, [uploaded_photo, uploaded_video], caption=caption)
                    print("✅ تم رفع البوست بنجاح")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ خطأ في الرفع إلى تليجرام: {e}")
            return False
    
    async def process_content(self, download_url, logo_url, channel_username, content_type, 
                            rename_option=False, new_name=None, series_links=None):
        """معالجة المحتوى بالكامل"""
        try:
            print("🔄 بدء معالجة المحتوى...")
            
            # الاتصال بتليجرام أولاً
            if not await self.init_client():
                return False
            
            # تحميل الفيديو
            video_filename = "video.mp4"
            print(f"📥 تحميل الفيديو...")
            if not await self.download_file(download_url, video_filename):
                return False
            
            # تحميل اللوجو
            logo_filename = "logo.png"
            print(f"📥 تحميل اللوجو...")
            logo_success = await self.download_file(logo_url, logo_filename)
            if not logo_success:
                logo_filename = None
            
            # إعادة تسمية الملف
            final_video_path = video_filename
            if rename_option and new_name:
                final_video_path = self.rename_file(video_filename, new_name)
            
            # إضافة اللوجو
            output_filename = "final_video.mp4"
            if logo_filename:
                if self.add_logo_to_video(final_video_path, logo_filename, output_filename):
                    final_video_path = output_filename
            
            # رفع المحتوى
            files_to_upload = []
            if content_type == 'movie' and logo_filename:
                files_to_upload.append(logo_filename)
            files_to_upload.append(final_video_path)
            
            print(f"📤 الرفع إلى تليجرام...")
            upload_success = await self.upload_to_telegram(
                files_to_upload, channel_username, content_type, title=new_name
            )
            
            # تنظيف الملفات
            self.cleanup_files([video_filename, logo_filename, output_filename])
            
            return upload_success
            
        except Exception as e:
            print(f"❌ خطأ في معالجة المحتوى: {e}")
            return False
    
    def cleanup_files(self, files):
        """تنظيف الملفات المؤقتة"""
        cleaned = 0
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned += 1
            except:
                pass
        print(f"🧹 تم تنظيف {cleaned} ملف")

async def main():
    print("=" * 50)
    print("🎯 MAIN FUNCTION STARTED")
    print("=" * 50)
    
    uploader = TelegramUploader()
    
    # قراءة البيانات
    download_url = os.getenv('INPUT_DOWNLOAD_URL')
    logo_url = os.getenv('INPUT_LOGO_URL')
    channel_username = os.getenv('INPUT_CHANNEL_USERNAME')
    content_type = os.getenv('INPUT_CONTENT_TYPE', 'movie')
    rename_option = os.getenv('INPUT_RENAME_FILE', 'false').lower() == 'true'
    new_name = os.getenv('INPUT_NEW_NAME', '')
    
    print("📋 معلومات المدخلات:")
    print(f"   📥 رابط الفيديو: {download_url}")
    print(f"   🖼️ رابط اللوجو: {logo_url}")
    print(f"   📢 القناة: {channel_username}")
    print(f"   🎬 النوع: {content_type}")
    print(f"   ✏️ إعادة تسمية: {rename_option}")
    if new_name:
        print(f"   📝 الاسم الجديد: {new_name}")
    print("=" * 50)
    
    success = await uploader.process_content(
        download_url=download_url,
        logo_url=logo_url,
        channel_username=channel_username,
        content_type=content_type,
        rename_option=rename_option,
        new_name=new_name
    )
    
    print("=" * 50)
    if success:
        print("✅ تم الرفع بنجاح!")
        return 0
    else:
        print("❌ فشل الرفع!")
        return 1

if __name__ == "__main__":
    print("⭐ STARTING SCRIPT EXECUTION")
    try:
        exit_code = asyncio.run(main())
        print(f"⭐ SCRIPT COMPLETED WITH CODE: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        print(f"💥 SCRIPT CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
