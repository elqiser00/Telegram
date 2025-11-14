#!/usr/bin/env python3
import os
import sys
import time

print("🚀 SIMPLE TEST STARTED!")
print("=" * 50)

# Check basic environment
print("✅ Python is working")
print(f"✅ Python version: {sys.version}")

# Check if we're in GitHub Actions
print(f"✅ GitHub Actions: {os.getenv('GITHUB_ACTIONS', 'NO')}")

# Check critical environment variables
print("🔍 Checking environment variables:")
env_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_SESSION_STRING']
for var in env_vars:
    value = os.getenv(var)
    print(f"   {var}: {'SET' if value else 'NOT SET'}")

print("📋 Checking input variables:")
input_vars = ['INPUT_DOWNLOAD_URL', 'INPUT_LOGO_URL', 'INPUT_CHANNEL_USERNAME']
for var in input_vars:
    value = os.getenv(var)
    print(f"   {var}: {value if value else 'NOT SET'}")

print("⏳ Simulating work for 30 seconds...")
for i in range(6):
    print(f"   🔄 Working... {i+1}/6")
    time.sleep(5)

print("=" * 50)
print("✅ SIMPLE TEST COMPLETED SUCCESSFULLY!")
sys.exit(0)
