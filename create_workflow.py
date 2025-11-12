import os

# Create directory
os.makedirs('/workspace/.github/workflows', exist_ok=True)

# Write the workflow file
content = """name: Upload Media to Telegram

on:
  workflow_dispatch:
    inputs:
      content_type:
        description: 'نوع المحتوى (movie / series)'
        required: true
        type: choice
        options:
          - movie
          - series
        default: 'movie'
      
      channel:
        description: 'رابط أو ID قناة Telegram (مثال: @channel_name أو -1001234567890)'
        required: true
        type: string
      
      logo_path:
        description: 'مسار اللوجو في المستودع (مثال: logos/movie_logo.jpg)'
        required: true
        type: string
      
      caption:
        description: 'وصف البوست (اختياري)'
        required: false
        type: string
      
      # للأفلام
      video_url:
        description: '[فيلم فقط] رابط تحميل الفيديو'
        required: false
        type: string
      
      custom_name:
        description: '[فيلم فقط] اسم مخصص للفيديو (اختياري - مثال: Movie_2024.mp4)'
        required: false
        type: string
      
      # للمسلسلات (حتى 10 حلقات)
      video_url_1:
        description: '[مسلسل] رابط الحلقة 1'
        required: false
        type: string
      
      video_url_2:
        description: '[مسلسل] رابط الحلقة 2'
        required: false
        type: string
      
      video_url_3:
        description: '[مسلسل] رابط الحلقة 3'
        required: false
        type: string
      
      video_url_4:
        description: '[مسلسل] رابط الحلقة 4'
        required: false
        type: string
      
      video_url_5:
        description: '[مسلسل] رابط الحلقة 5'
        required: false
        type: string
      
      video_url_6:
        description: '[مسلسل] رابط الحلقة 6'
        required: false
        type: string
      
      video_url_7:
        description: '[مسلسل] رابط الحلقة 7'
        required: false
        type: string
      
      video_url_8:
        description: '[مسلسل] رابط الحلقة 8'
        required: false
        type: string
      
      video_url_9:
        description: '[مسلسل] رابط الحلقة 9'
        required: false
        type: string
      
      video_url_10:
        description: '[مسلسل] رابط الحلقة 10'
        required: false
        type: string
      
      # أسماء مخصصة للحلقات (اختياري)
      custom_name_1:
        description: '[مسلسل] اسم مخصص للحلقة 1 (اختياري)'
        required: false
        type: string
      
      custom_name_2:
        description: '[مسلسل] اسم مخصص للحلقة 2 (اختياري)'
        required: false
        type: string
      
      custom_name_3:
        description: '[مسلسل] اسم مخصص للحلقة 3 (اختياري)'
        required: false
        type: string
      
      custom_name_4:
        description: '[مسلسل] اسم مخصص للحلقة 4 (اختياري)'
        required: false
        type: string
      
      custom_name_5:
        description: '[مسلسل] اسم مخصص للحلقة 5 (اختياري)'
        required: false
        type: string
      
      custom_name_6:
        description: '[مسلسل] اسم مخصص للحلقة 6 (اختياري)'
        required: false
        type: string
      
      custom_name_7:
        description: '[مسلسل] اسم مخصص للحلقة 7 (اختياري)'
        required: false
        type: string
      
      custom_name_8:
        description: '[مسلسل] اسم مخصص للحلقة 8 (اختياري)'
        required: false
        type: string
      
      custom_name_9:
        description: '[مسلسل] اسم مخصص للحلقة 9 (اختياري)'
        required: false
        type: string
      
      custom_name_10:
        description: '[مسلسل] اسم مخصص للحلقة 10 (اختياري)'
        required: false
        type: string

jobs:
  upload:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Upload to Telegram
        env:
          SESSION_STRING: ${{ secrets.SESSION_STRING }}
          API_ID: ${{ secrets.API_ID }}
          API_HASH: ${{ secrets.API_HASH }}
          CONTENT_TYPE: ${{ inputs.content_type }}
          CHANNEL: ${{ inputs.channel }}
          LOGO_PATH: ${{ inputs.logo_path }}
          CAPTION: ${{ inputs.caption }}
          VIDEO_URL: ${{ inputs.video_url }}
          CUSTOM_NAME: ${{ inputs.custom_name }}
          VIDEO_URL_1: ${{ inputs.video_url_1 }}
          VIDEO_URL_2: ${{ inputs.video_url_2 }}
          VIDEO_URL_3: ${{ inputs.video_url_3 }}
          VIDEO_URL_4: ${{ inputs.video_url_4 }}
          VIDEO_URL_5: ${{ inputs.video_url_5 }}
          VIDEO_URL_6: ${{ inputs.video_url_6 }}
          VIDEO_URL_7: ${{ inputs.video_url_7 }}
          VIDEO_URL_8: ${{ inputs.video_url_8 }}
          VIDEO_URL_9: ${{ inputs.video_url_9 }}
          VIDEO_URL_10: ${{ inputs.video_url_10 }}
          CUSTOM_NAME_1: ${{ inputs.custom_name_1 }}
          CUSTOM_NAME_2: ${{ inputs.custom_name_2 }}
          CUSTOM_NAME_3: ${{ inputs.custom_name_3 }}
          CUSTOM_NAME_4: ${{ inputs.custom_name_4 }}
          CUSTOM_NAME_5: ${{ inputs.custom_name_5 }}
          CUSTOM_NAME_6: ${{ inputs.custom_name_6 }}
          CUSTOM_NAME_7: ${{ inputs.custom_name_7 }}
          CUSTOM_NAME_8: ${{ inputs.custom_name_8 }}
          CUSTOM_NAME_9: ${{ inputs.custom_name_9 }}
          CUSTOM_NAME_10: ${{ inputs.custom_name_10 }}
        run: |
          python telegram_uploader.py
"""

with open('/workspace/.github/workflows/upload_to_telegram.yml', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ File created successfully!")
print(f"📁 Location: /workspace/.github/workflows/upload_to_telegram.yml")
print(f"📏 Size: {os.path.getsize('/workspace/.github/workflows/upload_to_telegram.yml')} bytes")

# List all files in the directory
print("\n📂 Files in .github/workflows/:")
for file in os.listdir('/workspace/.github/workflows/'):
    print(f"  - {file}")
