from telethon import events
from .. import utils, loader
import re, asyncio, os

chat = 1598492699

class TTsaveMod(loader.Module):
	"""Save tiktok video"""
	strings = {'name': 'TTsaveMod'}	
	async def client_ready(self, client, db):
		self.db = db
	
	async def ttsavecmd(self, message):
		""".ttsave {link}"""

		args = utils.get_args_raw(message)
		async with message.client.conversation(chat) as conv:
			await utils.answer(message, 'Скачиваю...')
			response = conv.wait_event(events.NewMessage(incoming=True, from_users=chat, chats=chat))
			bot_send_link = await message.client.send_message(chat, args)
			response = await response
			await response.download_media("hui.mp4")
			await message.client.send_file(message.to_id, "hui.mp4")
			await response.delete()
			await bot_send_link.delete()
			await message.delete()
			os.remove("hui.mp4")

	async def ttacceptcmd(self, message):
		""" .ttaccept {reply/id} для открытия в чате автоматического скачивания ссылок. без аргументов тоже работает.\n.ttaccept -l для показа открытых чатов """

		args = utils.get_args_raw(message)
		reply = await message.get_reply_message()
		users_list = self.db.get('TTsaveMod', 'users', [])

		if args == '-l':
			if len(users_list) == 0: return await utils.answer(message, 'Список пуст.')
			return await utils.answer(message, '• '+'\n• '.join([str(i) for i in users_list]))

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
		await self.db.set('TTsaveMod', 'users', users_list)

	async def watcher(self, message):
		try:
			users = self.db.get('TTsaveMod', 'users', [])
			if message.chat_id not in users: return
			links = re.findall(r'((?:https?://)?vm\.tiktok\.com/[A-Za-z0-9_]+/?)', message.raw_text)
			if len(links) == 0: return

			async with message.client.conversation(chat) as conv:
				for link in links:
					response = conv.wait_event(events.NewMessage(incoming=True, from_users=chat, chats=chat))
					bot_send_link = await message.client.send_message(chat, link)
					response = await response
					await response.download_media("hui.mp4")
					await message.client.send_file(message.chat_id, "hui.mp4")
					await response.delete()
					await bot_send_link.delete()
					os.remove("hui.mp4")
					await asyncio.sleep(5)
		except: pass
