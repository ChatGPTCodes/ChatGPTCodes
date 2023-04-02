import os
import re
import aiofiles
import httpx
from instaloader import Instaloader, Post
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor

# Set your bot token here
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Instaloader instance
loader = Instaloader(download_videos=True, download_geotags=False, download_comments=False, compress_json=False)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

async def download_instagram_video(url):
    match = re.search(r"(?:https?:\/\/)?(?:www\.)?(?:instagram\.com|instagr\.am)\/(?:p|reel)\/([^\/?]+)", url)
    if not match:
        raise ValueError("Invalid Instagram URL")

    shortcode = match.group(1)
    post = Post.from_shortcode(loader.context, shortcode)
    loader.download_post(post, target=f'{shortcode}_video')
    
    # Find the video file
    video_file = None
    for file in os.listdir(f"{shortcode}_video"):
        if file.endswith(".mp4"):
            video_file = os.path.join(f"{shortcode}_video", file)
            break

    if not video_file:
        raise FileNotFoundError("Video file not found")

    return video_file


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Send me an Instagram video URL and I'll download it for you.")

@dp.message_handler(regexp="(?:instagram.com|instagr.am)")
async def handle_url(message: types.Message):
    url = message.text
    try:
        await message.reply("Downloading the video, please wait...")
        video_file = await download_instagram_video(url)
        async with aiofiles.open(video_file, 'rb') as f:
            await bot.send_video(chat_id=message.chat.id, video=f)
        os.remove(video_file)
    except Exception as e:
        print(e)
        await message.reply("An error occurred while downloading the video. Please make sure the URL is correct.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
