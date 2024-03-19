
import cv2, time, math, sys, pysrt, getopt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from textwrap import wrap


def four_points_to_rectangle(points):
	k = sorted(points)
	Z = [(0, 1, k[0], k[1]), (1, 2, k[1], k[2]), (2, 3, k[2], k[3]),
		 (0, 2, k[0], k[2]), (1, 3, k[1], k[3]),
		 (0, 3, k[0], k[3])]
	a,maxa = Z[0], math.dist(Z[0][2],Z[0][3])
	for i,j,x,y in Z[1:]:
		if math.dist(x,y) > maxa:
			a,maxa = (i,j,x,y), math.dist(x,y)
	f = [0, 1, 2, 3]
	f.remove(a[0])
	f.remove(a[1])
	tuple(f)
	rect_width = math.dist(k[a[0]], k[f[0]])
	rect_height = math.dist(k[a[0]], k[f[1]])
	if rect_width < rect_height:
		rect_width, rect_height = rect_height, rect_width
		f.reverse()
	x = min(k[0][0], k[1][0], k[2][0], k[3][0])
	y = min(k[0][1], k[1][1], k[2][1], k[3][1])
	angle = np.rad2deg(np.arctan2(k[a[0]][1] - k[f[0]][1], k[a[0]][0] - k[f[0]][0]))*-1
	if angle > 90:
		angle -= 180
	if angle < -90:
		angle += 180
	return x, y, int(rect_width), int(rect_height), angle



DEBUG = False
font_path='Fonts/OpenSans.ttf'
font_color = "white"
points = 0
video_path = "input_video.mp4"
output_path = 'output_video.avi'
background = 255

Help = """
OPTIONS:
	--Help		: Show this help page
	--Text		: Text to be displayed over video (use double quotes(") to enter the text)
	--Font		: Path of font to be used (.ttf file)
	--Input		: Path/name of the input video file
	--Debug		: To print debug info (True or False)
	--Output	: Path/name of the output video file
	--Points	: Location points of the text ("x1,y1,x2,y2,x3,y3,x4,y4" or "x,y,height,width,angle")
	--Background	: Background of the text (True or False or some value)
	--Subtitles	: Path to subtitles file (.srt file)

USAGE:
	python3 main.py input_video.mp4 "x1,y1,x2,y2,x3,y3,x4,y4" "text" background
OR
	python3 main.py input_video.mp4 "x,y,height,width,angle" "Text to overlay" background
OR
	python3 main.py input_video.mp4 "x1,y1,x2,y2,x3,y3,x4,y4" subtitles.srt background
OR
	python3 main.py -i input_video.mp4 -o output_video.mp4 -p "x1,y1,x2,y2,x3,y3,x4,y4" -t "text"
	"""
argumentList = sys.argv[1:]
options = "h:i:o:p:t:d:f:b:s:"
long_options = ["Help", "Input", "Output", "Points", "Text", "Debug", "Font", "Background", "Subtitles"]
arguments, values = getopt.getopt(argumentList, options, long_options)
for currentArgument, currentValue in arguments:
	print()
	if currentArgument in ("-h", "--Help"):
		print (Help)
		exit()
	elif currentArgument in ("-i", "--Input"):  video_path = currentValue
	elif currentArgument in ("-o", "--Output"): output_path = currentValue
	elif currentArgument in ("-p", "--Points"): points = currentValue
	elif currentArgument in ("-t", "--Text"): text = currentValue 
	elif currentArgument in ("-d", "--Debug"): DEBUG = currentValue
	elif currentArgument in ("-f", "--Font"): font_path = currentValue
	elif currentArgument in ("-b", "--Background"): background = currentValue
	elif currentArgument in ("-s", "--Subtitles"): subtitles_path = currentValue
if len(sys.argv) == 5:
	try:
		video_path = sys.argv[1]
		points = sys.argv[2]
		text = sys.argv[3]
		background = sys.argv[4]
	except:
		pass
elif len(sys.argv) < 5:
	print(Help)
	exit()

subs = None
if text[-4:] == ".srt":
	subs = pysrt.open(text)

try:
	background = float(str(background).strip())
	if background <= 1: background *= 255
	background = int(background)
except:
    if "F" in background.upper():
        background = 0
    else:
        background = 255

points = tuple(map( int, points.replace(" ", "").split(",")))
if len(points) == 5:
	rect_x, rect_y, rect_width, rect_height, rect_angle = points
else:
	a1, a2, a3, a4, a5, a6, a7, a8 = points
	points = [(a1, a2), (a3, a4), (a5, a6), (a7, a8)]
	rect_x, rect_y, rect_width, rect_height, rect_angle = four_points_to_rectangle(points)

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
result = cv2.VideoWriter(output_path,  
						 cv2.VideoWriter_fourcc(*'MJPG'), #H264
						 fps, (width, height))

autofit_text = True
font_size = 40 # '7%'
if "/" not in font_path and "\\" not in font_path:
	font_path = "Fonts/" + font_path
if(type(font_size) == str):
	if font_size[-1] == '%':
		font_size = int(int(font_size[:-1])*height/100)
	elif font_size[-2:] == 'px':
		font_size = int(font_size[:-2])
font = ImageFont.truetype(font_path, font_size)

x = rect_width//2
y = rect_height//2

percent = 0
ii = 0
times =[]
while(cap.isOpened()):
	t0 = time.time()
	ii+=1
	if subs:
		try:
			text = subs.at(seconds=ii/fps)[0].text.replace("\n", " ")
		except:
			text = None
	timed = 0 
	ret, frame = cap.read()
	if ret == True:
		if int(ii/length*100) > percent:
			print(f"{ii/length*100:.0f}% ", end="", flush=True)
			percent+=1

		if text:
			im = Image.new("RGBA", (rect_width, rect_height), (0,0,0,background))
			draw = ImageDraw.Draw(im)

			while font_size > 1:
				bbox = draw.textbbox((x, y), text, font=font, anchor="mm")
				if bbox[0] > 0 and bbox[1] > 0 and bbox[2] < rect_width and bbox[3] < rect_height:
					break
				font_size -= 1
				font = font.font_variant(size=font_size)

			draw.text((x, y), text, font=font, fill="white", anchor="mm")
			im = im.rotate(rect_angle, expand=1)

			image = Image.fromarray(frame)
			image.paste(im, (rect_x, rect_y), im)

			if DEBUG:
				draw = ImageDraw.Draw(image)
				draw.rectangle((a1, a2, a1+1, a2+3), outline="blue")
				draw.rectangle((a3, a4, a3+1, a4+3), outline="blue")
				draw.rectangle((a5, a6, a5+1, a6+3), outline="blue")
				draw.rectangle((a7, a8, a7+1, a8+3), outline="blue")
			frame = np.asarray(image)

		result.write(frame)
	else:
		print('\nCompleted')
		break
	times.append(length*(time.time()-t0))
	if ii == 10:
		print("\nTotal time =>", int(sum(times)/len(times)), "seconds")
result.release() 
cap.release() 
cv2.destroyAllWindows()
