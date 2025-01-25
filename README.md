# shtcrop

shtcrop is a Telegram bot that detects and crops black, white, or blurry borders in videos, then re-uploads the edited video.

# Turkish Translation
[README-TR](README-TR.md)

## Features
- **Border Detection**: Identifies black, white, or blurry borders.
- **Video Cropping**: Removes unwanted borders from videos.
- **Telegram Integration**: Processes and re-uploads videos directly in Telegram.
- **Multi-Mode**: Supports black, white, and blurry(experimental) border detection.

## Usage

1. **Create venv & install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**:
   Edit `.env` file:
   ```
   mv env.example .env
   ```

3. **Run the Bot**:
   ```bash
   python cropper.py
   ```

## Usage

Send a video to the bot in Telegram. It will automatically process and re-upload the cropped version.

## License
This project is licensed under the [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html).
