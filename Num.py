from .. import loader, utils
import asyncio, pytz
from telethon.tl.types import MessageEntityTextUrl
import json as JSON
from datetime import datetime, date, time

class NumMod(loader.Module):
	"Заражает по реплаю."
	strings={"name": "NumMod"}
	
	async def client_ready(self, client, db):
		self.db = db
		if not self.db.get("NumMod", "exUsers", False):
			self.db.set("NumMod", "exUsers", [])
		if not self.db.get("NumMod", "infList", False):
			self.db.set("NumMod", "infList", {})
		
	async def numcmd(self, message):
		".num [arg] [arg] [arg]....\nВ качестве аргументов используй числа. или первые символы строки."
		reply = await message.get_reply_message()
		a = reply.text
		exlist = self.db.get("NumMod", "exUsers")
		count_st = 0
		count_hf = 0
		if not reply:
			await message.edit('Нет реплая.')
			return
		args = utils.get_args_raw(message)
		list_args=[]
		if not args:
			await message.edit('Нет аргументов')
			return
		for i in args.split(' '):
			if '-' in i:
				ot_do = i.split('-')
				try:
					for x in range(int(ot_do[0]),int(ot_do[1])+1):
						list_args.append(str(x))
				except:
					await message.respond('Используй правильно функцию "от-до"')
					return
			else:
				list_args.append(i)
		lis = a.splitlines()
		for start in list_args:
			for x in lis:
				if x.lower().startswith(str(start.lower())):
					count_st = 1
					if 'href="' in x:
						count_hf = 1
						b=x.find('href="')+6
						c=x.find('">')
						link = x[b:c]
						if link.startswith('tg'):
							list = '@' + link.split('=')[1]
							if list in exlist:
								await message.reply(f'Исключение: <code>{list}</code>')
							else:
								await message.reply(f'заразить {list}')
							break
						elif link.startswith('https://t.me'):
							a ='@' + str(link.split('/')[3])
							if a in exlist:
								await message.reply(f'Исключение: <code>{a}</code>')
							else:
								await message.reply(f'заразить {a}')
							break
						else:
							await message.reply('что за хуета?')
							break
			await asyncio.sleep(3)
				
		if not count_st:
			await message.edit('Не найдено ни одного совпадения в начале строк с аргументами.')
			
		elif not count_hf:
			await message.edit('Не найдено ни одной ссылки.')
			
		elif len(list_args) >= 3:
			await message.respond('<b>Заражения успешно завершены.</b>')
			
	async def zarcmd(self, message):
		"Заражает всех по реплаю."
		reply = await message.get_reply_message()
		exlist = self.db.get("NumMod", "exUsers")
		if not reply:
			await message.edit('Нет реплая.')
			return
		json = JSON.loads(reply.to_json())
		for i in range(0, len(reply.entities) ):
			try:
				link = json["entities"][i]["url"]
				if link.startswith('tg'):
					list = '@' + link.split('=')[1]
					if list in exlist:
						await message.reply(f'Исключение: <code>{list}</code>')
					else:
						await message.reply('заразить ' + list)
				elif link.startswith('https://t.me'):
					a ='@' + str(link.split('/')[3])
					if a in exlist:
						await message.reply(f'Исключение: <code>{a}</code>')
					else:
						await message.reply(f'заразить {a}')
				else:
					await message.reply('что за хуета?')
			except:
				await message.reply("заразить " + reply.raw_text[json["entities"][i]["offset"]:json["entities"][i]["offset"]+json["entities"][i]["length"]] )
			await asyncio.sleep(3)
		await message.delete() 
		
	async def exnumcmd(self, message):
		"Добавляет исключения в модуль.\nИспользуй: .exnum {@user/@id}"
		args = utils.get_args_raw(message)
		exlistGet = self.db.get("NumMod", "exUsers")
		exlist = exlistGet.copy()
		if not args:
			if len(exlist) < 1:
				await message.edit('Список исключений пуст.')
				return
			exsms = ''
			count = 0
			for i in exlist:
				count+=1
				exsms+=f'<b>{count}.</b> <code>{i}</code>\n'
			message = await utils.answer(message, exsms)
			return
		if args == 'clear':
			exlist.clear()
			self.db.set("NumMod", "exUsers", exlist)
			await message.edit('Список исключений очистен.')
			return
		if len(args.split(' ')) > 1 or args[0] != '@':
			await message.edit('Количество аргументов <b>больше</b> одного, либо начинается <b>не</b> со знака <code>@</code>')
			return
		if args in exlist:
			exlist.remove(args)
			self.db.set("NumMod", "exUsers", exlist)
			await message.edit(f'Пользователь <code>{args}</code> исключён.')
			return
		exlist.append(args)
		self.db.set("NumMod", "exUsers", exlist)
		await message.edit(f'Пользователь <code>{args}</code> добавлен.')
		
	async def zarlistcmd(self, message):
		""" Лист ваших заражений.\n.zarlist {@id/user} {count} {args}\nДля удаления: .zarlist {@id/user}\nАргументы:\n-k -- добавить букву k(тысяч) к числу.\n-f -- поиск по ид'у/юзеру.\n-r -- добавлению в список по реплаю."""
		args = utils.get_args_raw(message)
		infList = self.db.get("NumMod", "infList")
		timezone = "Europe/Kiev"
		vremya = datetime.now(pytz.timezone(timezone)).strftime("%d.%m")
		try:
			args_list = args.split(' ')
		except:
			pass
		if not args:
			if not infList:
				await utils.answer(message, "Лист заражений <b>пуст</b>.")
				return
			sms = ''
			for key, value in infList.items():
				sms+=f'<b>• <code>{key}</code> -- <code>{value[0]}</code> [<i>{value[1]}</i>]</b>\n'
			await utils.answer(message, sms)
			return
		if not '-r' in args.lower():
			if args_list[0] == "clear":
				infList.clear()
				self.db.set("NumMod", "infList", infList)
				await utils.answer(message, "Лист заражений <b>очищен</b>.")
			elif args_list[0] in infList and '-f' in args.lower():
				user = infList[args_list[0]]
				await utils.answer(message, f"<b>• <code>{args_list[0]}</code> -- {user[0]} [<i>{user[1]}</i>]</b>")
			elif len(args_list) == 1 and args_list[0] in infList:
				infList.pop(args_list[0])
				self.db.set("NumMod", "infList", infList)
				await utils.answer(message, f"Пользователь <code>{args}</code> удалён из списка.")
			elif args_list[0][0] != '@':
				await utils.answer(message, 'Это не <b>@ид/юзер</b>.')
			else:
				try:
					user, count = str(args_list[0]), float(args_list[1])
				except:
					await utils.answer(message, "Данные были введены не корректно")
					return
				k = ''
				if '-k' in args.lower():
					k+='k'
				infList[user] = [str(count)+k, vremya]
				self.db.set("NumMod", "infList", infList)
				await utils.answer(message, f"Пользователь <code>{user}</code> добавлен в список заражений.\nЧисло: <code>{count}</code>{k}\nДата: <b>{vremya}</b>")
		else:
			reply = await message.get_reply_message()
			if not reply: 
				return await utils.answer(message, 'Реплай должен быть на смс ириса "<b>...подверг заражению...</b>"')
			elif reply.sender_id != 707693258 and not 'подверг заражению' in reply.text:
				return await utils.answer(message, 'Реплай должен быть на смс ириса "<b>...подверг заражению...</b>"')
			else: #☣
				text = reply.text
				x = text.index('☣')+4
				count = text[x:].split(' ', maxsplit=1)[0]
				x = text.index('user?id=') + 8
				user = '@' + text[x:].split('"', maxsplit=1)[0]
				infList[user] = [str(count), vremya]
				self.db.set("NumMod", "infList", infList)
				await utils.answer(message, f"Пользователь <code>{user}</code> добавлен в список заражений.\nЧисло: <code>{count}</code>\nДата: <b>{vremya}</b>")
