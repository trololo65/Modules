# meta developer: @trololo_1

from .. import loader, utils
import subprocess
try:
    from glitch_this import ImageGlitcher
except:
    mod_inst = subprocess.Popen("pip install glitch-this", shell=True) 
    mod_inst.wait()
    from glitch_this import ImageGlitcher


class glitchMod(loader.Module):
	"Накладывает на изображения глитч эффект."
	strings = {"name":"glitchMod"}

	async def client_ready(self, message, db):
		self.db=db
		if not self.db.get("glitch", "frames", False):
			self.db.set("glitch", "frames", 23)
		if not self.db.get("glitch", "step", False):
			self.db.set("glitch", "step", 1)
		if not self.db.get("glitch", "duration", False):
			self.db.set("glitch", "duration", 200)
		if not self.db.get("glitch", "loop", False):
			self.db.set("glitch", "loop", 0)
        
	async def glitchcmd(self, message):
		"Используй: \n.glitch {аргументы} {реплай на фото} {уровень сдвига 0.0 - 10.0} \nЧтобы наложить эффект на фото.\nИспользуй: \n.glitch\nчтобы посмотреть аргументы."
		args = utils.get_args_raw(message)
		reply = await message.get_reply_message()
		glitcher = ImageGlitcher()
		args_glitch = ['-g', '-c', '-sl']
		FRAMES = self.db.get("glitch", "frames")
		STEP = self.db.get("glitch", "step")
		DURATION = self.db.get("glitch", "duration")
		LOOP =self.db.get("glitch", "loop")
		
		gif_output = False
		color = False
		lines = False
		amount = 1.5
		if not reply and not args:
			message = await utils.answer(message, f'Аргументы:\n• <code>{args_glitch[0]}</code>  --- возвращает изображение как гифку. \n• <code>{args_glitch[1]}</code>  --- добавляет эффект смещения цвета. \n• <code>{args_glitch[2]}</code>  --- добавляет эффект линий.')
			return
		if not reply.photo and not reply.sticker:
			message = await utils.answer(message, 'Реплай должен быть на фото.')
			return
		if args:
			args = [i for i in args.split(' ')]
			try:
				amount = float(args[-1])
			except ValueError:
				amount = 1.5
			gif_output = True if args_glitch[0] in args else False
			color = True if args_glitch[1] in args else False
			lines = True if args_glitch[2] in args else False
		file = reply.file.name if reply.file.name else "huita" + reply.file.ext
		await reply.download_media(file)
		b = glitcher.glitch_image(file, amount, color_offset =  color, gif = gif_output, scan_lines = lines, step = STEP, frames = FRAMES)
		if gif_output:
			b[0].save('glitch_image.gif', format = 'GIF', append_images = b[1:], save_all = True, duration = DURATION, loop = LOOP )
			await message.client.send_file(message.to_id, 'glitch_image.gif')
		else:
			b.save('glitch_image.jpg')
			await message.client.send_file(message.to_id, 'glitch_image.jpg')
		await message.delete()
		
		
	async def glconfcmd(self, message):
		"Настройка глитч эффекта."
		args = utils.get_args_raw(message)
		glitch_opt = ["frames", "step", "duration", "loop"]
		if not args:
			message = await utils.answer(message, f"Доступные настройки:\n• <code>{glitch_opt[0]}</code> --- количество кадров.\n• <code>{glitch_opt[1]}</code> --- количество кадров без глюка(значение 1 ставит все кадры с глюком).\n• <code>{glitch_opt[2]}</code> --- длительность кадра(в миллисекундах).\n• <code>{glitch_opt[3]}</code> --- количество зацикливаний(значение 0 бесконечно зацикливает).\n\nИспользовать так:\noption = value")
			return
		args = [ i for i in args.split('=')]
		
		for i in glitch_opt:
			if i == args[0].strip().lower():
				try:
					self.db.set("glitch", i, int(args[1]))
				except ValueError:
					message = await utils.answer(message, 'Значение было не числовым.')
					return
				message = await utils.answer(message, f'Опция <b>{i}</b> успешно установлена со значением <b>{args[1]}</b>')
				return
		message = await utils.answer(message, 'Нет совпадений опций или неправильное значение.')
		return
			
			
