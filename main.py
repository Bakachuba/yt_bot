import logging
from aiogram import Bot, Dispatcher, executor, types
import yt_dlp
import aiofiles
import asyncio

logging.basicConfig(level=logging.INFO)

bot = Bot(token="6530530732:AAElGEjLjRlZyx3H7Cz1Qo3cd9nst816MSI")
dp = Dispatcher(bot)

class FilenameCollectorPP(yt_dlp.postprocessor.common.PostProcessor):
    def __init__(self):
        super().__init__(None)
        self.filenames = []

    def run(self, information):
        self.filenames.append(information["filepath"])
        return [], information

async def send_document(message, file_path, arguments):
    async with aiofiles.open(file_path, 'rb') as f:
        await message.reply_document(f)
    await message.reply(f'Файл был отправлен!\nСпасибо за использование бота\n\n__{arguments}__')
    await asyncio.create_task(aiofiles.os.remove(file_path))

async def process_search(message, arg):
    await message.reply('Ожидайте...')
    YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'noplaylist': 'True',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
    }
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        filename_collector = FilenameCollectorPP()
        ydl.add_post_processor(filename_collector)
        video = ydl.extract_info(f"ytsearch:{arg}", download=True)['entries'][0]
        await send_document(message, filename_collector.filenames[0], arg)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, который поможет тебе скачать аудио с YouTube.")

@dp.message_handler(commands=['sea'])
async def search(message: types.Message):
    arg = message.get_args()
    await process_search(message, arg)

@dp.message_handler(commands=['yt'])
async def youtube(message: types.Message):
    arguments = message.get_args()
    await process_search(message, arguments)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
