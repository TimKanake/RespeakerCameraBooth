from picamera import PiCamera
from respeaker3 import MicArray
from threading import Thread
import time
import sys
import cv2
import os
import argparse


# Configure the ArgParser
parser = argparse.ArgumentParser(description="Specify arguments to override default settings.")
parser.add_argument('-facedetect', default=False, help='Specifies if recording should start upon face detection',
					type=bool)
parser.add_argument('-length', help='Amount of time to record in Seconds', default=30, type=int)

args = parser.parse_args()

camera = PiCamera()


def setup_time():
	try:
		import ntplib
		client = ntplib.NTPClient()
		response = client.request('pool.ntp.org')
		print time.localtime(response.tx_time)
		os.system('date ' + time.strftime('%m%d%H%M%Y.%S', time.localtime(response.tx_time)))
	except:
		print('Could not sync with time server.')
	print('Done.')


def detect_face(image_path='foo.jpeg', casc_path = 'haarcascade_frontalface_default.xml'):
	face_cascade = cv2.CascadeClassifier(casc_path)
	face_found = False
	global camera
	if camera.closed:
			camera = PiCamera()
	print 'finding faces in frame...'
	while not face_found:
		capture_image()
		image = cv2.imread(image_path)
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		# Detect faces in the image
		faces = face_cascade.detectMultiScale(
			gray,
			scaleFactor=1.1,
			minNeighbors=5,
			minSize=(30, 30)
			)
		if len(faces) > 0:
			face_found = True
			camera.close()
		else:
			print 'removing image'
			os.remove(image_path)
	for (x, y, w, h) in faces:
		cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
	print 'A Face Has Been Found!!'
	return


def capture_image(image_name='foo.jpeg'):
	global camera
	if camera.closed:
		print 'Camera is opening...'
		camera = PiCamera()
	camera.capture(image_name)


# capture video file

def capture_video(video_length=10, recording_name='foo.h264', start_time=time.time()):
	global camera
	if camera.closed:
		print 'Camera is opening...'
		camera = PiCamera()
	while True:
		if time.time() >= start_time+1:
			print 'Time started recording video: ', time.time()
			camera.start_recording(recording_name)
			camera.wait_recording(video_length)
			camera.stop_recording()
			print 'finished recording video ', time.time()
			break


def record_video_with_audio(length=60, start_delay=8.0, on_face_detect=False):
	sd = MicArray()
	if on_face_detect:
		detect_face()
		start_time = time.time()+start_delay
	else:
		start_time = time.time()+start_delay
	t1 = Thread(target=capture_video, kwargs={'start_time': start_time, 'video_length':length})
	t2 = Thread(target=sd.run, kwargs={'start_time':start_time, 'audio_length':length})
	t1.start()
	t2.start()
	t1.join()
	t2.join()


if __name__ == '__main__':
	length = args.length
	on_face_detect = args.facedetect
	record_video_with_audio(length,on_face_detect=on_face_detect)
