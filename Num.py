from .. import loader, utils
import asyncio
from telethon.tl.types import MessageEntityTextUrl
import json as JSON

class NumMod(loader.Module):
	"Заражает по реплаю."
	strings={"name": "NumMod"}
	
	async def numcmd(self, message):
		".num [arg] [arg] [arg]....\nВ качестве аргументов используй числа. или первые символы строки."
		reply = await message.get_reply_message()
		a = reply.text
		count_st = 0
		count_hf = 0
		if not a:
			await message.edit('Нет реплая.')
			return
		args = utils.get_args_raw(message)
		list_args=[]
		for i in args.split(' '):
			list_args.append(i)
		if not args:
			await message.edit('Нет аргументов')
			return
		lis = []
		for i in a.splitlines():
			lis.append(i)
		for start in list_args:
			if start.isdigit():
				if not start[:-1] == '.':
					start+='.'
			for x in lis:
				if x.lower().startswith(str(start.lower())):
					count_st = 1
					if 'href="' in x:
						count_hf = 1
						b=x.find('href="')+6
						c=x.find('">')
						link = x[b:c]
						if link.startswith('tg'):
							list = []
							for i in link.split('='):
								list.append(i)
							await message.reply(f'заразить @{list[1]}')
						elif link.startswith('https://t.me'):
							a ='@' + str(link.split('/')[3])
							b = await message.client.get_entity(a)
							await message.reply(f'заразить @{b.id}')
						else:
							await message.reply('что за хуета?')
			await asyncio.sleep(3)
				
		if not count_st:
			await message.edit('Не найдено ни одного совпадения в начале строк с аргументами.')
			
		elif not count_hf:
			await message.edit('Не найдено ни одной ссылки.')
			
		else:
			await message.respond('<b>Заражения успешно завершены.</b>')
			
	async def zarcmd(self, message):
		"Заражает всех по реплаю."
		reply = await message.get_reply_message()
		json = JSON.loads(reply.to_json())
		for i in range(0, len(reply.entities) ):
			try:
				link = json["entities"][i]["url"]
				if link.startswith('tg'):
					list = []
					for i in link.split('='):
						list.append(i)
					await message.reply('заразить @' + list[1])
				elif link.startswith('https://t.me'):
					a ='@' + str(link.split('/')[3])
					b = await message.client.get_entity(a)
					await message.reply(f'заразить @{b.id}')
				else:
					await message.reply('что за хуета?')
			except:
				await message.reply("заразить " + reply.raw_text[json["entities"][i]["offset"]:json["entities"][i]["offset"]+json["entities"][i]["length"]] )
			await asyncio.sleep(3)
		await message.respond('<b>Заражения успешно завершены.</b>')


