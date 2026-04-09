# meta developer: @trololo_1

from telethon import events
from .. import utils, loader
import re, asyncio, os

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
		async with message.client.conversation(self.db.get('TTsaveMod', 'chat')) as conv:
			await utils.answer(message, 'Скачиваю...')
			response1, response2 = [conv.wait_event(events.NewMessage(incoming=True, from_users=self.db.get('TTsaveMod', 'chat'), chats=self.db.get('TTsaveMod', 'chat'))) for i in range(2)]
			bot_send_link = await message.client.send_message(self.db.get('TTsaveMod', 'chat'), args)
			response1 = await response1
			response2 = await response2
			now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			await response2.download_media(f"{now_time}.mp4")
			await message.client.send_file(message.to_id, f"{now_time}.mp4")
			await response1.delete()
			await response2.delete()
			await bot_send_link.delete()
			await message.delete()
			os.remove(f"{now_time}.mp4")

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