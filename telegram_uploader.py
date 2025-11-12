import os
import asyncio
import aiohttp
import requests
from telethon import TelegramClient, events
from telethon.tl.types import InputMediaUploadedDocument
from PIL import Image, ImageDraw, ImageFont
import subprocess
import ssl
import urllib3

# تعطيل التحقق من SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

class TelegramUploader:
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.session_string = os.getenv('TELEGRAM_SESSION_STRING')
        self.client = None
        
    async def init_client(self):
        """تهيئة العميل التليجرام"""
        self.client = TelegramClient(
            StringSession(self.session_string), 
            self.api_id, 
            self.api_hash
        )
        await self.client.start()
        
    async def download_video(self, url, filename):
        """تحميل الفيديو مع تعطيل SSL verification"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        with open(filename, 'wb') as f:
                            while True:
                                chunk = await response.content.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                        return True
        except Exception as e:
            print(f"Error downloading video: {e}")
            return False
    
    def add_logo_to_video(self, video_path, logo_path, output_path, position='left'):
        """إضافة لوجو إلى الفيديو"""
        try:
            # استخدام ffmpeg لإضافة اللوجو
            if position == 'left':
                overlay = '10:10'  # أعلى اليسار
            else:
                overlay = 'main_w-overlay_w-10:10'  # أعلى اليمين
                
            cmd = [
                'ffmpeg', '-i', video_path, '-i', logo_path,
                '-filter_complex', f'[1]scale=100:100[logo];[0][logo]overlay={overlay}',
                '-codec:a', 'copy', output_path, '-y'
            ]
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            print(f"Error adding logo: {e}")
            return False
    
    def rename_file(self, file_path, new_name):
        """إعادة تسمية الملف"""
        try:
            directory = os.path.dirname(file_path)
            extension = os.path.splitext(file_path)[1]
            new_path = os.path.join(directory, f"{new_name}{extension}")
            os.rename(file_path, new_path)
            return new_path
        except Exception as e:
            print(f"Error renaming file: {e}")
            return file_path
    
    async def upload_to_telegram(self, file_paths, channel_username, post_type, title=None, links=None):
        """رفع الملفات إلى قناة التليجرام"""
        try:
            entity = await self.client.get_entity(channel_username)
            
            if post_type == 'movie':
                # رفع فيلم مع صورة وفيديو في نفس البوست
                if len(file_paths) >= 2:
                    # تحديد الملفات (الصورة الأولى، الفيديو الثاني)
                    image_file = file_paths[0] if file_paths[0].lower().endswith(('.jpg', '.png', '.jpeg')) else None
                    video_file = file_paths[1] if file_paths[1].lower().endswith(('.mp4', '.avi', '.mkv')) else None
                    
                    if image_file and video_file:
                        # رفع الصورة
                        uploaded_photo = await self.client.upload_file(image_file)
                        
                        # رفع الفيديو
                        uploaded_video = await self.client.upload_file(video_file)
                        
                        # إنشاء البوست مع الصورة والفيديو
                        caption = f"🎬 **{title}**\n\n" if title else "🎬 **فيلم جديد**\n\n"
                        
                        await self.client.send_file(
                            entity,
                            [uploaded_photo, uploaded_video],
                            caption=caption
                        )
            
            elif post_type == 'series':
                # رفع مسلسل مع روابط متعددة
                caption = f"📺 **{title}**\n\n" if title else "📺 **مسلسل جديد**\n\n"
                
                if links:
                    for i, link in enumerate(links[:10], 1):
                        caption += f"الحلقة {i}: {link}\n"
                
                # رفع جميع الملفات
                uploaded_files = []
                for file_path in file_paths:
                    uploaded_file = await self.client.upload_file(file_path)
                    uploaded_files.append(uploaded_file)
                
                await self.client.send_file(
                    entity,
                    uploaded_files,
                    caption=caption
                )
            
            return True
            
        except Exception as e:
            print(f"Error uploading to Telegram: {e}")
            return False
    
    async def process_content(self, download_url, logo_url, channel_username, content_type, 
                            rename_option=False, new_name=None, series_links=None):
        """معالجة المحتوى بالكامل"""
        try:
            await self.init_client()
            
            # تحميل الفيديو
            video_filename = "downloaded_video.mp4"
            print("جاري تحميل الفيديو...")
            download_success = await self.download_video(download_url, video_filename)
            
            if not download_success:
                return False
            
            # تحميل اللوجو
            logo_filename = "logo.png"
            logo_success = await self.download_video(logo_url, logo_filename)
            
            if not logo_success:
                return False
            
            # إعادة تسمية الملف إذا طلب المستخدم
            if rename_option and new_name:
                video_filename = self.rename_file(video_filename, new_name)
            
            # إضافة اللوجو إلى الفيديو
            output_filename = "video_with_logo.mp4"
            print("جاري إضافة اللوجو...")
            logo_success = self.add_logo_to_video(video_filename, logo_filename, output_filename)
            
            if not logo_success:
                output_filename = video_filename  # استخدام الفيديو الأصلي إذا فشلت إضافة اللوجو
            
            # رفع المحتوى إلى التليجرام
            files_to_upload = [logo_filename, output_filename] if content_type == 'movie' else [output_filename]
            
            print("جاري الرفع إلى التليجرام...")
            upload_success = await self.upload_to_telegram(
                files_to_upload, 
                channel_username, 
                content_type,
                title=new_name,
                links=series_links
            )
            
            # تنظيف الملفات المؤقتة
            try:
                os.remove(video_filename)
                os.remove(logo_filename)
                os.remove(output_filename)
            except:
                pass
            
            return upload_success
            
        except Exception as e:
            print(f"Error in process_content: {e}")
            return False

# دالة للتفاعل مع المستخدم
async def main():
    uploader = TelegramUploader()
    
    print("🚀 Telegram Uploader Bot")
    print("=" * 30)
    
    # إدخال البيانات
    download_url = input("🔗 رابط تحميل الفيديو: ")
    logo_url = input("🖼️ رابط اللوجو: ")
    channel_username = input("📢 رابط القناة (@username): ")
    
    print("\n📝 نوع المحتوى:")
    print("1 - فيلم 🎬")
    print("2 - مسلسل 📺")
    content_choice = input("اختر النوع (1/2): ")
    
    content_type = 'movie' if content_choice == '1' else 'series'
    
    rename_option = input("🔄 هل تريد إعادة تسمية الملف؟ (y/n): ").lower() == 'y'
    new_name = None
    if rename_option:
        new_name = input("✏️ الاسم الجديد: ")
    
    series_links = None
    if content_type == 'series':
        print("🔗 إضافة روابط الحلقات (حتى 10 روابط، اكتب 'done' للإنهاء):")
        series_links = []
        for i in range(10):
            link = input(f"رابط الحلقة {i+1}: ")
            if link.lower() == 'done':
                break
            series_links.append(link)
    
    # معالجة المحتوى
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
    else:
        print("❌ فشل الرفع!")

if __name__ == "__main__":
    asyncio.run(main())
