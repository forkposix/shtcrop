import os
import asyncio
import cv2
import numpy as np
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import hashlib
import datetime

load_dotenv()

TOKEN = os.getenv('TOKEN')
ALLOWED_CHAT_IDS = os.getenv('ALLOWED_CHAT_IDS')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB'))

ALLOWED_CHAT_IDS = list(map(int, ALLOWED_CHAT_IDS.split(',')))

app = Client(
    "video_bot",
    bot_token=TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

def detect_black_borders(cap):
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    skip_interval = 5
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    min_x, min_y, max_x, max_y = width, height, 0, 0

    for i in range(0, frame_count, skip_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break

        inverted_frame = invert_colors(frame)
        gray = cv2.cvtColor(inverted_frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)

    if min_x >= max_x or min_y >= max_y or (min_x == width and min_y == height):
        return 0, 0, width, height

    return min_x, min_y, max_x, max_y

def invert_colors(image):
    b, g, r = cv2.split(image)
    inverted_b = 255 - b
    inverted_g = 255 - g
    inverted_r = 255 - r
    inverted_image = cv2.merge((inverted_b, inverted_g, inverted_r))
    return inverted_image


def detect_white_borders(cap):
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    skip_interval = 5
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    min_x, min_y, max_x, max_y = width, height, 0, 0

    for i in range(0, frame_count, skip_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)

    if min_x >= max_x or min_y >= max_y or (min_x == width and min_y == height):
        return 0, 0, width, height

    return min_x, min_y, max_x, max_y

def detect_blurry_regions(cap):
    blurry_frames = []
    threshold = 100

    for i in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        if laplacian_var < threshold:
            blurry_frames.append((i, laplacian_var))

    return blurry_frames

def detect_blurry_borders(cap):
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    skip_interval = 5
    blurry_frames = []
    blur_threshold = 100

    # Analyze frames at intervals
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in range(0, frame_count, skip_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance < blur_threshold:
            blurry_frames.append(i)

    if not blurry_frames:
        return 0, 0, frame_width, frame_height

    min_x, min_y, max_x, max_y = frame_width, frame_height, 0, 0

    # Collect bounding boxes around blurry areas
    for frame_index in blurry_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Morphological operations to reduce noise
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)

    return min_x, min_y, max_x, max_y

async def crop_video(video_path, crop_params):
    crop_width = crop_params[2] - crop_params[0]
    crop_height = crop_params[3] - crop_params[1]
    out_path = get_output_filename(video_path)
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-vf', f'crop={crop_width}:{crop_height}:{crop_params[0]}:{crop_params[1]}',
        '-c:v', 'libx264', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        out_path
    ]
    process = await asyncio.create_subprocess_exec(
        *ffmpeg_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(f"ffmpeg hata kodu: {process.returncode}\nstdout: {stdout.decode()}\nstderr: {stderr.decode()}")
    return out_path

def get_output_filename(video_path):
    # MD5 hash hesapla
    with open(video_path, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    md5sum = file_hash.hexdigest()

    date_str = datetime.datetime.now().strftime("%Y%m%d")

    return f"fixed_{date_str}_{md5sum}.mp4"

async def process_video(video_path, mode):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, 0, 0, 0, 0

    if mode == 'black':
        crop_params = detect_black_borders(cap)
    elif mode == 'white':
        crop_params = detect_white_borders(cap)
    elif mode == 'blurry':
        crop_params = detect_blurry_borders(cap)
    else:
        raise ValueError("Geçersiz mod: sadece 'black', 'white' veya 'blurry' olabilir.")

    cap.release()

    if crop_params[0] >= crop_params[2] or crop_params[1] >= crop_params[3]:
        return None, 0, 0, 0, 0

    fixed_video_path = await crop_video(video_path, crop_params)
    return fixed_video_path, crop_params[0], crop_params[1], crop_params[2], crop_params[3]

@app.on_message(filters.chat(ALLOWED_CHAT_IDS) & filters.video)
async def handle_video(client, message: Message):
    try:
        if message.video.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            await message.reply_text(f"Video dosyası {MAX_FILE_SIZE_MB} MB'den büyük olduğu için işlenemiyor.")
            return

        processing_message = await message.reply_text("Video indiriliyor...", reply_to_message_id=message.id)
        print("Video alındı:", message.video.file_name)
        video_path = await message.download()

        if not video_path or os.path.getsize(video_path) == 0:
            raise Exception("Video dosyası indirilirken hata oluştu veya dosya boyutu 0 B.")

        await processing_message.edit_text(f"Video siyah modda işleniyor", parse_mode=enums.ParseMode.HTML)
        fixed_video_path_black, min_x_black, min_y_black, max_x_black, max_y_black = await process_video(video_path, 'black')
        if min_x_black <= 1 and min_y_black <= 1:
            await processing_message.edit_text(f"Video beyaz modda işleniyor", parse_mode=enums.ParseMode.HTML)
            fixed_video_path_white, min_x_white, min_y_white, max_x_white, max_y_white = await process_video(video_path, 'white')
            if min_x_white <= 1 and min_y_white <= 1:
                await processing_message.edit_text(f"Video bulanık modda işleniyor", parse_mode=enums.ParseMode.HTML)
                fixed_video_path_blur, min_x_blur, min_y_blur, max_x_blur, max_y_blur = await process_video(video_path, 'blurry')
                if min_x_blur <= 1 and min_y_blur <= 1:
                    await processing_message.edit_text("Hiçbir modda border bulunamadı.")
                else:
                    await processing_message.edit_text(f"Video yükleniyor...", parse_mode=enums.ParseMode.HTML)
                    await send_video_with_caption(client, message.chat.id, fixed_video_path_blur, f"Blur Mod: {min_x_blur}:{min_y_blur}:{max_x_blur}:{max_y_blur}", message.id)
                    await processing_message.delete()
                    os.remove(fixed_video_path_blur)
            else:
                await processing_message.edit_text(f"Video yükleniyor...", parse_mode=enums.ParseMode.HTML)
                await send_video_with_caption(client, message.chat.id, fixed_video_path_white, f"Beyaz Mod: {min_x_white}:{min_y_white}:{max_x_white}:{max_y_white}", message.id)
                os.remove(fixed_video_path_white)
                await processing_message.delete()
        else:
            await processing_message.edit_text(f"Video yükleniyor...", parse_mode=enums.ParseMode.HTML)
            await send_video_with_caption(client, message.chat.id, fixed_video_path_black, f"Siyah Mod: {min_x_black}:{min_y_black}:{max_x_black}:{max_y_black}", message.id)
            os.remove(fixed_video_path_black)
            await processing_message.delete()

        os.remove(video_path)

    except Exception as e:
        await processing_message.edit_text(f"Hata oluştu: <pre language='Error'>{e}</pre>", parse_mode=enums.ParseMode.HTML)


async def send_video_with_caption(client, chat_id, video_path, caption, reply_to_message_id):
    message = await client.send_video(
        chat_id=chat_id,
        video=video_path,
        caption=caption,
        reply_to_message_id=reply_to_message_id
    )
    return message

@app.on_message(filters.command("settings") & filters.chat(ALLOWED_CHAT_IDS))
async def show_settings(client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(".mp4 dosyalarını sil", callback_data="clear_mp4")]
        ]
    )
    await message.reply("Settings:", reply_markup=keyboard)

@app.on_callback_query(filters.regex("clear_mp4"))
async def clear_mp4_files(client, callback_query):
    try:
        files_deleted = 0
        for root, dirs, files in os.walk("."):
            for filename in files:
                if filename.endswith(".mp4"):
                    file_path = os.path.join(root, filename)
                    os.remove(file_path)
                    files_deleted += 1
        await callback_query.message.edit_text(f"{files_deleted} adet .mp4 dosyası silindi.")
    except Exception as e:
        await callback_query.message.edit_text(f"Dosya silinirken hata oluştu:\n{e}")

async def start_bot():
    print("Bot çalışıyor...")
    await app.start()

async def stop_bot():
    print("Bot durduruluyor...")
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
