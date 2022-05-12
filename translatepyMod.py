# meta developer: @trololo_1
# Github: trololo65
import subprocess
try:
	from translatepy import Translator
except:
	mod_inst = subprocess.Popen("pip install --upgrade translatepy", shell=True) 
	mod_inst.wait()
	from translatepy import Translator
from translatepy.translators.google import GoogleTranslate
from translatepy.translators.bing import BingTranslate
from translatepy.translators.yandex import YandexTranslate
from translatepy.translators.reverso import ReversoTranslate
from translatepy.translators.deepl import DeeplTranslate
from translatepy.translators.libre import LibreTranslate
from translatepy.translators.translatecom import TranslateComTranslate
from translatepy.translators.mymemory import MyMemoryTranslate
from .. import loader, utils

@loader.tds
class translatepyMod(loader.Module):
	"""Перевод текста. Автоматическое распознование языка."""
	strings = {'name': 'translatepy'}
	
	async def client_ready(self, client, db):
		self.db = db
		if not self.db.get('translatepy', 'services', False):
			self.db.set('translatepy', 'services', {'google': True, 'bing': False, 'yandex': False, 'reverso': False, 'libre': False, 'translatecom': False, 'deepl': False, 'mymemory': False,})

	async def trnsltcmd(self, message):
		"""Используй: .trnslt {язык} {текст или реплай}"""
		
		args = utils.get_args_raw(message)
		reply = await message.get_reply_message()
		args_list = args.split(' ', maxsplit = 1)
		sL = self.db.get('translatepy', 'services') #serviceList
		if not args:
			await utils.answer(message, 'Где аргументы?')
			return 
		if not reply and len(args_list) <= 1 :
			await utils.answer(message, 'Нет реплая и текста для перевода.')
			return 
		if len(args_list) == 1:
			text = reply.raw_text
		else:
			text = args_list[1]
		lng = args_list[0]
		sL_class = {'google': GoogleTranslate(), 'yandex': YandexTranslate(), 'bing': BingTranslate(), 'reverso': ReversoTranslate(), 'deepl': DeeplTranslate(), 'libre': LibreTranslate(), 'translatecom': TranslateComTranslate(), 'mymemory': MyMemoryTranslate()}
		try:
			sL_active = str(list(sL.keys())[list(sL.values()).index(True)]) # Поиск установленного сервера
			t = sL_class[sL_active]
		except:
			t = Translator()

		res = t.translate(text,lng) # result translate

		await utils.answer(message, f'<b>[{res.service}: {res.source_language} -> {lng}]</b>\n<code>{res.result}</code>')

	async def tservicecmd(self, message):
		""" Установка сервиса для перевода.\nИспользуй .tservice list для просмотра всех сервисов"""
		args = utils.get_args_raw(message)
		sL = self.db.get('translatepy', 'services') #serviceList
		service = str(list(sL.keys())[list(sL.values()).index(True)]) # Поиск установленного сервера
		if not args:
			await utils.answer(message, '<b>Установка:</b> <code>.tservice {сервис}</code>'+f'\n<b>Сервис:</b> <code>{service}</code>')
		elif args == 'list':
			await utils.answer(message, '<b>Достуные сервисы:</b>\n<code>Google</code>\n<code>Bing</code>\n<code>Yandex</code>\n<code>Reverso</code>\n<code>Deepl</code>\n<code>Libre</code>\n<code>TranslateCom</code>\n<code>MyMemory</code>')
		elif args.lower() in sL:
			for key, value in sL.items(): # Переборка словаря
				sL[key] = False # Установка всех значений на False
			sL[args.lower()] = True # Установка нужного значения на True
			self.db.set('translatepy', 'services', sL)
			await utils.answer(message, f'Сервис <b>{args}</b> успешно установлен.')
		else:
			await utils.answer(message, f'Неверно введён сервис.')
