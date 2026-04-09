# meta developer: @trololo_1

from telethon import events
from .. import utils, loader
import re, asyncio, os
from datetime import datetime

default_chat = "@SaveAsBot"

class TTsaveMod(loader.Module):
    """Save tiktok video"""
    strings = {'name': 'TTsaveMod'}
    async def client_ready(self, client, db):
        self.db = db
        self.default_chat = default_chat
        if not self.db.get('TTsaveMod', 'chat', False):
            self.db.set('TTsaveMod', 'chat', self.default_chat)

    async def save_video(self, message):
        """save video from tiktok"""
        args = utils.get_args_raw(message)
        chat = self.db.get('TTsaveMod', 'chat')
        ev = events.NewMessage(incoming=True, from_users=chat, chats=chat)
        async with message.client.conversation(chat) as conv:
            await utils.answer(message, 'Скачиваю...')
            t1 = asyncio.create_task(conv.wait_event(ev))
            t2 = asyncio.create_task(conv.wait_event(ev))
            try:
                bot_send_link = await message.client.send_message(chat, args)
                response1, response2 = await asyncio.gather(t1, t2)
            except BaseException:
                for t in (t1, t2):
                    if not t.done():
                        t.cancel()
                await asyncio.gather(t1, t2, return_exceptions=True)
                raise

            # Определяем, в каком из response пришло видео
            video_response, other_response = None, None
            if hasattr(response1, "media") and response1.media is not None:
                if getattr(response1.media, "document", None) or getattr(response1.media, "video", None):
                    video_response = response1
                    other_response = response2
            if video_response is None and hasattr(response2, "media") and response2.media is not None:
                if getattr(response2.media, "document", None) or getattr(response2.media, "video", None):
                    video_response = response2
                    other_response = response1
            if video_response is None:
                await utils.answer(message, "Не удалось получить видео.")
                await response1.delete()
                await response2.delete()
                await bot_send_link.delete()
                await message.delete()
                return False

            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = f"{now_time}.mp4"
            await video_response.download_media(filename)
            await message.client.send_file(message.to_id, filename)
            await response1.delete()
            await response2.delete()
            await bot_send_link.delete()
            await message.delete()
            os.remove(filename)
            return True

    async def setbotcmd(self, message):
        """use: .setbot чтобы установить бота для скачивания."""
        args = utils.get_args_raw(message)

        try:
            bot = await message.client.get_entity(args)
        except:
            return await utils.answer(message, f"<b>бот не найден.</b>")
        self.db.set('TTsaveMod', 'bot', str(bot.id))
        await utils.answer(message, f"<b>бот <code>{bot.username}</code> установлен.</b>")

    async def ttsavecmd(self, message):
        """.ttsave {link}"""

        args = utils.get_args_raw(message)
        save_video = await self.save_video(message)
        if save_video:
            await utils.answer(message, f"<b>видео успешно скачано.</b>")
        else:
            await utils.answer(message, f"<b>не удалось скачать видео.</b>")

    async def ttacceptcmd(self, message):
        """ .ttaccept {reply/id} для открытия в чате автоматического скачивания ссылок. без аргументов тоже работает.\n.ttaccept -l для показа открытых чатов """

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        users_list = self.db.get('TTsaveMod', 'users', [])

        if args == '-l':
            if len(users_list) == 0: return await utils.answer(message, 'Список пуст.')
            return await utils.answer(message, '• '+'\n• '.join(['<code>'+str(i)+'</code>' for i in users_list]))

        try:
            if not args and not reply:
                user = message.chat_id
            else:
                user = reply.sender_id if not args else int(args)
        except:
            return await utils.answer(message, 'Неверно введён ид.')
        if user in users_list:
            users_list.remove(user)
            await utils.answer(message, f'Ид <code>{str(user)}</code> исключен.')
        else:
            users_list.append(user)
            await utils.answer(message, f'Ид <code>{str(user)}</code> добавлен.')
        self.db.set('TTsaveMod', 'users', users_list)

    async def watcher(self, message):
        try:
            users = self.db.get('TTsaveMod', 'users', [])
            if message.chat_id not in users: return
            links = re.findall(r'((?:https?://)?v[mt]\.tiktok\.com/[A-Za-z0-9_]+/?)', message.raw_text)
            if len(links) == 0: return

            for link in links:
                save_video = await self.save_video(message)
                await asyncio.sleep(5)
        except: pass
