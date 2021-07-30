"""
Кузнецов Юрий, гр.05370
Лабораторная №5 - LSB
	Число изменяемых бит - 1
"""

from PIL import Image
from math import sqrt
import random

#Функция перевода в двоичную систему счисления
#n - число, k - кол-во разрядов
def ToBinary(n, k):
	res = ""
	while n != 0:
		res = str(n % 2) + res
		n //= 2
	#дополняем незначащими нулями до k символов
	while len(res) < k:
		res = str(0) + res
	return res

#Функция перевода в 10-ую систему счисления
def ToDecimal(s):
	res = 0
	for i in range(len(s)):
		res += int(s[len(s) - 1 - i]) * (2 ** i)
	return res

#Функция, генерирующая случайное сообщение
#Размер сообщения задается размерами изображения
def GenerateRandomMessage(txt_source, img_source):
	f = open(txt_source, 'w')
	img = Image.open(img_source)
	width, height = img.size
	for i in range(width * height):
		#По биту на каждый из каналов RGB
		for j in range(3):
			f.write(str(random.randint(0, 1)) + ' ')
		f.write('\n')
	f.close()
	img.close()
	return txt_source

#Функция получения изображения всех LSB данного изображения
#Если LSB = 1, то в канал записываем 255, иначе 0
def GetLSBs(source):
	img = Image.open(source)

	width, height = img.size
	full_size = width * height
	pixels_in_percent = int(full_size / 100)
	old_percents = 0

	done = '█'
	wait = '_'

	for i in range(width):
		for j in range(height):
			cords = i, j
			pixel = list(img.getpixel(cords))
			for k in range(3):
				n = pixel[k]
				n = ToBinary(n, 8)
				if int(n[7]):
					n = 255
				else:
					n = 0
				pixel[k] = n
			img.putpixel(cords, tuple(pixel))

			#визуализация загрузки
			current_pixel = (i + 1) * height + j + 1
			if current_pixel % pixels_in_percent == 0:
				val = int(current_pixel / pixels_in_percent)
				qnt_of_done = int(val / 5)
				print('\rLoad: |' + done * qnt_of_done + wait * (20 - qnt_of_done) + '| - ' + str(val) + '%', end='')

	print()
	path = "LSB_" + source
	img.save(path, "PNG")
	return path

def GetMSBs(source):
	img = Image.open(source)
	width, height = img.size
	for i in range(width):
		for j in range(height):
			cords = i, j
			pixel = list(img.getpixel(cords))
			for k in range(3):
				n = pixel[k]
				n = ToBinary(n, 8)
				if int(n[0]):
					n = 255
				else:
					n = 0
				pixel[k] = n
			img.putpixel(cords, tuple(pixel))
	path = "MSB_" + source
	img.save(path, "PNG")
	return path

#Запись в изображение
#На вход подается бинарное сообщение, разбитое на блоки по 3 бита
#Каждый блок вписывается в один пиксель путем замены последнего бита в каждом из RGB-каналов
def WriteMessage(txt_source, img_source):
	f = open(txt_source, 'r')
	msg = f.read().split('\n')
	f.close()

	img = Image.open(img_source)
	width, height = img.size
	
	full_size = width * height
	pixels_in_percent = int(full_size / 100)
	old_percents = 0

	done = '█'
	wait = '_'

	for i in range(width):
		for j in range(height):
			cords = i, j
			pixel = list(img.getpixel(cords))
			msg_split = list(map(str, msg[i * height + j].split(' ')))
			for k in range(3):
				n = ToBinary(pixel[k], 8)
				n = n[:7] + msg_split[k]
				pixel[k] = ToDecimal(n)
			img.putpixel(cords, tuple(pixel))

			#визуализация загрузки
			current_pixel = (i + 1) * height + j + 1
			if current_pixel % pixels_in_percent == 0:
				val = int(current_pixel / pixels_in_percent)
				qnt_of_done = int(val / 5)
				print('\rLoad: |' + done * qnt_of_done + wait * (20 - qnt_of_done) + '| - ' + str(val) + '%', end='')

	print()
	path = "Crypt_" + txt_source[:-4] + "_" + img_source
	img.save(path, "PNG")
	return path

#Функция считывает последние биты с каждого канала каждого пикселя в файл result.txt
#Запись в файл происходит в том же формате, что и во входном файле:
#Строки из 3-х чисел [0; 1], разделенных пробелами
def ReadMessage(source):
	f = open("result.txt", 'w')
	img = Image.open(source)
	width, height = img.size

	full_size = width * height
	pixels_in_percent = int(full_size / 100)
	old_percents = 0

	done = '█'
	wait = '_'

	for i in range(width):
		for j in range(height):
			cords = i, j
			pixel = list(img.getpixel(cords))
			for k in range(3):
				n = ToBinary(pixel[k], 8)
				f.write(str(n[7]) + ' ')
			f.write('\n')

			#визуализация загрузки
			current_pixel = (i + 1) * height + j + 1
			if current_pixel % pixels_in_percent == 0:
				val = int(current_pixel / pixels_in_percent)
				qnt_of_done = int(val / 5)
				print('\rLoad: |' + done * qnt_of_done + wait * (20 - qnt_of_done) + '| - ' + str(val) + '%', end='')

	print()
	img.close()
	f.close()

def MergePics(source, secret):
	img = Image.open(source)
	noise = Image.open(secret)
	width, height = img.size
	for i in range(width):
		for j in range(height):
			cords = i, j
			img_pixel = list(img.getpixel(cords))
			noise_pixel = list(noise.getpixel(cords))
			for k in range(3):
				n = ToBinary(img_pixel[k], 8)
				if noise_pixel[k] == 255:
					n = n[:7] + str(1)
				else:
					n = n[:7] + str(0)
				img_pixel[k] = ToDecimal(n)
			img.putpixel(cords, tuple(img_pixel))
	img.save(source[:len(source)-4] + '_' + secret, "PNG")
	noise.close()	

#GenerateRandomMessage("msg.txt", "source.png")
#WriteMessage("msg.txt", "source.png")
#WriteMessage("meaningful_msg.txt", "source.png")
#ReadMessage("Crypt_meaningful_msg_source.png")
#GetLSBs("Crypt_msg_source.png")
#GetLSBs("source_beach.png")
#GetLSBs("Crypt_msg_source.png")
#GetLSBs("Crypt_meaningful_msg_source.png")
#GetLSBs("source_lips.png")
GetLSBs("source_GP.png")
GetLSBs("source_che.png")
GetLSBs("source_lips.png")