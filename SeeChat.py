from .. import loader, utils
from datetime import datetime, date, time
from asyncio import sleep
import os, io, asyncio, pytz, requests


@loader.tds
class SeeChatMod(loader.Module):
	"""tracking in all PM chats."""
	strings={"name": "SeeChat"}

	async def client_ready(self, message, db):
		self.db = db
		self.db.set("SeeChat", "seechat", True)
		self.di = "SeeChat/"
		if not os.path.exists(self.di):
			os.mkdir(self.di)

	async def seechatcmd(self, message):
		"""use: .seechat | to enable tracking in all PM chats."""
	   
		if self.db.get("SeeChat", "seechat") is not True:
			await utils.answer(message, "[SeeChat] turned <b>on</b> succesfully.")
			self.db.set("SeeChat", "seechat", True)
		else:
			await utils.answer(message, "[SeeChat] turned <b>off</b> succesfully.")
			self.db.set("SeeChat", "seechat", False)

	async def setchatcmd(self, message):
		"""use: .setchat | to set this chat as a track chat."""
	   
		chat = await message.client.get_entity(message.to_id)
		self.db.set("SeeChat", "log", str(chat.id))
		await utils.answer(message, f"<b>this chat was set as a chat for tracks.</b>")

	async def seechatscmd(self, message):
		"""use: .seechats | to see the list of tracking people."""
		
		await utils.answer(message, "wait a second..")
		chats = ""
		for userId in enumerate(os.listdir(self.di)):
			try:
				user = await message.client.get_entity(int(userId[1][:-4]))
			except: pass
			if not user.deleted:
				chats += f"{userId[0]+1} • <a href=tg://user?id={user.id}>{user.first_name}</a> ID: [<code>{user.id}</code>]\n"
			else:
				chats += f"{userId[0]+1} • deleted account ID: [<code>{user.id}</code>]\n"
		await utils.answer(message, "<b>Tracking users:</b>\n\n" + chats)

	async def gseecmd(self, message):
		"""use: .gsee {id} | to get the tracked file."""
		args = utils.get_args_raw(message)
		if not args:
			return await utils.answer(message, "<b>what about args?</b>")
		try:
			user = await message.client.get_entity(int(args))
			await utils.answer(message, f"<b>PM file with: <code>{user.first_name}</code></b>")
			await message.client.send_file(message.to_id, f"{self.di}{args}.txt")
		except: return await utils.answer(message, "<b>file is empty.</b>")

	async def delseecmd(self, message):
		"""use: .delsee {id} | to delete the tracked file."""
		args = utils.get_args_raw(message)
		if not args:
			return await utils.answer(message, "<b>what about args?</b>")
		if args == "all":
			os.system(f"rm -rf {self.di}*")
			await utils.answer(message, "<b>all PM chats file has been successfully deleted.</b>")
		else:
			try:
				user = await message.client.get_entity(int(args))
				await utils.answer(message, f"<b>the chat file has been deleted with: <code>{user.first_name}</code></b>")
				os.remove(f"{self.di}{args}.txt")
			except: return await utils.answer(message, "<b>file can't be deleted.</b>")

	async def excseecmd(self, message):
		"""use: .excsee {id} | to add / remove user from exclude tracking."""
		exception = self.db.get("SeeChat", "exception", [])
		args = utils.get_args_raw(message)
		if not args:
			return await utils.answer(message, "<b>what about args?</b>")
		if args == "clear":
			self.db.set("SeeChat", "exception", [])
			return await utils.answer(message, "<b>the exclusion list was cleared successfully.</b>")
		try:
			user = await message.client.get_entity(int(args))
			if str(user.id) not in exception:
				exception.append(str(user.id))
				await utils.answer(message, f"<b>{user.first_name}, has been added to the list of exclusions.</b>")
				os.remove(f"{self.di}{user.id}.txt")
			else:
				exception.remove(str(user.id))
				await utils.answer(message, f"<b>{user.first_name}, has been removed from the list of exclusions.</b>")
			self.db.set("SeeChat", "exception", exception)
		except: return await utils.answer(message, "<b>failed to remove user from the list of exclusions</b>")
	
	async def exclistcmd(self, message):
		"""use: .exclist | to see the list of exceptions."""
		exception = self.db.get("SeeChat", "exception", [])
		users = ""
		try:
			for exc in enumerate(exception):
				user = await message.client.get_entity(int(exc[1]))
				users += f"{exc[0]+1} • <a href=tg://user?id={user.id}>{user.first_name}</a> ID: [<code>{user.id}</code>]\n"
			await utils.answer(message, "<b>List of exclusions:</b>\n\n" + users)
		except Exception as e: return await utils.answer(message, f"<b>the list of users is empty.</b> {e}")

	async def watcher(self, message):
		me = await message.client.get_me()
		seechat = self.db.get("SeeChat", "seechat")
		exception = self.db.get("SeeChat", "exception", [])
		log = self.db.get("SeeChat", "log", str(me.id))
		chat = await message.client.get_entity(int(log))
		timezone = "Europe/Kiev"
		vremya = datetime.now(pytz.timezone(timezone)).strftime("[%Y-%m-%d %H:%M:%S]")
		user = await message.client.get_entity(message.chat_id)
		userid = str(user.id)
		try:
			if message.sender_id == me.id: user.first_name = me.first_name
		except: pass
		if message.is_private and seechat and userid not in exception and not user.bot and not user.verified:
			if message.text:
				file = open(f"{self.di}{user.id}.txt", "a", encoding='utf-8')
				file.write(f"{user.first_name} >> {message.text} << {vremya}\n\n")
			if message.sender_id == me.id:
				return
			if message.video:
				try:
					await message.forward_to(chat.id)
				except:
					file = message.file.name or "huita" + message.file.ext
					await message.download_media(file)
					await message.client.send_message(chat.id, f"<b>Video from</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>:")
					await message.client.send_file(chat.id, file)
					os.remove(file)
			elif message.photo:
				file = io.BytesIO()
				file.name = message.file.name or f"SeeChat{message.file.ext}"
				await message.client.download_file(message, file)
				file.seek(0)
				await message.client.send_message(chat.id, f"<b>Picture from</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>:")
				await message.client.send_file(chat.id, file, force_document=False)
			elif message.voice or message.audio or message.video_note or message.document:
				await message.client.send_message(chat.id, f"<b>Media from</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>:")
				await message.forward_to(chat.id)