import pyaudio
import Queue
import numpy as np
from gcc_phat import gcc_phat
import math
import audioop
import time
import wave
from collections import deque
from pixels import pixels
import csv
import sys
import os
import ntplib


SOUND_SPEED = 340
MIC_DISTANCE_4 = 0.081
MAX_TDOA_4 = MIC_DISTANCE_4 / float(SOUND_SPEED)
DIRECTIONS_QUEUE = Queue.Queue()
AUDIO_QUEUE = Queue.Queue()

try:
	client = ntplib.NTPClient()
	response = client.request('pool.ntp.org')
	print time.localtime(response.tx_time)
	os.system('date ' + time.strftime('%m%d%H%M%Y.%S', time.localtime(response.tx_time)))
except:
	print('Could not sync with time server.')

print('Done.')


class MicArray(object):
	def __init__(self, rate=16000, channels=4, chunk_size=None):
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = channels
		self.RATE = rate
		self.CHUNK = chunk_size if chunk_size else 1024
		self.pyaudio_instance = pyaudio.PyAudio()
		self.SILENCE_LIMIT = 5
		self.PREV_AUDIO = 0.5
		self.THRESHOLD = 800
		self.queue = Queue.Queue()

	# Need to sort out setting threshold for 4 mic array
	def setup_mic(self, num_samples=50):
		# Gets average audio intensity of your mic sound.
		print "Getting intensity values from mic."
		device_index = None
		for i in range(self.pyaudio_instance.get_device_count()):
			dev = self.pyaudio_instance.get_device_info_by_index(i)
			name = dev['name'].encode('utf-8')
			if dev['maxInputChannels'] == self.CHANNELS:
				device_index = i
				break

		if device_index is None:
			raise Exception('can not find input device with {} channel(s)'.format(self.CHANNELS))

		p = pyaudio.PyAudio()
		stream = p.open(
			input=True,
			format=self.FORMAT,
			channels=self.CHANNELS,
			rate=self.RATE,
			frames_per_buffer=self.CHUNK,
			input_device_index=device_index,
		)
		values = [
			math.sqrt(abs(audioop.avg(stream.read(self.CHUNK), 4)))
			for x in range(num_samples)]
		values = sorted(values, reverse=True)
		r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
		print " Finished getting intensity values from mic"
		stream.close()
		p.terminate()
		return r

	# Save recorded speech to a wav file.
	def save_speech(self, data):
		p = self.pyaudio_instance
		filename = int(time.time())
		data = ''.join(data)
		wf = wave.open('./audio_files/' + filename + '.wav', 'wb')
		wf.setnchannels(4)
		wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
		wf.setframerate(self.RATE)
		wf.writeframes(data)
		wf.close()


	def run(self, audio_length=10, start_time=time.time()):
		p = self.pyaudio_instance
		device_index = None
		print 'Setting up pyaudio ...'
		for i in range(self.pyaudio_instance.get_device_count()):
			dev = self.pyaudio_instance.get_device_info_by_index(i)
			name = dev['name'].encode('utf-8')
			if dev['maxInputChannels'] == self.CHANNELS:
				print('Using {}'.format(name))
				device_index = i
				break

		if device_index is None:
			raise Exception('can not find input device with {} channel(s)'.format(self.CHANNELS))

		stream = p.open(
			input=True,
			format=self.FORMAT,
			channels=self.CHANNELS,
			rate=int(self.RATE),
			frames_per_buffer=int(self.CHUNK),
			input_device_index=device_index,
		)
		print "* Listening mic..."
		audio2send = []
		cur_data = ''
		rel = int(self.RATE / self.CHUNK)
		slid_win = deque(maxlen=self.SILENCE_LIMIT * rel)

		# Prepend audio from 0.5 seconds before noise was detected
		prev_audio = deque(maxlen=self.PREV_AUDIO * rel)
		started = False
		response = []
		if time.time() >= start_time():
			while time.time()-start_time < audio_length:
				try:
					cur_data = stream.read(self.CHUNK)
					slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 3))))
					audio2send.append(cur_data)
				except KeyboardInterrupt:
					self.save_speech(audio2send)

		self.save_speech(audio2send)
		print "* Done recording...Exiting..."
		stream.close()
		p.terminate()


if __name__ == '__main__':
	pass
