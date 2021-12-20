# by: @trololo_1
import subprocess
try:
	import emoji
except:
	mod_inst = subprocess.Popen("pip install emoji", shell=True) 
	mod_inst.wait()
	import emoji
from .. import loader, utils
import string, pickle

@loader.tds
class RPMod(loader.Module):
	"""Модуль RPMod."""
	strings = {'name': 'RPMod'}

	async def client_ready(self, client, db):
		self.db = db
		if not self.db.get("RPMod", "exlist", False):
			self.db.set("RPMod", "exlist", [])
		if not self.db.get("RPMod", "status", False):
			self.db.get("RPMod", "status", 1)
		if not self.db.get("RPMod", "rprezjim", False):
			self.db.set("RPMod", "rprezjim", 1)
		if not self.db.get('RPMod', 'rpnicks', False):
			self.db.set('RPMod', 'rpnicks', {})
		if not self.db.get('RPMod', 'rpcomands', False):
			comands = {'чмок': 'чмокнул', 'лизь': 'лизнул', 'кусь': 'кусьнул', 'поцеловать': 'поцеловал', 'выебать': 'выебал', 'трахнуть': 'трахнул', 'выпороть': 'выпорол', 'шлепнуть': 'шлепнул', 'отлизать': 'отлизал у', 'прижать': 'прижал', 'погладить': 'погладил', 'да.': 'пизда', 'где.': 'в пизде', 'нет.': 'пидора ответ', 'бывает.': 'ну это пиздец конечно на самом деле', 'обнять': 'обнял'}
			self.db.set('RPMod', 'rpcomands', comands)
		if not self.db.get('RPMod', 'rpemoji', False):
			self.db.set('RPMod', 'rpemoji', {'лизь': '👅'})
		if not self.db.get('RPMod', 'useraccept', False):
			self.db.set('RPMod', 'useraccept', [])

	async def dobrpcmd(self, message):
		"""Используй: .dobrp (команда) / (действие) / (эмодзи) чтобы добавить команду. Можно и без эмодзи."""
		args = utils.get_args_raw(message)
		dict_rp = self.db.get('RPMod', 'rpcomands')
		
		try:
			key_rp = str(args.split('/')[0]).strip()
			value_rp = str(args.split('/', maxsplit=2)[1]).strip()
			lenght_args = args.split('/')
			count_emoji = 0
			
			if len(lenght_args) >= 3:
				emoji_rp = str(args.split('/', maxsplit=2)[2]).strip()
				dict_emoji_rp = self.db.get('RPMod', 'rpemoji')
				
				r = emoji_rp
				lst = []
				count_emoji = 1
				for x in r:
					if x in emoji.UNICODE_EMOJI['en'].keys(): lst.append(x)
					if x.isalpha() or x.isspace() or x.isdigit() or x in string.punctuation:
						await utils.answer(message, f"<b>Были введены не только эмодзи(пробел тоже символ). </b>")
						return
				if len(lst) > 3:
					await utils.answer(message, f"<b>Было введено более 3 эмодзи.</b>")
					return
				elif not emoji_rp or not emoji_rp.strip():
					await utils.answer(message, f"<b>Разделитель для эмодзи есть, а их нет? хм.</b>")
					return
				
		
			key_len = [len(x) for x in key_rp.split()]
		
			if len(dict_rp) >= 70:
				await utils.answer(message, '<b>Достигнут лимит рп команд.</b>')
			elif not key_rp or not key_rp.strip():
				await utils.answer(message, '<b>Вы не ввели название рп команды.</b>')
			elif not value_rp or not value_rp.strip():
				await utils.answer(message, '<b>Вы не ввели действие для рп команды.</b>')
			elif int(len(key_len)) > 1:
				await utils.answer(message, '<b>В качестве рп команды было введено больше одного слова.</b>')
			elif key_rp == 'all':
				await utils.answer(message, '<b>Использовать \'<code>all</code>\' в качестве названия команды запрещено!</b>')
			elif count_emoji == 1:
				dict_emoji_rp[key_rp] = emoji_rp
				dict_rp[key_rp]= value_rp
				self.db.set('RPMod', 'rpcomands', dict_rp)
				self.db.set('RPMod', 'rpemoji', dict_emoji_rp)
				await utils.answer(message, f'<b>Команда \'<code>{key_rp}</code>\' успешно добавлена с эмодзи \'{emoji_rp}\'!</b>')
			else:
				 dict_rp[key_rp]= value_rp
				 self.db.set('RPMod', 'rpcomands', dict_rp)
				 await utils.answer(message, f'<b>Команда \'<code>{key_rp}</code>\' успешно добавлена!</b>')
		except:
			await utils.answer(message, '<b>Вы не ввели разделитель /, либо вовсе ничего не ввели.</b>')

	async def delrpcmd(self, message):
		"""Используй: .delrp (команда) чтобы удалить команду.\n Используй: .delrp all чтобы удалить все команды."""
		args = utils.get_args_raw(message)
		dict_rp = self.db.get('RPMod', 'rpcomands')
		dict_emoji_rp = self.db.get('RPMod', 'rpemoji')
		key_rp = str(args)
		count = 0
		if key_rp == 'all':
			dict_rp.clear()
			dict_emoji_rp.clear()
			self.db.set('RPMod', 'rpcomands', dict_rp)
			self.db.set('RPMod', 'rpemoji', dict_emoji_rp)
			await utils.answer(message, '<b>Список рп команд очищен.</b>')
			return
		elif not key_rp or not key_rp.strip():
			await utils.answer(message, '<b>Вы не ввели команду.</b>')
		else:
			try:
				if key_rp in dict_emoji_rp:
					dict_rp.pop(key_rp)
					dict_emoji_rp.pop(key_rp)
					self.db.set('RPMod', 'rpcomands', dict_rp)
					self.db.set('RPMod', 'rpemoji', dict_emoji_rp)
				else:
					dict_rp.pop(key_rp)
					self.db.set('RPMod', 'rpcomands', dict_rp)
				await utils.answer(message, f'<b>Команда \'<code>{key_rp}</code>\' успешно удалена!</b>')
			except KeyError:
				await utils.answer(message, '<b>Команда не найдена.</b>')

	async def rpmodcmd(self, message):
		"""Используй: .rpmod чтобы включить/выключить RP режим.\nИспользуй: .rpmod toggle чтобы сменить режим на отправку или изменение смс."""
		status = self.db.get("RPMod", "status")
		rezjim = self.db.get("RPMod", "rprezjim")
		args = utils.get_args_raw(message)
		if not args:
			if status == 1:
				self.db.set("RPMod", "status", 2)
				await utils.answer(message, "<b>RP Режим <code>выключен</code></b>")
			else:
				self.db.set("RPMod", "status", 1)
				await utils.answer(message, "<b>RP Режим <code>включен</code></b>")
		elif args.strip() == 'toggle':
			if rezjim == 1:
				self.db.set("RPMod", "rprezjim", 2)
				await utils.answer(message, "<b>RP Режим изменён на <code>отправку смс.</code></b>")
			else:
				self.db.set("RPMod", "rprezjim", 1)
				await utils.answer(message, "<b>RP Режим изменён на <code>изменение смс.</code></b>")
		else:  	
			await utils.answer(message, 'Что то не так.. ')

	async def rplistcmd(self, message):
		"""Используй: .rplist чтобы посмотреть список рп команд."""
		com = self.db.get('RPMod', 'rpcomands')
		emojies = self.db.get('RPMod', 'rpemoji')
		l = len(com)
		
		listComands = f'У вас рп команд: <b>{l}</b> из <b>70</b>. '
		if len(com) == 0:
			await utils.answer(message, '<b>Увы, у вас нету рп команд. :(</b>')
			return
		for i in com:
			if i in emojies.keys():
				listComands+=f'\n• <b><code>{i}</code> - {com[i]} |</b> {emojies[i]}'
			else:
				listComands+=f'\n• <b><code>{i}</code> - {com[i]}</b>'
		await utils.answer(message, listComands)

	async def rpnickcmd(self, message):
		"""Используй: .rpnick (ник) чтобы сменить свой ник. Если без аргументов, то вернётся ник из тг."""
		r = utils.get_args_raw(message).strip()
		nicks = self.db.get('RPMod', 'rpnicks')
		me = await message.client.get_entity(message.sender_id)
		if not r:
			nicks[str(me.id)] = me.first_name
			self.db.set('RPMod', 'rpnicks', nicks)
			await utils.answer(message, f"<b>Ник изменён на {me.first_name}</b>")
			return
		lst = []
		nick = ''
		for x in r:
			if x in emoji.UNICODE_EMOJI['en'].keys(): lst.append(x)
			if x not in emoji.UNICODE_EMOJI['en'].keys(): nick+=x
		if len(lst) > 3:
			await utils.answer(message, f"<b>Ник '{r}' содержит более трёх эмодзи.</b>")
		elif len(lst) + len(nick) >= 45:
			await utils.answer(message, f"<b>Ник превышает лимит в 45 символов(возможно эмодзи имеют длину более 1 символа).</b>")
		else:
			nicks[str(me.id)] = r
			self.db.set('RPMod', 'rpnicks', nicks)
			await utils.answer(message, f"<b>Ник изменён на {r}</b>")

	async def rpbackcmd(self, message):
		"""Бекап рп команд.\n .rpback для просмотра аргументов. """
		args = utils.get_args_raw(message).strip()
		comands = self.db.get('RPMod', 'rpcomands')
		emojies = self.db.get('RPMod', 'rpemoji')
		file_name = 'RPModBackUp.pickle'
		id = message.to_id
		reply = await message.get_reply_message()
		if not args:
			await utils.answer(message, '<b>Аргументы:</b>\n<code>-b</code> <b>-- сделать бекап.</b>\n<code>-r</code> <b>загрузить бекап.(используй с реплаем на файл)</b>')
		if args == '-b':
			try:
				await message.delete()
				dict_all = { 'rp': comands, 'emj': emojies}
				with open(file_name, 'wb') as f:
					pickle.dump(dict_all, f)
				await message.client.send_file(id, file_name)
			except Exception as e:
				await utils.answer(message, f"<b>Ошибка:\n</b>{e}")
		elif args == '-r' and reply:
			try:
				if not reply.document:
					await utils.answer(message, f"<b>Это не файл.</b>")
				await reply.download_media(file_name)
				with open(file_name, 'rb') as f:
					data = pickle.load(f)
				rp = data['rp']
				emj = data['emj']
				result_rp = dict(comands, **rp)
				result_emj = dict(emojies, **emj)
				self.db.set('RPMod', 'rpcomands', result_rp)
				self.db.set('RPMod', 'rpemoji', result_emj)
				await utils.answer(message, f"<b>Команды обновлены!</b>")
			except Exception as e:
				await utils.answer(message, f"<b>Ошибка:\n</b>{e}")
			
	async def rpblockcmd(self, message):
		"""Используй: .rpblock чтобы добавить/удалить исключение(использовать в нужном чате).\nИспользуй: .rpblock list чтобы просмотреть чаты в исключениях.\nИспользуй .rpblock (ид) чтобы удалить чат из исключений."""
		args = utils.get_args_raw(message)
		ex = self.db.get("RPMod", "exlist")
		if not args:
			a = await message.client.get_entity(message.to_id)
			if a.id in ex:
				ex.remove(a.id)
				self.db.set("RPMod", "exlist", ex)
				try:
					name = a.title
				except:
					name = a.first_name
				await utils.answer(message, f'<i>Чат <b><u>{name}</u></b>[<code>{a.id}</code>] удален из исключений.</i>')
			else:
				ex.append(a.id)
				self.db.set("RPMod", "exlist", ex)
				try:
					name = a.title
				except:
					name = a.first_name
				await utils.answer(message, f'<i>Чат <b><u>{name}</u></b>[<code>{a.id}</code>] добавлен в исключения.</i>')
		elif args.isdigit():
			args = int(args)
			if args in ex:
				ex.remove(args)
				self.db.set("RPMod", "exlist", ex)
				a = await message.client.get_entity(args)
				try:
					name = a.title
				except:
					name = a.first_name
				await utils.answer(message, f'<i>Чат <b><u>{name}</u></b>(<code>{args}</code>) удален из исключений.</i>')
			else:
				try:
					a = await message.client.get_entity(args)
				except:
					await utils.answer(message, '<b>Неверный ид.</b>')
				ex.append(args)
				self.db.set("RPMod", "exlist", ex)
				try:
					name = a.title
				except:
					name = a.first_name
				await utils.answer(message, f'<i>Чат <b><u>{name}</u></b>[<code>{a.id}</code>] добавлен в исключения.</i>')
		elif args == 'list':
			ex_len = len(ex)
			if ex_len == 0:
				await utils.answer(message, f'<b>Список исключений пуст.</b>')
				return
			sms = f'<i> Чаты, которые есть в исключениях({ex_len}):</i>'
			for i in ex:
				try:
					a = await message.client.get_entity(i)
				except:
					await utils.answer(message, f'<b>Неверный ид -- {a}</b>')
					return
				try:
					name = a.title
				except:
					name = a.first_name
				sms+=f'\n• <b><u>{name}</u> --- </b><code>{i}</code>'
			await utils.answer(message, sms)
		else:
			await utils.answer(message, 'Что то пошло не так..')

	async def useracceptcmd(self, message):
		""" Добавление/удаление пользователей, разрешенным использовать ваши команды.\n .useraccept {id/reply} """
		reply = await message.get_reply_message()
		args = utils.get_args_raw(message)
		userA = self.db.get('RPMod', 'useraccept')
		if not reply and not args:
			await utils.answer(message, 'Нет ни реплая, ни аргрументов.')
		elif args == '-l':
			sms = '<b>Пользователи, у которых есть доступ к командам:</b>'
			for i in userA:
				try:
					user = await message.client.get_entity(int(i))
					sms+= f'\n<b>• <u>{user.first_name}</u> ---</b> <code>{i}</code>'
				except:
					sms+= f'\n<b>•</b> <code>{i}</code>'
			await utils.answer(message, sms)
		elif args or reply:
			args = int(args) if args.isdigit() else reply.sender_id
			if args in userA:
				userA.remove(args)
				self.db.set('RPMod', 'useraccept', userA)
				await utils.answer(message, f'<b>Пользователю <code>{args}</code> был закрыт доступ.</b>')
			else:
				userA.append(args)
				self.db.set('RPMod', 'useraccept', userA)
				await utils.answer(message, f'<b>Пользователю <code>{args}</code> был открыт доступ.</b>')
		else:
			await utils.answer(message, 'Что то не так..')

	async def watcher(self, message):
		try:
			status = self.db.get("RPMod", "status")
			comand = self.db.get('RPMod', 'rpcomands')
			rezjim = self.db.get('RPMod', 'rprezjim')
			emojies = self.db.get('RPMod', 'rpemoji')
			ex = self.db.get("RPMod", "exlist")
			nicks = self.db.get('RPMod', 'rpnicks')
			users_accept = self.db.get('RPMod', 'useraccept')

			me = (await message.client.get_entity(message.sender_id))
			me_id = (await message.client.get_me()).id
			if str(me.id) in nicks.keys():
				nick = nicks[str(me.id)]
			else:
				nick = me.first_name
			args = message.text.lower()
			
			chat_rp = await message.client.get_entity(message.to_id)
			lines = args.splitlines()
			detail = []
			tags = lines[0].split(' ')
			round = 1
			if not tags[-1].startswith('@'):
				reply = await message.get_reply_message()
				user = await message.client.get_entity(reply.sender_id)
			else:
				if tags[0] in comand:
					if message.sender_id == me_id or message.sender_id in users_accept:
						if not tags[-1][1:].isdigit():
							user = await message.client.get_entity(tags[-1])
						else:
							user = await message.client.get_entity(int(tags[-1][1:]))
						lines[0] = lines[0].rsplit(' ', 1)[0]
			for i in lines[0].split(' ',maxsplit=1):
				if round == 1:
					detail.append(i)
				else:
					detail.append(' '+i)
				round+=1
			if len(detail) < 2:
				detail.append(' ')
			user.first_name = nicks[str(user.id)] if str(user.id) in nicks else user.first_name
			
			if status == 1 and chat_rp.id not in ex:
				if message.sender_id in users_accept or message.sender_id == me_id:
					for i in comand:
						if detail[0] == i:
							if detail[0] in emojies.keys():
								if len(lines) < 2:
									if rezjim == 1:
										return await utils.answer(message, f"{emojies[detail[0]]} | <a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"+detail[1])
									else:
										return await message.respond(f"{emojies[detail[0]]} | <a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"+detail[1])
								else:
									if rezjim == 1:
										return await utils.answer(message, f"{emojies[detail[0]]} | <a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"+detail[1]+f"\n<b>С репликой: </b>{lines[1]}")
									else:
										return await message.respond(f"{emojies[detail[0]]} | <a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"+detail[1]+f"\n<b>С репликой: </b>{lines[1]}")
							else:
								if len(lines) < 2:
									if rezjim == 1:
										return await utils.answer(message, f"<a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"+detail[1])
									else:
										return await message.respond(f"<a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"+detail[1])
								else:
									if rezjim == 1:
										return await utils.answer(message, f"<a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"+detail[1]+f"\n<b>С репликой: </b>{lines[1]}")
									else:
										return await message.respond(f"<a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"+detail[1]+f"\n<b>С репликой: </b>{lines[1]}")
		except: pass
