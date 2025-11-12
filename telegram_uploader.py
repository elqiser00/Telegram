import os
import asyncio
import aiohttp
import requests
from telethon import TelegramClient
from telethon.sessions import StringSession
import subprocess
import ssl
import urllib3
import sys
import time

# تعطيل التحقق من SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

class TelegramUploader:
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.session_string = os.getenv('TELEGRAM_SESSION_STRING')
        self.client = None
        self.last_update_time = 0
        
    async def init_client(self):
        """تهيئة العميل التليجرام"""
        self.client = TelegramClient(
            StringSession(self.session_string), 
            int(self.api_id), 
            self.api_hash
        )
        await self.client.start()
        print("✅ تم الاتصال بتليجرام بنجاح")
        
    async def download_file(self, url, filename):
        """تحميل الملف مع تعطيل SSL verification"""
        try:
            print(f"📥 جاري تحميل {filename}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded_size = 0
                        
                        with open(filename, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                
                                # تحديث الـ progress كل 10 ثواني فقط
                                current_time = time.time()
                                if current_time - self.last_update_time >= 10:
                                    if total_size > 0:
                                        percent = (downloaded_size / total_size) * 100
                                        print(f"📥 التحميل: {percent:.1f}% ({downloaded_size}/{total_size} bytes)")
                                    else:
                                        print(f"📥 تم تحميل: {downloaded_size} bytes")
                                    self.last_update_time = current_time
                        
                        # طباعة النتيجة النهائية
                        print(f"✅ تم تحميل {filename} بنجاح - {downloaded_size} bytes")
                        return True
                    else:
                        print(f"❌ فشل التحميل: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ خطأ في التحميل: {e}")
            return False
    
    def add_logo_to_video(self, video_path, logo_path, output_path, position='top-left'):
        """إضافة لوجو إلى الفيديو"""
        try:
            print("🎨 جاري إضافة اللوجو إلى الفيديو...")
            
            if position == 'top-left':
                overlay = '10:10'
            elif position == 'top-right':
                overlay = 'main_w-overlay_w-10:10'
            else:
                overlay = '10:10'
                
            cmd = [
                'ffmpeg', '-i', video_path, '-i', logo_path,
                '-filter_complex', f'[1]scale=150:150[logo];[0][logo]overlay={overlay}',
                '-codec:a', 'copy', output_path, '-y'
            ]
            
            # تشغيل ffmpeg بدون output مزعج
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ تم إضافة اللوجو بنجاح")
                return True
            else:
                print(f"❌ خطأ في ffmpeg")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في إضافة اللوجو: {e}")
            return False
    
    def rename_file(self, file_path, new_name):
        """إعادة تسمية الملف"""
        try:
            directory = os.path.dirname(file_path)
            extension = os.path.splitext(file_path)[1]
            new_path = os.path.join(directory, f"{new_name}{extension}")
            os.rename(file_path, new_path)
            print(f"✏️ تم إعادة التسمية إلى: {new_name}{extension}")
            return new_path
        except Exception as e:
            print(f"⚠️ خطأ في إعادة التسمية: {e}")
            return file_path
    
    async def upload_media_group(self, entity, files, caption):
        """رفع مجموعة وسائط"""
        try:
            print("📤 جاري رفع الملفات...")
            uploaded_files = []
            
            for i, file_path in enumerate(files, 1):
                print(f"📤 رفع الملف {i}/{len(files)}...")
                uploaded_file = await self.client.upload_file(file_path)
                uploaded_files.append(uploaded_file)
            
            await self.client.send_file(entity, uploaded_files, caption=caption)
            print("✅ تم رفع الملفات بنجاح")
            return True
        except Exception as e:
            print(f"❌ خطأ في رفع المجموعة: {e}")
            return False
    
    async def upload_single_post(self, entity, image_path, video_path, caption):
        """رفع بوست واحد بصورة وفيديو"""
        try:
            print("📤 جاري رفع البوست...")
            
            # رفع الصورة
            print("🖼️ رفع الصورة...")
            uploaded_photo = await self.client.upload_file(image_path)
            
            # رفع الفيديو
            print("🎬 رفع الفيديو...")
            uploaded_video = await self.client.upload_file(video_path)
            
            # إرسال معًا
            await self.client.send_file(
                entity,
                [uploaded_photo, uploaded_video],
                caption=caption
            )
            print("✅ تم رفع البوست بنجاح")
            return True
        except Exception as e:
            print(f"❌ خطأ في رفع البوست: {e}")
            return False
    
    async def upload_to_telegram(self, file_paths, channel_username, post_type, title=None, links=None):
        """رفع الملفات إلى قناة التليجرام"""
        try:
            print(f"📤 جاري الرفع إلى القناة: {channel_username}")
            entity = await self.client.get_entity(channel_username)
            
            if post_type == 'movie':
                # البحث عن الصورة والفيديو
                image_files = [f for f in file_paths if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                video_files = [f for f in file_paths if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
                
                if image_files and video_files:
                    caption = f"🎬 **{title}**\n\n" if title else "🎬 **فيلم جديد**\n\n"
                    success = await self.upload_single_post(entity, image_files[0], video_files[0], caption)
                    return success
            
            elif post_type == 'series':
                caption = f"📺 **{title}**\n\n" if title else "📺 **مسلسل جديد**\n\n"
                
                if links:
                    caption += "**روابط الحلقات:**\n"
                    for i, link in enumerate(links[:10], 1):
                        caption += f"الحلقة {i}: {link}\n"
                
                success = await self.upload_media_group(entity, file_paths, caption)
                return success
            
            return False
            
        except Exception as e:
            print(f"❌ خطأ في الرفع إلى تليجرام: {e}")
            return False
    
    async def process_content(self, download_url, logo_url, channel_username, content_type, 
                            rename_option=False, new_name=None, series_links=None):
        """معالجة المحتوى بالكامل"""
        try:
            await self.init_client()
            
            # تحميل الفيديو
            video_filename = "downloaded_video.mp4"
            download_success = await self.download_file(download_url, video_filename)
            
            if not download_success:
                return False
            
            # تحميل اللوجو
            logo_filename = "logo.png"
            logo_success = await self.download_file(logo_url, logo_filename)
            
            if not logo_success:
                print("⚠️ فشل تحميل اللوجو، المتابعة بدون لوجو")
                logo_filename = None
            
            # إعادة تسمية الملف إذا طلب المستخدم
            final_video_path = video_filename
            if rename_option and new_name:
                final_video_path = self.rename_file(video_filename, new_name)
            
            # إضافة اللوجو إلى الفيديو إذا كان موجودًا
            output_filename = "final_video.mp4"
            if logo_filename and os.path.exists(logo_filename):
                logo_success = self.add_logo_to_video(final_video_path, logo_filename, output_filename, 'top-left')
                if logo_success:
                    final_video_path = output_filename
                else:
                    print("⚠️ فشل إضافة اللوجو، المتابعة بدون لوجو")
                    final_video_path = video_filename
            else:
                final_video_path = video_filename
            
            # رفع المحتوى إلى التليجرام
            files_to_upload = []
            
            if content_type == 'movie':
                # إضافة صورة وفيديو للفيلم
                if logo_filename and os.path.exists(logo_filename):
                    files_to_upload.append(logo_filename)
                files_to_upload.append(final_video_path)
            else:
                # للمسلسلات، رفع الفيديو فقط
                files_to_upload.append(final_video_path)
            
            print("📤 جاري الرفع إلى تليجرام...")
            upload_success = await self.upload_to_telegram(
                files_to_upload, 
                channel_username, 
                content_type,
                title=new_name,
                links=series_links
            )
            
            # تنظيف الملفات المؤقتة
            self.cleanup_files([video_filename, logo_filename, output_filename])
            
            return upload_success
            
        except Exception as e:
            print(f"❌ خطأ في معالجة المحتوى: {e}")
            return False
    
    def cleanup_files(self, files):
        """تنظيف الملفات المؤقتة"""
        print("🧹 جاري تنظيف الملفات المؤقتة...")
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        print("✅ تم التنظيف")

# دالة رئيسية تعمل مع GitHub Actions
async def main_github():
    uploader = TelegramUploader()
    
    # قراءة البيانات من environment variables
    download_url = os.getenv('INPUT_DOWNLOAD_URL')
    logo_url = os.getenv('INPUT_LOGO_URL')
    channel_username = os.getenv('INPUT_CHANNEL_USERNAME')
    content_type = os.getenv('INPUT_CONTENT_TYPE', 'movie')
    rename_option = os.getenv('INPUT_RENAME_FILE', 'false').lower() == 'true'
    new_name = os.getenv('INPUT_NEW_NAME', '')
    series_links_str = os.getenv('INPUT_SERIES_LINKS', '')
    
    series_links = []
    if series_links_str:
        series_links = [link.strip() for link in series_links_str.split(',') if link.strip()]
    
    print("🚀 بدء عملية الرفع...")
    print(f"📥 رابط الفيديو: {download_url}")
    print(f"🖼️ رابط اللوجو: {logo_url}")
    print(f"📢 القناة: {channel_username}")
    print(f"🎬 النوع: {content_type}")
    print(f"✏️ إعادة تسمية: {rename_option}")
    if new_name:
        print(f"📝 الاسم الجديد: {new_name}")
    if series_links:
        print(f"🔗 عدد روابط المسلسل: {len(series_links)}")
    print("=" * 50)
    
    success = await uploader.process_content(
        download_url=download_url,
        logo_url=logo_url,
        channel_username=channel_username,
        content_type=content_type,
        rename_option=rename_option,
        new_name=new_name,
        series_links=series_links
    )
    
    if success:
        print("✅ تم الرفع بنجاح!")
        sys.exit(0)
    else:
        print("❌ فشل الرفع!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main_github())
