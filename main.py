import os
import re
import sys
import time
import shutil
import os.path
import asyncio
from telethon import functions, types
from distutils.dir_util import copy_tree
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterDocument, InputMessagesFilterRoundVideo, InputMessagesFilterVoice, InputMessagesFilterVideo

# API DATA
api_id = 00000000
api_hash = 'hash'
loop = asyncio.get_event_loop()

# Заменить смайлики
def replace_astral(str):
	s = list(str)
	if str == "None":
		return ""
	else:
		for i in range(len(s)):
			c = ord(s[i])
			if c > 0xFFFF:
				s[i] = ''.format(c)
		return ''.join(s)

# Запуск программы
async def main():
	if os.path.isfile("account/telethon.session") == True:
		async with TelegramClient("account/telethon.session", api_id, api_hash) as client:

			# Вывод информации о профиле
			me = await client.get_me()
			name = "@"+me.username if me.username != None else replace_astral(str(me.last_name)) + " " + replace_astral(str(me.first_name))
			username = "@"+me.username if me.username != None else ""
			phone = "+"+str(me.phone) if me.phone != None else ""
			path = f"ID_{me.id} ({name})"
			if os.path.exists(path) == False:
				os.mkdir(path)

			# Скопировать telethon session и tdata
			if os.path.isfile(path+"/telethon.session") == False:
				shutil.copy("account/telethon.session", path)

			# Сохранить файл с информацией о профиле
			if os.path.isfile(path+"/Profile Info.txt") == False:
				with open(path+"/Profile Info.txt", 'w', encoding='utf-8') as f:
					f.write(f"""ID: {me.id}\nAccess Hash: {me.access_hash}\nFirst Name: {replace_astral(str(me.first_name))}\nLast Name {replace_astral(str(me.last_name))}\nUsername: {username}\nPhone Number: {phone}""")

			# Получить диалоги
			if os.path.isfile(path+"/Dialogs Info.txt") == False:
				dialogs = await client.get_dialogs(limit=None)
				users_dialogs = [f"{me.id} - {replace_astral(str(me.last_name))} {replace_astral(str(me.first_name))}"]
				channel_dialogs = []
				for i in range(len(dialogs)):
					if dialogs[i].entity.id != me.id:
						# Переписки
						if hasattr(dialogs[i].message.peer_id, 'user_id') == True:
							username = "(@"+dialogs[i].entity.username+")" if dialogs[i].entity.username != None else ""
							if dialogs[i].entity.bot == False:
								phone = "(+"+str(dialogs[i].entity.phone)+")" if dialogs[i].entity.phone != None else ""
								users_dialogs.append(f"{dialogs[i].entity.id} - {replace_astral(str(dialogs[i].entity.last_name))} {replace_astral(str(dialogs[i].entity.first_name))} {username} {phone}")
						
						# Приватные каналы
						elif hasattr(dialogs[i].message.peer_id, 'channel_id') == True:
							if hasattr(dialogs[i].entity, 'username') == True:
								if dialogs[i].entity.username == None:
									channel_dialogs.append(f"{dialogs[i].entity.id} - {replace_astral(str(dialogs[i].entity.title))} (Private Chat)")

				# Сохранить файл с диалогами
				with open(path+"/Dialogs Info.txt", 'w', encoding='utf-8') as f:
					for row in users_dialogs + channel_dialogs:
						f.write(str(row) + '\n')

				print("Отсортируйте чаты в файле 'Dialogs Info.txt' и перезапустите программу")
				time.sleep(10000)

			# Вывод информации о скачивании 
			def callback(current, total):
				pr = '{:.2%}'.format(current / total)
				sys.stdout.write(f'Скачиваю видео {int(current/1048576)}/{int(total/1048576)} MB: {pr}\r')
				sys.stdout.flush()

			# Получить медиа
			async def download_media(path, id_dialog, msgs):
				id_msg = 0
				for msg in msgs:
					try:
						if msg.media is not None:
							id_msg += 1
							media = msg.media
							if hasattr(media, 'photo'):
								print(f"Скачиваю фото {id_msg}/{len(msgs)} {id_dialog}_{msg.id}.jpg")
								if os.path.isfile(f"{path}/Media/1. Photos/{id_dialog}_{msg.id}.jpg") == False:
									await client.download_media(message=msg, file=f"{path}/Media/1. Photos/{id_dialog}_{msg.id}.jpg", thumb=1)
							elif hasattr(media, 'document'):
								if hasattr(media.document, 'mime_type'):
									if media.document.mime_type == "video/mp4":
										if hasattr(media.document.attributes[0], 'round_message'):
											if media.document.attributes[0].round_message == True:
												print(f"Скачиваю видео {id_msg}/{len(msgs)} {id_dialog}_{msg.id}.jpg ({int(media.document.size/1048576)} MB)")
												if os.path.isfile(path+f"/Media/3. Round Videos/{id_dialog}_{msg.id}.jpg") == False:
													await client.download_media(message=msg, file=path+f"/Media/3. Round Videos/{id_dialog}_{msg.id}.jpg", thumb=1)
											else:
												print(f"Скачиваю видео {id_msg}/{len(msgs)} {id_dialog}_{msg.id}.jpg ({int(media.document.size/1048576)} MB)")
												if os.path.isfile(path+f"/Media/2. Videos/{id_dialog}_{msg.id}.jpg") == False:
													await client.download_media(message=msg, file=path+f"/Media/2. Videos/{id_dialog}_{msg.id}.jpg", thumb=1)
										else:
											print(f"Скачиваю видео {id_msg}/{len(msgs)} {id_dialog}_{msg.id}.jpg ({int(media.document.size/1048576)} MB)")
											if os.path.isfile(path+f"/Media/2. Videos/{id_dialog}_{msg.id}.jpg") == False:
												await client.download_media(message=msg, file=path+f"/Media/2. Videos/{id_dialog}_{msg.id}.jpg", thumb=1)
									elif media.document.mime_type == "audio/ogg":
										print(f"Скачиваю голосовое сообщение {id_msg}/{len(msgs)} {id_dialog}_{msg.id}.ogg")
										if os.path.isfile(path+f"/Media/4. Voice Messages/{id_dialog}_{msg.id}.ogg") == False:
											await client.download_media(message=msg, file=path+f"/Media/4. Voice Messages/{id_dialog}_{msg.id}.ogg")
									elif media.document.mime_type == "image/webp":
										print("")
									elif media.document.mime_type == "video/webp":
										print("")
									elif media.document.mime_type == "application/x-tgsticker":
										print("")
									else:
										if media.document.size < 62914560:
											if hasattr(media.document.attributes[0], 'file_name'):
												file_name = replace_astral(str(media.document.attributes[0].file_name))
											else:
												file_name = str(msg.id)
											print(f"Скачиваю документ {id_msg}/{len(msgs)} {file_name} ({int(media.document.size/1048576)} MB)")
											await client.download_media(message=msg, file=path+f"/Media/5. Documents/{id_dialog}_{file_name}", progress_callback=callback)
										else:
											print(f"Вес файла {int(media.document.size/1048576)} MB - отмена скачивания")
					except Exception as a:
						if str(a).find("disk is full") != -1:
							print("Недостаточно памяти на диске!")
							sys.exit()
						print(a)

			await client.get_dialogs(limit=None)
			# Получить сообщения
			if os.path.isfile(path+"/Dialogs Info.txt") == True:
				with open(path+"/Dialogs Info.txt", 'r+', encoding='utf-8') as f:
					lines = f.readlines()
					users_dialogs = []
					users_dialogs_names = []
					group_dialogs = []
					group_dialogs_names = []
					for i in range(len(lines)):
						if lines[i].find("* ") == -1:
							if lines[i].find("(Private Chat)") != -1:
								group_dialogs.append(lines[i].split(" - ")[0].replace("\ufeff",""))
								group_dialogs_names.append(lines[i].split(" - ")[1].replace("\ufeff",""))
							else:
								users_dialogs.append(lines[i].split(" - ")[0].replace("\ufeff",""))
								users_dialogs_names.append(lines[i].split(" - ")[1].replace("\ufeff",""))

					# Получить медиа с переписок
					for i in range(len(users_dialogs)):
						print(f" - Диалог {i+1}/{len(users_dialogs)} - {users_dialogs_names[i]}")
						id_dialog = int(str(users_dialogs[i]))
						try:
							await download_media(path, id_dialog, await client.get_messages(await client.get_entity(id_dialog), limit=500, filter=InputMessagesFilterPhotos))
							await download_media(path, id_dialog, await client.get_messages(await client.get_entity(id_dialog), limit=200, filter=InputMessagesFilterVideo))
							#await download_media(path, id_dialog, await client.get_messages(await client.get_entity(id_dialog), limit=150, filter=InputMessagesFilterRoundVideo))
							#await download_media(path, id_dialog, await client.get_messages(await client.get_entity(id_dialog), limit=150, filter=InputMessagesFilterVoice))
							#await download_media(path, id_dialog, await client.get_messages(await client.get_entity(id_dialog), limit=250, filter=InputMessagesFilterDocument))
						except Exception as a:
							print(a)
						for i2 in range(len(lines)):
							if lines[i2].find(str(id_dialog)) != -1:
								lines[i2] = "* "+lines[i2] 
						with open(path+"/Dialogs Info.txt", 'w', encoding='utf-8') as f:
							f.writelines(lines)

					# Получить медиа с чатов
					for i in range(len(group_dialogs)):
						print(f" - Чат {i+1}/{len(group_dialogs)} - {group_dialogs_names[i]}")
						id_dialog = int(str(group_dialogs[i]))
						try:
							await download_media(path, id_dialog, await client.get_messages(await client.get_entity(id_dialog), limit=100, filter=InputMessagesFilterPhotos))
							await download_media(path, id_dialog, await client.get_messages(await client.get_entity(id_dialog), limit=100, filter=InputMessagesFilterVideo))
							await download_media(path, id_dialog, await client.get_messages(await client.get_entity(id_dialog), limit=100, filter=InputMessagesFilterRoundVideo))
							await download_media(path, id_dialog, await client.get_messages(await client.get_entity(id_dialog), limit=100, filter=InputMessagesFilterVoice))
							await download_media(path, id_dialog, await client.get_messages(await client.get_entity(id_dialog), limit=100, filter=InputMessagesFilterDocument))
						except Exception as a:
							print(a)
						for i2 in range(len(lines)):
							if lines[i2].find(str(id_dialog)) != -1:
								lines[i2] = "* "+lines[i2]
						with open(path+"/Dialogs Info.txt", 'w', encoding='utf-8') as f:
							f.writelines(lines)

					print("Дамп готов!")
			else:
				print("Ошибка! Отсутствует база с диалогами")
	else:
		print("Отсутствует файл telethon.session")

loop.run_until_complete(main())
