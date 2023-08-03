import os
import re
import sys
import time
import shutil
import os.path
import asyncio
from os import listdir
from os.path import isfile, join
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
onlyfolders = [f for f in listdir() if isfile(join("", f)) == False and f != "account"]
for i in range(len(onlyfolders)):
	print(str(i+1)+". "+onlyfolders[i])
folder = onlyfolders[int(input("Выберете папку с данными: "))-1]

async def main():
	if os.path.isfile(folder+"/telethon.session") == True:
		async with TelegramClient(folder+"/telethon.session", api_id, api_hash) as client:
			path = folder

			# Вывод информации о скачивании 
			def callback(current, total):
				pr = '{:.2%}'.format(current / total)
				sys.stdout.write(f'Скачиваю видео {int(current/1048576)}/{int(total/1048576)} MB: {pr}\r')
				sys.stdout.flush()

			# Получить медиа
			async def download_media(path, id_dialog, msgs):
				id_msg = 0
				try:
					for msg in msgs:
						if hasattr(msg, 'media'):
							if msg.media is not None:
								id_msg += 1
								media = msg.media
								if hasattr(media, 'photo'):
									if os.path.getsize(f"{path}/Media/1. Photos/{id_dialog}_{msg.id}.jpg") < 48000:
										print(f"Скачиваю фото {id_msg}/{len(msgs)} {id_dialog}_{msg.id}.jpg")
										await client.download_media(message=msg, file=f"{path}/Media/1. Photos/{id_dialog}_{msg.id}.jpg")
								elif hasattr(media, 'document'):
									if hasattr(media.document, 'mime_type'):
										if media.document.mime_type == "video/mp4":
											if hasattr(media.document.attributes[0], 'round_message'):
												if media.document.attributes[0].round_message == True:
													print(f"Скачиваю видео {id_msg}/{len(msgs)} {id_dialog}_{msg.id}.mp4 ({int(media.document.size/1048576)} MB)")
													if os.path.isfile(path+f"/Media/3. Round Videos/{id_dialog}_{msg.id}.mp4") == False:
														await client.download_media(message=msg, file=path+f"/Media/3. Round Videos/{id_dialog}_{msg.id}.mp4", progress_callback=callback)
														os.remove(path+f"/Media/3. Round Videos/{id_dialog}_{msg.id}.jpg")
												else:
													print(f"Скачиваю видео {id_msg}/{len(msgs)} {id_dialog}_{msg.id}.mp4 ({int(media.document.size/1048576)} MB)")
													if os.path.isfile(path+f"/Media/2. Videos/{id_dialog}_{msg.id}.mp4") == False:
														await client.download_media(message=msg, file=path+f"/Media/2. Videos/{id_dialog}_{msg.id}.mp4", progress_callback=callback)
														os.remove(path+f"/Media/2. Videos/{id_dialog}_{msg.id}.jpg")
											else:
												print(f"Скачиваю видео {id_msg}/{len(msgs)} {id_dialog}_{msg.id}.mp4 ({int(media.document.size/1048576)} MB)")
												if os.path.isfile(path+f"/Media/2. Videos/{id_dialog}_{msg.id}.mp4") == False:
													await client.download_media(message=msg, file=path+f"/Media/2. Videos/{id_dialog}_{msg.id}.mp4", progress_callback=callback)
													os.remove(path+f"/Media/2. Videos/{id_dialog}_{msg.id}.jpg")
										elif media.document.mime_type == "image/webp":
											print("")
										elif media.document.mime_type == "video/webp":
											print("")
										elif media.document.mime_type == "application/x-tgsticker":
											print("")
						else:
							print(msg)
				except Exception as a:
					if str(a).find("disk is full") != -1:
						print("Недостаточно памяти на диске!")
						sys.exit()
					print(a)

			# Получить все файлы с фото
			await client.get_dialogs(limit=None)
			path_photo = path+'/Media/1. Photos/'
			path_video = path+'/Media/2. Videos/'
			path_round_video = path+'/Media/3. Round Videos/'

			# Фотографии
			onlyfiles = [f for f in listdir(path_photo) if isfile(join(path_photo, f))]
			photo_messages = []
			id_dialog = 0
			for file in onlyfiles:
				if file.find(".jpg") != -1:
					if id_dialog != "ID"+file.split("_")[0]:
						if len(photo_messages) > 0:
							await download_media(path, int(photo_messages[0].split("ID")[1]), await client.get_messages(await client.get_entity(int(photo_messages[0].split("ID")[1])), ids=photo_messages[1:]))
						photo_messages = []
						id_dialog = "ID"+file.split("_")[0]
						photo_messages.append("ID"+file.split("_")[0])
						photo_messages.append(int(file.split("_")[1].split(".")[0]))
					else:
						photo_messages.append(int(file.split("_")[1].split(".")[0]))

			# Видео
			onlyfiles = [f for f in listdir(path_video) if isfile(join(path_video, f))]
			#onlyfiles = onlyfiles + [f for f in listdir(path_round_video) if isfile(join(path_round_video, f))]
			messages_video = []
			id_dialog = 0
			for file in onlyfiles:
				if file.find(".jpg") != -1:
					if id_dialog != "ID"+file.split("_")[0]:
						if len(messages_video) > 0:
							await download_media(path, int(messages_video[0].split("ID")[1]), await client.get_messages(await client.get_entity(int(messages_video[0].split("ID")[1])), ids=messages_video[1:]))
						messages_video = []
						id_dialog = "ID"+file.split("_")[0]
						messages_video.append("ID"+file.split("_")[0])
						messages_video.append(int(file.split("_")[1].split(".")[0]))
					else:
						messages_video.append(int(file.split("_")[1].split(".")[0]))


	else:
		print("Отсутствует файл telethon.session или tdata")

loop.run_until_complete(main())
