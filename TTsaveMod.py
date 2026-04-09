# meta developer: @trololo_1

from .. import utils, loader
import re, asyncio, os
from datetime import datetime

default_chat = "@SaveAsBot"
MODE_FORWARD = "forward"
MODE_DOWNLOAD = "download"

class TTsaveMod(loader.Module):
    """Save tiktok video"""
    strings = {'name': 'TTsaveMod'}
    async def client_ready(self, client, db):
        self.db = db
        self.default_chat = default_chat
        if not self.db.get('TTsaveMod', 'chat', False):
            self.db.set('TTsaveMod', 'chat', self.default_chat)

    def _send_mode(self):
        m = self.db.get('TTsaveMod', 'send_mode', MODE_FORWARD)
        return m if m in (MODE_FORWARD, MODE_DOWNLOAD) else MODE_FORWARD

    async def save_video(self, message, url=None):
        """save video from tiktok. url: ссылка; для .ttsave можно не передавать (берётся из аргументов команды)."""
        if url is not None:
            args = str(url).strip()
        else:
            args = utils.get_args_raw(message).strip()
        if not args:
            await utils.answer(message, "Нет ссылки.")
            return False
        dest = message.peer_id
        chat = self.db.get('TTsaveMod', 'chat')
        mode = self._send_mode()
        status_msg = await message.respond('Скачиваю...')

        async def erase_status():
            try:
                await status_msg.delete()
            except Exception:
                pass

        try:
            async with message.client.conversation(chat) as conv:
                bot_send_link = await conv.send_message(args)
                response1 = await conv.get_response()
                response2 = await conv.get_response()

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
                    await erase_status()
                    await message.respond("Не удалось получить видео.")
                    await response1.delete()
                    await response2.delete()
                    await bot_send_link.delete()
                    return False

                if mode == MODE_FORWARD:
                    await video_response.forward_to(dest)
                    await response1.delete()
                    await response2.delete()
                    await bot_send_link.delete()
                    await erase_status()
                    return True

                now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                filename = f"{now_time}.mp4"
                await video_response.download_media(filename)
                await response1.delete()
                await response2.delete()
                await bot_send_link.delete()
                await erase_status()
                await message.client.send_file(dest, filename)
                os.remove(filename)
                return True
        except Exception:
            await erase_status()
            raise

    async def setbotcmd(self, message):
        """use: .setbot чтобы установить бота для скачивания."""
        args = utils.get_args_raw(message)

        try:
            bot = await message.client.get_entity(args)
        except:
            return await utils.answer(message, f"<b>бот не найден.</b>")
        self.db.set('TTsaveMod', 'bot', str(bot.id))
        await utils.answer(message, f"<b>бот <code>{bot.username}</code> установлен.</b>")

    async def ttsendmodecmd(self, message):
        """.ttsendmode forward|download — пересылка с бота (по умолчанию) или скачивание и отправка. Без аргументов — текущий режим."""
        raw = (utils.get_args_raw(message) or "").strip().lower()
        if not raw:
            cur = self._send_mode()
            tip = "пересылка с бота" if cur == MODE_FORWARD else "скачивание и отправка"
            return await utils.answer(
                message,
                f"<b>Сейчас:</b> {tip}\n<code>.ttsendmode forward|download</code>",
            )
        if raw in ("forward", "пересылка", "fwd", "f"):
            self.db.set("TTsaveMod", "send_mode", MODE_FORWARD)
            return await utils.answer(message, "<b>Режим:</b> пересылка с бота.")
        if raw in ("download", "скачивание", "скачать", "dl", "d"):
            self.db.set("TTsaveMod", "send_mode", MODE_DOWNLOAD)
            return await utils.answer(message, "<b>Режим:</b> скачивание и отправка.")
        return await utils.answer(message, "<code>.ttsendmode forward|download</code>")

    async def ttsavecmd(self, message):
        """.ttsave {link}"""

        args = utils.get_args_raw(message)
        save_video = await self.save_video(message)
        if save_video:
            if self._send_mode() == MODE_FORWARD:
                await utils.answer(message, "<b>видео переслано.</b>")
            else:
                await utils.answer(message, "<b>видео успешно отправлено.</b>")
        else:
            await utils.answer(message, "<b>не удалось скачать видео.</b>")

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
                await self.save_video(message, url=link)
                await asyncio.sleep(5)
        except Exception:
            pass
