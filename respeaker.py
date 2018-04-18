import pyaudio
import Queue
import time
import wave


class MicArray(object):
	def __init__(self, rate=44100, channels=4, chunk_size=2048):
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = channels
		self.RATE = rate
		self.CHUNK = chunk_size if chunk_size else 1024
		self.pyaudio_instance = pyaudio.PyAudio()
		self.queue = Queue.Queue()

	# Save recorded speech to a wav file.
	def save_speech(self, data):
		p = self.pyaudio_instance
		filename = str(time.time())
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
		for i in range(p.get_device_count()):
			dev = p.get_device_info_by_index(i)
			name = dev['name'].encode('utf-8')
			if dev['maxInputChannels'] == self.CHANNELS:
				print('Using {}'.format(name))
				device_index = i
				break

		if device_index is None:
			raise Exception('can not find input device with {} channel(s)'.format(self.CHANNELS))
		audio2send = []
		cur_data = ''
		rel = self.RATE / self.CHUNK
		while True:
			if time.time() >= start_time:
					print 'Opening stream ', time.time()
					stream = p.open(
							input=True,
							format=self.FORMAT,
							channels=self.CHANNELS,
							rate=int(self.RATE),
							frames_per_buffer=self.CHUNK,
							input_device_index=device_index,)
					print 'Stream is now open ', time.time()

					cur_data = stream.read(self.CHUNK)
					for i in range(0, int(rel * audio_length)):
							try:
									cur_data = stream.read(self.CHUNK, False)
							except IOError:
									continue

							audio2send.append(cur_data)
							print i
					print 'Finished recording audio ', time.time()
					self.save_speech(audio2send)
					return


if __name__ == '__main__':
	sd = MicArray()
	time_var = time.time()
	sd.run(start_time=time_var)
