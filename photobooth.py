from picamera import PiCamera
import time
import cv2
from respeaker import MicArray

camera = PiCamera()


# capture image

def capture_image(image_name='foo.jpg'):
	global camera
	camera.start_preview()
	time.sleep(2)
	camera.capture(image_name)


# capture video file

def capture_video(recording_time=10, recording_name='foo.h264', start_time=time.time()):
	global camera
	if time.time() >= start_time:
		camera.start_recording(recording_name)
		camera.wait_recording(recording_time)
		camera.stop_recording()

def record_video_with_audio(length=10):
	sd = MicArray()
	start_time = time.time() + 10
	capture_video(start_time=start_time,recording_time=length)
	sd.run(start_time=start_time, audio_length=length)

