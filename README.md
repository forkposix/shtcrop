# shtcrop

shtcrop is a Telegram bot that detects and crops black, white, or blurry borders in videos, then re-uploads the edited video.

## Features
- **Border Detection**: Identifies black, white, or blurry borders.
- **Video Cropping**: Removes unwanted borders from videos.
- **Telegram Integration**: Processes and re-uploads videos directly in Telegram.
- **Multi-Mode**: Supports black, white, and blurry(experimental) border detection.

## Requirements

Install these Python libraries:
```
asyncio
opencv-python-headless
numpy
Pyrogram
python-dotenv
hashlib
datetime
ffmpeg-python
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file and add:
   ```
   TOKEN=<Telegram Bot Token>
   API_ID=<Telegram API ID>
   API_HASH=<Telegram API Hash>
   ALLOWED_CHAT_IDS=<Allowed Chat IDs>
   MAX_FILE_SIZE_MB=<Max File Size in MB>
   ```

3. **Run the Bot**:
   ```bash
   python bot.py
   ```

## Usage

Send a video to the bot in Telegram. It will automatically process and re-upload the cropped version.

## Contributing

Feel free to submit pull requests or issues.
