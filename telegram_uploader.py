#!/usr/bin/env python3
import os
import sys
import asyncio
import aiohttp
import requests
from telethon import TelegramClient
from telethon.sessions import StringSession
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
        self.chunk_size = 64 * 1024
        self.upload_chunk_size = 512 * 1024
        
        print("⚡ Turbo Uploader Initialized")
        
    async def init_client(self):
        """تهيئة العميل التليجرام"""
        try:
            print("🔌 Connecting to Telegram...")
            
            if not all([self.api_id, self.api_hash, self.session_string]):
                print("❌ Missing Telegram credentials")
                return False
                
            self.client = TelegramClient(
                StringSession(self.session_string), 
                int(self.api_id), 
                self.api_hash
            )
            
            await self.client.start()
            me = await self.client.get_me()
            print(f"✅ Connected as: {me.first_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
        
    async def turbo_download(self, url, filename):
        """تحميل سريع"""
        try:
            print(f"📥 Downloading: {filename}")
            start_time = time.time()
            
            # إصلاح التحذير: استخدام ssl=False بدل verify_ssl
            connector = aiohttp.TCPConnector(limit=20, ssl=False)
            timeout = aiohttp.ClientTimeout(total=600)
            
            async with aiohttp.ClientSession(
                timeout=timeout, 
                connector=connector,
                headers={'User-Agent': 'Mozilla/5.0'}
            ) as session:
                
                async with session.get(url) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded_size = 0
                        
                        with open(filename, 'wb') as f:
                            async for chunk in response.content.iter_chunked(self.chunk_size):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                                    
                                    # عرض التقدم
                                    if total_size > 0:
                                        percent = (downloaded_size / total_size) * 100
                                        if int(percent) % 10 == 0:  # عرض كل 10%
                                            print(f"   📥 Progress: {percent:.1f}%")
                        
                        download_time = time.time() - start_time
                        print(f"✅ Download completed: {self.format_size(downloaded_size)}")
                        print(f"   ⏱️ Time: {self.format_time(download_time)}")
                        
                        return True
                    else:
                        print(f"❌ Download failed: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Download error: {e}")
            return False
    
    async def turbo_upload(self, file_paths, channel_input, post_type, title=None):
        """رفع سريع"""
        try:
            print(f"📤 Uploading to: {channel_input}")
            
            entity = await self.find_channel_entity(channel_input)
            if not entity:
                return False
            
            print(f"   ✅ Target: {getattr(entity, 'title', 'Unknown')}")
            
            if post_type == 'movie':
                image_files = [f for f in file_paths if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                video_files = [f for f in file_paths if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
                
                if image_files and video_files:
                    caption = f"🎬 **{title}**\n\n" if title else "🎬 **فيلم جديد**\n\n"
                    
                    print("   🖼️ Uploading image...")
                    uploaded_photo = await self.client.upload_file(image_files[0])
                    
                    print("   🎬 Uploading video...")
                    uploaded_video = await self.client.upload_file(video_files[0])
                    
                    await self.client.send_file(entity, [uploaded_photo, uploaded_video], caption=caption)
                    print("✅ Upload completed!")
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    async def smart_logo_processing(self, video_path, logo_path, output_path):
        """معالجة اللوجو"""
        try:
            print("🎨 Processing logo...")
            
            if not all(map(os.path.exists, [video_path, logo_path])):
                return False
            
            cmd = [
                'ffmpeg', '-i', video_path, '-i', logo_path,
                '-filter_complex', '[1]scale=150:150[logo];[0][logo]overlay=10:10',
                '-c:a', 'copy', output_path, '-y'
            ]
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                lambda: subprocess.run(cmd, capture_output=True, text=True)
            )
            
            if result.returncode == 0:
                print("✅ Logo processing completed")
                return True
            else:
                print("❌ Logo processing failed")
                return False
            
        except Exception as e:
            print(f"❌ Logo processing error: {e}")
            return False
    
    async def find_channel_entity(self, channel_input):
        """بحث عن القناة"""
        try:
            print(f"   🔍 Searching for channel...")
            
            channel_input = channel_input.strip()
            
            # البحث برقم القناة
            numbers = re.findall(r'-?\d+', channel_input)
            for number in numbers:
                if len(str(abs(int(number)))) > 8:
                    try:
                        entity = await self.client.get_entity(int(number))
                        print(f"   ✅ Found by ID: {number}")
                        return entity
                    except:
                        continue
            
            # البحث في المحادثات
            async for dialog in self.client.iter_dialogs(limit=20):
                if hasattr(dialog.entity, 'id'):
                    if str(dialog.entity.id) in channel_input:
                        print(f"   ✅ Found in dialogs: {dialog.name}")
                        return dialog.entity
            
            print(f"   ❌ Channel not found")
            return None
            
        except Exception as e:
            print(f"❌ Channel search error: {e}")
            return None
    
    async def process_content(self, download_url, logo_url, channel_username, content_type, rename_option=False, new_name=None):
        """معالجة المحتوى"""
        try:
            print("🔄 Starting processing...")
            
            # الاتصال أولاً
            if not await self.init_client():
                return False
            
            # تحميل الفيديو
            video_filename = "video.mp4"
            print(f"📥 Downloading video...")
            if not await self.turbo_download(download_url, video_filename):
                return False
            
            # تحميل اللوجو
            logo_filename = "logo.png"
            print(f"📥 Downloading logo...")
            if not await self.turbo_download(logo_url, logo_filename):
                logo_filename = None
            
            # إعادة تسمية
            final_video_path = video_filename
            if rename_option and new_name:
                final_video_path = self.rename_file(video_filename, new_name)
            
            # إضافة اللوجو
            output_filename = "final_video.mp4"
            if logo_filename:
                if await self.smart_logo_processing(final_video_path, logo_filename, output_filename):
                    final_video_path = output_filename
            
            # الرفع
            files_to_upload = [logo_filename, final_video_path] if content_type == 'movie' and logo_filename else [final_video_path]
            
            upload_success = await self.turbo_upload(
                files_to_upload, channel_username, content_type, new_name
            )
            
            # تنظيف
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
        except:
            pass
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
        print(f"🧹 Cleaned {cleaned} files")
    
    def format_size(self, size_bytes):
        """تنسيق حجم الملف"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def format_time(self, seconds):
        """تنسيق الوقت"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"

async def main():
    print("🎯 MAIN STARTED")
    print("=" * 60)
    
    uploader = TurboUploader()
    
    # قراءة البيانات
    download_url = os.getenv('INPUT_DOWNLOAD_URL')
    logo_url = os.getenv('INPUT_LOGO_URL')
    channel_username = os.getenv('INPUT_CHANNEL_USERNAME')
    content_type = os.getenv('INPUT_CONTENT_TYPE', 'movie')
    rename_option = os.getenv('INPUT_RENAME_FILE', 'false').lower() == 'true'
    new_name = os.getenv('INPUT_NEW_NAME', '')
    
    print("📋 Inputs:")
    print(f"   📥 Video: {download_url}")
    print(f"   🖼️ Logo: {logo_url}")
    print(f"   📢 Channel: {channel_username}")
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
        print("✅ UPLOAD COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print("❌ UPLOAD FAILED!")
        return 1

if __name__ == "__main__":
    print("⭐ SCRIPT STARTING")
    try:
        exit_code = asyncio.run(main())
        print(f"⭐ SCRIPT COMPLETED")
        sys.exit(exit_code)
    except Exception as e:
        print(f"💥 SCRIPT CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
