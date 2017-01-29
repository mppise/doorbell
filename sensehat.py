#
import sys#, time
from sense_hat import SenseHat

# variables
sense = SenseHat()
sense.set_rotation(90)
O = [0, 0, 0] # Off
R = [255, 0, 0]  # Red
Y = [255, 255, 0]  # Yellow
W = [255, 255, 255]  # White
G = [0, 255, 0]	# Green

def showNotification(status):
	if status == "warn":
		# visuals warn
		visual = [
		O, O, O, Y, Y, O, O, O,
		O, O, O, Y, Y, O, O, O,
		O, O, Y, W, W, Y, O, O,
		O, O, Y, W, W, Y, O, O,
		O, Y, O, W, W, O, Y, O,
		O, Y, O, O, O, O, Y, O,
		Y, O, O, W, W, O, O, Y,
		Y, Y, Y, Y, Y, Y, Y, Y
		]
		sense.set_pixels(visual)

	elif status == "error":
		# visuals error
		visual = [
		R, R, R, R, R, R, R, R,
		R, O, O, O, O, O, O, R,
		R, O, O, O, O, O, O, R,
		R, O, O, O, O, O, O, R,
		R, O, O, O, O, O, O, R,
		R, O, O, O, O, O, O, R,
		R, O, O, O, O, O, O, R,
		R, R, R, R, R, R, R, R
		]
		sense.set_pixels(visual)

	elif status == "ok":
		# visuals ok
		visual = [
		G, G, G, G, G, G, G, G,
		G, O, O, O, O, O, O, G,
		G, W, O, O, O, O, W, G,
		G, 0, W, W, W, W, O, G,
		G, 0, W, W, W, W, O, G,
		G, W, O, O, O, O, W, G,
		G, O, O, O, O, O, O, G,
		G, G, G, G, G, G, G, G
		]
		sense.set_pixels(visual)

	elif status == "blip":
		# visuals blip
		visual = [
		G, O, O, Y, Y, O, O, G,
		O, O, O, R, R, O, O, O,
		O, O, O, O, O, O, O, O,
		R, Y, O, W, W, O, Y, R,
		R, Y, O, W, W, O, Y, R,
		O, O, O, O, O, O, O, O,
		O, O, O, R, R, O, O, O,
		G, O, O, Y, Y, O, O, G
		]
                sense.set_pixels(visual)

	elif status == "clear":
		# visuals clear all
		sense.clear();

        elif status == "message":
		sense.clear();
		sense.show_message(str(sys.argv[2]))


if len(sys.argv) > 1:
	switch = sys.argv[1]
	showNotification(switch)
else:
	print("Switch not specified : 'ok | warn | error | clear | blip'")
	sense.clear()
	
