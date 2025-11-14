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
import re

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
        try:
            print("🔌 جاري الاتصال بتليجرام...")
            
            if not all([self.api_id, self.api_hash, self.session_string]):
                print("❌ معلومات تليجرام ناقصة!")
                return False
                
            self.client = TelegramClient(
                StringSession(self.session_string), 
                int(self.api_id), 
                self.api_hash
            )
            
            await self.client.start()
            print("✅ تم الاتصال بتليجرام بنجاح")
            return True
            
        except Exception as e:
            print(f"❌ فشل الاتصال بتليجرام: {e}")
            return False
        
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

    async def find_channel_entity(self, channel_input):
        """البحث عن القناة بطرق مختلفة"""
        try:
            print(f"   🔍 جاري البحث عن القناة: {channel_input}")
            
            # تنظيف المدخل من المسافات
            channel_input = channel_input.strip()
            
            # المحاولة 1: إذا كان رابط دعوة (يبدأ بـ +)
            if '+_' in channel_input or channel_input.startswith('https://t.me/+') or channel_input.startswith('t.me/+'):
                print(f"   🔍 المحاولة 1: التعامل مع رابط الدعوة")
                try:
                    # استخراج الـ hash من رابط الدعوة
                    if 't.me/+' in channel_input:
                        invite_hash = channel_input.split('t.me/+')[-1]
                    elif '+_' in channel_input:
                        invite_hash = channel_input
                    else:
                        invite_hash = channel_input.replace('https://t.me/', '')
                    
                    # تنظيف الـ hash
                    invite_hash = invite_hash.strip().replace('+', '')
                    
                    print(f"   🔑 محاولة الانضمام برابط الدعوة: {invite_hash}")
                    
                    # الانضمام للقناة عبر رابط الدعوة
                    result = await self.client.import_chat_invite(invite_hash)
                    if result and hasattr(result, 'chats') and result.chats:
                        entity = await self.client.get_entity(result.chats[0].id)
                        print(f"   ✅ تم الانضمام للقناة عبر رابط الدعوة: {getattr(entity, 'title', 'Unknown')}")
                        return entity
                except Exception as e:
                    print(f"   ⚠️ فشل الانضمام عبر رابط الدعوة: {e}")
            
            # المحاولة 2: استخراج الرقم من الرابط
            try:
                print(f"   🔍 المحاولة 2: استخراج الرقم من الرابط")
                # البحث عن أرقام في النص
                numbers = re.findall(r'-?\d+', channel_input)
                if numbers:
                    for number in numbers:
                        # تجاهل الأرقام الصغيرة (مثل أرقام الرسائل)
                        if len(str(abs(int(number)))) > 8:
                            try:
                                entity = await self.client.get_entity(int(number))
                                print(f"   ✅ تم العثور على القناة بالرقم: {number}")
                                return entity
                            except:
                                continue
            except Exception as e:
                print(f"   ⚠️ فشل استخراج الرقم: {e}")
            
            # المحاولة 3: كـ username
            try:
                print(f"   🔍 المحاولة 3: البحث كـ username")
                username = channel_input
                
                # تنظيف الـ username من الروابط
                if 'https://t.me/' in username:
                    username = username.split('https://t.me/')[-1]
                elif 't.me/' in username:
                    username = username.split('t.me/')[-1]
                
                # إزالة الـ + إذا موجود
                username = username.replace('+', '')
                
                # إزالة أي parameters إضافية
                username = username.split('?')[0].split('/')[0]
                
                if username and not username.startswith('@'):
                    username = f"@{username}"
                
                if username and username != '@':
                    entity = await self.client.get_entity(username)
                    print(f"   ✅ تم العثور على القناة كـ username: {username}")
                    return entity
            except Exception as e:
                print(f"   ⚠️ فشل البحث كـ username: {e}")
            
            # المحاولة 4: البحث في الدردشات
            try:
                print(f"   🔍 المحاولة 4: البحث في الدردشات")
                async for dialog in self.client.iter_dialogs():
                    if hasattr(dialog.entity, 'id'):
                        # تحقق من الرقم
                        if str(dialog.entity.id) in channel_input:
                            print(f"   ✅ تم العثور على القناة في الدردشات بالرقم")
                            return dialog.entity
                        
                        # تحقق من username
                        if hasattr(dialog.entity, 'username') and dialog.entity.username:
                            username_clean = channel_input.replace('@', '').replace('https://t.me/', '').replace('t.me/', '').split('?')[0].replace('+', '')
                            if dialog.entity.username.lower() == username_clean.lower():
                                print(f"   ✅ تم العثور على القناة في الدردشات بالاسم")
                                return dialog.entity
                        
                        # تحقق من العنوان
                        if hasattr(dialog.entity, 'title'):
                            if dialog.entity.title.lower() in channel_input.lower():
                                print(f"   ✅ تم العثور على القناة في الدردشات بالعنوان")
                                return dialog.entity
            except Exception as e:
                print(f"   ⚠️ فشل البحث في الدردشات: {e}")
            
            print(f"   ❌ لم يتم العثور على القناة بأي طريقة")
            return None
            
        except Exception as e:
            print(f"❌ خطأ في البحث عن القناة: {e}")
            return None
    
    async def upload_to_telegram(self, file_paths, channel_input, post_type, title=None, links=None):
        """رفع الملفات إلى قناة التليجرام"""
        try:
            print(f"📤 جاري الرفع إلى القناة: {channel_input}")
            
            # البحث عن القناة
            entity = await self.find_channel_entity(channel_input)
            
            if not entity:
                print(f"❌ لا يمكن العثور على القناة: {channel_input}")
                print("💡 تأكد من:")
                print("   - رابط الدعوة صحيح")
                print("   - البوت مضاف للقناة")
                print("   - البوت عنده صلاحية الرفع")
                print("   - حاول استخدام رقم القناة مباشرة (مثل: -1001548535280)")
                return False
            
            print(f"   ✅ تم العثور على القناة: {getattr(entity, 'title', 'Unknown')}")
            print(f"   🔢 رقم القناة: {entity.id}")
            
            if post_type == 'movie':
                # البحث عن الصورة والفيديو
                image_files = [f for f in file_paths if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                video_files = [f for f in file_paths if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
                
                if image_files and video_files:
                    caption = f"🎬 **{title}**\n\n" if title else "🎬 **فيلم جديد**\n\n"
                    
                    # رفع الصورة
                    print("   🖼️ رفع الصورة...")
                    uploaded_photo = await self.client.upload_file(image_files[0])
                    
                    # رفع الفيديو
                    print("   🎬 رفع الفيديو...")
                    uploaded_video = await self.client.upload_file(video_files[0])
                    
                    # إرسال معًا
                    await self.client.send_file(
                        entity,
                        [uploaded_photo, uploaded_video],
                        caption=caption
                    )
                    print("✅ تم رفع البوست بنجاح")
                    return True
                else:
                    print("❌ لا توجد صور أو فيديوهات كافية للفيلم")
                    return False
            
            elif post_type == 'series':
                caption = f"📺 **{title}**\n\n" if title else "📺 **مسلسل جديد**\n\n"
                
                if links:
                    caption += "**روابط الحلقات:**\n"
                    for i, link in enumerate(links[:10], 1):
                        caption += f"الحلقة {i}: {link}\n"
                
                # رفع الملفات
                uploaded_files = []
                for file_path in file_paths:
                    print(f"   📤 رفع: {os.path.basename(file_path)}")
                    uploaded_file = await self.client.upload_file(file_path)
                    uploaded_files.append(uploaded_file)
                
                await self.client.send_file(entity, uploaded_files, caption=caption)
                print("✅ تم رفع الملفات بنجاح")
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
            connection_success = await self.init_client()
            if not connection_success:
                return False
            
            # تحميل الفيديو
            video_filename = "video.mp4"
            print(f"📥 تحميل الفيديو...")
            download_success = await self.download_file(download_url, video_filename)
            if not download_success:
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
            
            # إضافة اللوجو إلى الفيديو
            output_filename = "final_video.mp4"
            if logo_filename and os.path.exists(logo_filename):
                logo_success = self.add_logo_to_video(final_video_path, logo_filename, output_filename)
                if logo_success:
                    final_video_path = output_filename
            
            # رفع المحتوى إلى التليجرام
            files_to_upload = []
            
            if content_type == 'movie':
                if logo_filename and os.path.exists(logo_filename):
                    files_to_upload.append(logo_filename)
                files_to_upload.append(final_video_path)
            else:
                files_to_upload.append(final_video_path)
            
            print(f"📤 الرفع إلى تليجرام...")
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
        cleaned = 0
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned += 1
            except:
                pass
        print(f"✅ تم تنظيف {cleaned} ملف")

# دالة رئيسية
async def main():
    print("=" * 50)
    print("🚀 TELEGRAM UPLOADER")
    print("=" * 50)
    
    uploader = TelegramUploader()
    
    # قراءة البيانات
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
        new_name=new_name,
        series_links=series_links
    )
    
    print("=" * 50)
    if success:
        print("✅ تم الرفع بنجاح!")
        sys.exit(0)
    else:
        print("❌ فشل الرفع!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
