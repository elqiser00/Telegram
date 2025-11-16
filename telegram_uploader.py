#!/usr/bin/env python3
import os
import sys
import asyncio
import aiohttp
import requests
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import DocumentAttributeVideo
import subprocess
import time
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor
import math

print("🚀 SUPER FAST UPLOADER STARTED!")
print("=" * 60)

class TurboUploader:
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.session_string = os.getenv('TELEGRAM_SESSION_STRING')
        self.client = None
        self.download_speed = 0
        self.upload_speed = 0
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # إعدادات السرعة
        self.chunk_size = 64 * 1024  # 64KB chunks للتحميل
        self.upload_chunk_size = 512 * 1024  # 512KB chunks للرفع
        
        print("⚡ Turbo Uploader Initialized")
        print(f"   🔧 Chunk Size: {self.chunk_size // 1024}KB")
        print(f"   🔧 Upload Chunk: {self.upload_chunk_size // 1024}KB")
        
    async def init_client(self):
        """تهيئة العميل التليجرام بتحسينات السرعة"""
        try:
            print("🔌 Connecting to Telegram (Turbo Mode)...")
            
            if not all([self.api_id, self.api_hash, self.session_string]):
                print("❌ Missing Telegram credentials")
                return False
                
            # إعدادات متقدمة للسرعة
            self.client = TelegramClient(
                StringSession(self.session_string), 
                int(self.api_id), 
                self.api_hash,
                connection_retries=3,
                retry_delay=1,
                timeout=60,
                flood_sleep_threshold=120
            )
            
            await self.client.start()
            
            # اختبار السرعة
            me = await self.client.get_me()
            print(f"✅ Connected as: {me.first_name}")
            print("⚡ Connection optimized for speed")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
        
    async def turbo_download(self, url, filename):
        """تحميل سريع مع تعدد المسارات"""
        try:
            print(f"📥 TURBO Download: {filename}")
            start_time = time.time()
            
            # إعدادات متقدمة للتحميل
            connector = aiohttp.TCPConnector(
                limit=20,  # زيادة عدد الاتصالات المتوازية
                limit_per_host=5,
                verify_ssl=False
            )
            
            timeout = aiohttp.ClientTimeout(total=600)  # 10 دقائق
            
            async with aiohttp.ClientSession(
                timeout=timeout, 
                connector=connector,
                headers={'User-Agent': 'Mozilla/5.0 Turbo Downloader'}
            ) as session:
                
                async with session.get(url) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded_size = 0
                        
                        with open(filename, 'wb') as f:
                            last_update = time.time()
                            speed_samples = []
                            
                            async for chunk in response.content.iter_chunked(self.chunk_size):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                                    
                                    # حساب السرعة
                                    current_time = time.time()
                                    time_diff = current_time - last_update
                                    
                                    if time_diff >= 2:  # تحديث كل ثانيتين
                                        speed = downloaded_size / (current_time - start_time)
                                        speed_samples.append(speed)
                                        
                                        if len(speed_samples) > 5:
                                            speed_samples.pop(0)
                                        
                                        avg_speed = sum(speed_samples) / len(speed_samples)
                                        self.download_speed = avg_speed
                                        
                                        if total_size > 0:
                                            percent = (downloaded_size / total_size) * 100
                                            eta = (total_size - downloaded_size) / avg_speed if avg_speed > 0 else 0
                                            
                                            print(f"   🚀 {percent:.1f}% | "
                                                  f"Speed: {self.format_speed(avg_speed)} | "
                                                  f"ETA: {self.format_time(eta)}")
                                        else:
                                            print(f"   🚀 {self.format_size(downloaded_size)} | "
                                                  f"Speed: {self.format_speed(avg_speed)}")
                                        
                                        last_update = current_time
                        
                        download_time = time.time() - start_time
                        avg_speed = downloaded_size / download_time
                        
                        print(f"✅ Download completed: {self.format_size(downloaded_size)}")
                        print(f"   ⏱️ Time: {self.format_time(download_time)}")
                        print(f"   ⚡ Average Speed: {self.format_speed(avg_speed)}")
                        
                        return True
                    else:
                        print(f"❌ Download failed: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Download error: {e}")
            return False
    
    async def turbo_upload(self, file_paths, channel_input, post_type, title=None):
        """رفع سريع مع تحسينات"""
        try:
            print(f"📤 TURBO Upload to: {channel_input}")
            start_time = time.time()
            
            entity = await self.find_channel_entity(channel_input)
            if not entity:
                return False
            
            print(f"   ✅ Target: {getattr(entity, 'title', 'Unknown')}")
            
            if post_type == 'movie':
                image_files = [f for f in file_paths if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                video_files = [f for f in file_paths if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
                
                if image_files and video_files:
                    caption = f"🎬 **{title}**\n\n⚡ Powered by Turbo Uploader" if title else "🎬 **فيلم جديد**\n\n⚡ Powered by Turbo Uploader"
                    
                    # رفع متوازي للصورة والفيديو
                    upload_tasks = []
                    
                    print("   🖼️ Turbo uploading image...")
                    upload_tasks.append(self.upload_with_progress(image_files[0], "Image"))
                    
                    print("   🎬 Turbo uploading video...")
                    upload_tasks.append(self.upload_with_progress(video_files[0], "Video"))
                    
                    # انتظار اكتمال الرفع
                    uploaded_files = await asyncio.gather(*upload_tasks)
                    
                    # إرسال البوست
                    await self.client.send_file(entity, uploaded_files, caption=caption)
                    
                    upload_time = time.time() - start_time
                    total_size = sum(os.path.getsize(f) for f in file_paths)
                    avg_speed = total_size / upload_time
                    
                    print(f"✅ Upload completed!")
                    print(f"   ⏱️ Time: {self.format_time(upload_time)}")
                    print(f"   ⚡ Average Speed: {self.format_speed(avg_speed)}")
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    async def upload_with_progress(self, file_path, file_type):
        """رفع ملف مع عرض التقدم"""
        try:
            file_size = os.path.getsize(file_path)
            start_time = time.time()
            uploaded_size = 0
            
            print(f"      📤 {file_type}: {self.format_size(file_size)}")
            
            # رفع الملف مع متابعة التقدم
            file = await self.client.upload_file(
                file_path,
                part_size_kb=self.upload_chunk_size // 1024,
                progress_callback=lambda sent, total: self.upload_progress(
                    file_type, sent, total, start_time
                ) if sent > 0 else None
            )
            
            return file
            
        except Exception as e:
            print(f"      ❌ {file_type} upload failed: {e}")
            raise
    
    def upload_progress(self, file_type, sent, total, start_time):
        """عرض تقدم الرفع"""
        if total > 0:
            percent = (sent / total) * 100
            elapsed = time.time() - start_time
            speed = sent / elapsed if elapsed > 0 else 0
            eta = (total - sent) / speed if speed > 0 else 0
            
            print(f"      🚀 {file_type}: {percent:.1f}% | "
                  f"Speed: {self.format_speed(speed)} | "
                  f"ETA: {self.format_time(eta)}")
    
    async def smart_logo_processing(self, video_path, logo_path, output_path):
        """معالجة ذكية للوجو"""
        try:
            print("🎨 Smart logo processing...")
            
            if not all(map(os.path.exists, [video_path, logo_path])):
                print("❌ Files missing for logo processing")
                return False
            
            # تحديد حجم الفيديو تلقائياً
            cmd_info = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                       '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video_path]
            result = subprocess.run(cmd_info, capture_output=True, text=True)
            
            if result.returncode == 0:
                dimensions = result.stdout.strip().split(',')
                if len(dimensions) == 2:
                    video_width = int(dimensions[0])
                    logo_size = max(100, video_width // 15)  # حجم ذكي للوجو
                    
                    cmd = [
                        'ffmpeg', '-i', video_path, '-i', logo_path,
                        '-filter_complex', f'[1]scale={logo_size}:{logo_size}[logo];[0][logo]overlay=10:10',
                        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                        '-c:a', 'copy', output_path, '-y'
                    ]
                    
                    # تشغيل في thread منفصل
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.executor, 
                        lambda: subprocess.run(cmd, capture_output=True, text=True)
                    )
                    
                    if result.returncode == 0:
                        print("✅ Smart logo processing completed")
                        return True
                    else:
                        print("❌ Logo processing failed")
                        return False
            
            return False
            
        except Exception as e:
            print(f"❌ Logo processing error: {e}")
            return False
    
    async def find_channel_entity(self, channel_input):
        """بحث ذكي عن القناة"""
        try:
            print(f"   🔍 Smart channel search: {channel_input}")
            
            channel_input = channel_input.strip()
            
            # محاولات متعددة للعثور على القناة
            search_methods = [
                self._search_by_invite_link,
                self._search_by_id,
                self._search_in_dialogs
            ]
            
            for method in search_methods:
                entity = await method(channel_input)
                if entity:
                    return entity
            
            print(f"   ❌ Channel not found")
            return None
            
        except Exception as e:
            print(f"❌ Channel search error: {e}")
            return None
    
    async def _search_by_invite_link(self, channel_input):
        """البحث برابط الدعوة"""
        if '+_' in channel_input or 't.me/+' in channel_input:
            try:
                invite_hash = channel_input.split('t.me/+')[-1] if 't.me/+' in channel_input else channel_input
                invite_hash = invite_hash.replace('+', '').strip()
                
                print(f"   🔑 Trying invite link: {invite_hash}")
                result = await self.client.import_chat_invite(invite_hash)
                
                if result and hasattr(result, 'chats') and result.chats:
                    entity = await self.client.get_entity(result.chats[0].id)
                    print(f"   ✅ Found via invite: {getattr(entity, 'title', 'Unknown')}")
                    return entity
            except Exception as e:
                print(f"   ⚠️ Invite failed: {e}")
        return None
    
    async def _search_by_id(self, channel_input):
        """البحث برقم القناة"""
        numbers = re.findall(r'-?\d+', channel_input)
        for number in numbers:
            if len(str(abs(int(number)))) > 8:
                try:
                    entity = await self.client.get_entity(int(number))
                    print(f"   ✅ Found by ID: {number}")
                    return entity
                except:
                    continue
        return None
    
    async def _search_in_dialogs(self, channel_input):
        """البحث في المحادثات"""
        try:
            async for dialog in self.client.iter_dialogs(limit=50):
                if hasattr(dialog.entity, 'id'):
                    # بحث بطرق متعددة
                    if (str(dialog.entity.id) in channel_input or
                        (hasattr(dialog.entity, 'username') and dialog.entity.username and 
                         dialog.entity.username in channel_input)):
                        print(f"   ✅ Found in dialogs: {dialog.name}")
                        return dialog.entity
        except:
            pass
        return None
    
    async def process_content(self, download_url, logo_url, channel_username, content_type, rename_option=False, new_name=None):
        """معالجة محسنة للمحتوى"""
        try:
            print("🔄 Starting turbo processing...")
            
            # الاتصال أولاً
            if not await self.init_client():
                return False
            
            # إنشاء أسماء ملفات فريدة
            file_hash = hashlib.md5(f"{download_url}{time.time()}".encode()).hexdigest()[:8]
            video_filename = f"video_{file_hash}.mp4"
            logo_filename = f"logo_{file_hash}.png"
            output_filename = f"final_{file_hash}.mp4"
            
            # تحميل متوازي للفيديو واللوجو
            print("📥 Parallel downloading...")
            download_tasks = [
                self.turbo_download(download_url, video_filename),
                self.turbo_download(logo_url, logo_filename)
            ]
            
            download_results = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            if not all(download_results):
                print("❌ Download failed")
                return False
            
            # معالجة الملفات
            final_video_path = video_filename
            
            if rename_option and new_name:
                final_video_path = self.rename_file(video_filename, new_name)
            
            # معالجة اللوجو
            if await self.smart_logo_processing(final_video_path, logo_filename, output_filename):
                final_video_path = output_filename
            
            # الرفع النهائي
            files_to_upload = [logo_filename, final_video_path] if content_type == 'movie' else [final_video_path]
            
            upload_success = await self.turbo_upload(
                files_to_upload, channel_username, content_type, new_name
            )
            
            # تنظيف الملفات
            self.cleanup_files([video_filename, logo_filename, output_filename])
            
            return upload_success
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
            return False
    
    def rename_file(self, file_path, new_name):
        """إعادة تسمية الملف"""
        try:
            if os.path.exists(file_path):
                directory = os.path.dirname(file_path)
                extension = os.path.splitext(file_path)[1]
                new_path = os.path.join(directory, f"{new_name}{extension}")
                os.rename(file_path, new_path)
                print(f"✏️ Renamed to: {new_name}{extension}")
                return new_path
        except Exception as e:
            print(f"⚠️ Rename error: {e}")
        return file_path
    
    def cleanup_files(self, files):
        """تنظيف الملفات"""
        cleaned = 0
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned += 1
            except:
                pass
        print(f"🧹 Cleaned {cleaned} temporary files")
    
    def format_size(self, size_bytes):
        """تنسيق حجم الملف"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def format_speed(self, speed_bytes):
        """تنسيق السرعة"""
        return self.format_size(speed_bytes) + "/s"
    
    def format_time(self, seconds):
        """تنسيق الوقت"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"

async def main():
    print("🎯 TURBO MAIN STARTED")
    print("=" * 60)
    
    uploader = TurboUploader()
    
    # قراءة البيانات
    download_url = os.getenv('INPUT_DOWNLOAD_URL')
    logo_url = os.getenv('INPUT_LOGO_URL')
    channel_username = os.getenv('INPUT_CHANNEL_USERNAME')
    content_type = os.getenv('INPUT_CONTENT_TYPE', 'movie')
    rename_option = os.getenv('INPUT_RENAME_FILE', 'false').lower() == 'true'
    new_name = os.getenv('INPUT_NEW_NAME', '')
    
    print("📋 Turbo Inputs:")
    print(f"   📥 Video: {download_url}")
    print(f"   🖼️ Logo: {logo_url}")
    print(f"   📢 Channel: {channel_username}")
    print(f"   🎬 Type: {content_type}")
    print(f"   ✏️ Rename: {rename_option}")
    if new_name:
        print(f"   📝 New Name: {new_name}")
    print("=" * 60)
    
    success = await uploader.process_content(
        download_url=download_url,
        logo_url=logo_url,
        channel_username=channel_username,
        content_type=content_type,
        rename_option=rename_option,
        new_name=new_name
    )
    
    print("=" * 60)
    if success:
        print("🎉 TURBO UPLOAD COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print("💥 TURBO UPLOAD FAILED!")
        return 1

if __name__ == "__main__":
    print("⭐ TURBO SCRIPT STARTING")
    try:
        exit_code = asyncio.run(main())
        print(f"⭐ TURBO SCRIPT COMPLETED: {'SUCCESS' if exit_code == 0 else 'FAILED'}")
        sys.exit(exit_code)
    except Exception as e:
        print(f"💥 TURBO SCRIPT CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
