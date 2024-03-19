
import cv2, time, math, sys, pysrt, getopt
from PIL import Image, ImageDraw, ImageFont
import numpy as np

Help = """
OPTIONS:
	--Help		: Shows this help page
	--Text		: Text to be displayed on video. Use double quotes(Example "text") to enter the text.
	--Font		: Path of font file to be used (.ttf file)
	--Input		: Path/name of the input video file
	--Output	: Path/name of the output video file
	--Locations	: Location locations of the text 
						("x1,y1,x2,y2,x3,y3,x4,y4" or "x,y,height,width,angle"
						or "3/4" or "0.75")
	--Background	: Background rectangle around the text
						True => Black background
						False => No background
						A number value => translucent background
	--Subtitles	: Path/name of the subtitles file (.srt file)

USAGE:
	python3 main.py input_video.mp4 text/subtitles [location] [background(True/False)]
OR
	python3 main.py input_video.mp4 "text" "x1,y1,x2,y2,x3,y3,x4,y4" background

	Replace x1,y1,x2,y2,x3,y3,x4,y4 with the corner locations of the subtitle (x1,y1), (x2,y2), (x3,y3) and (x4,y4).
	For example:
		python3 main.py input_video.mp4 "How are you?" "20, 150, 330, 230, 20, 350, 330, 330" True

OR
	python3 main.py input_video.mp4 "Text to overlay" "x,y,height,width,angle" background

	Replace x,y,height,width,angle with location of rectangle of the subtitle
	For example:
		python3 main.py input_video.mp4 "How are you?" "20, 150, 330, 250, -10" True

OR
	python3 main.py input_video.mp4 subtitles.srt "x1,y1,x2,y2,x3,y3,x4,y4" background
OR
	python3 main.py input_video.mp4 subtitles.srt location.txt background
OR
	python3 main.py input_video.mp4 "text or subtitle file only"
OR
	python3 main.py -i input_video.mp4 -o output_video.mp4 -l "x1,y1,x2,y2,x3,y3,x4,y4" -t "text"
OR
	python3 main.py --Input input_video.mp4 --Output output_video.mp4 --Location locations.txt
	                --Subtitles subtitles.srt --Background False


	"""

""" This function takes four (x,y) points of a frame as [(x1, x2), (x3, x4), (x5, x6), (x7, x8)].
	It finds a rectangle that align with the four points.
    Then it return x,y location of top left of the rectangle and the height, width and angle of the rectangle.
    """
def get_rect_from_four_corners(corners):
	k = sorted(corners)
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


""" This function takes any type of location info and 
	returns the location info of a rectangle in the format (x,y,height,width,angle).
	It can take a number or equation like 3/4,
	then it centers the x axis and ratio that equation with height for the y-axis.
	It can take x1,y1,x2,y2,x3,y3,x4,y4 four corner points of a rectangle.
	It can take x,y,height,width,angle of a rectangle and returns the same.
	And by default it centers the x-axis, and 3/4 the y-axis for the location of rectrangle,
	and width of rectangle is in golden ratio.
"""
def get_rect_from_location(location):
	if "/" in location and len(location)<20 and not any(c.isalpha() for c in location):
		location = eval(location)
		if location <= 1:
			location *= height
		else:
			location = 3/4*height
		location = int(location)
	elif len(location) < 5:
		location = int(3/4*height)
	location = tuple(map( int, str(location).replace(" ", "").split(",")))
	if len(location) == 5:
		return location
	elif len(location) == 8:
		a1, a2, a3, a4, a5, a6, a7, a8 = location
		return get_rect_from_four_corners([(a1, a2), (a3, a4), (a5, a6), (a7, a8)])
	else: 
		rect_width = int(width/1.618)
		rect_height = min(int(height/6), int(rect_width/4))
		return int(width/2 - rect_width/2), int(location[0] - rect_height/2), rect_width, rect_height, 0

font_path='Arial-Unicode-Regular.ttf'
font_color = "white"
locations = "0"
video_path = "input_video.mp4"
output_path = 'output_video.mp4'
background = 255
input_used = False

argumentList = sys.argv[1:]
options = "h:i:o:p:t:d:f:b:s:"
long_options = ["Help", "Input", "Output", "Locations", "Text", "Font", "Background", "Subtitles"]
arguments, values = getopt.getopt(argumentList, options, long_options)
for currentArgument, currentValue in arguments:
	if currentArgument in ("-h", "--Help"):
		print (Help)
		exit()
	elif currentArgument in ("-i", "--Input"):
		video_path = currentValue
		input_used = True
	elif currentArgument in ("-o", "--Output"): output_path = currentValue
	elif currentArgument in ("-l", "--Locations"): locations = currentValue
	elif currentArgument in ("-t", "--Text"): text = currentValue 
	elif currentArgument in ("-f", "--Font"): font_path = currentValue
	elif currentArgument in ("-b", "--Background"): background = currentValue
	elif currentArgument in ("-s", "--Subtitles"): text = currentValue
if input_used:
	pass
elif len(sys.argv) == 5:  # for five arguments
	try:
		video_path = sys.argv[1]
		locations = sys.argv[2]
		text = sys.argv[3]
		background = sys.argv[4]
	except:
		pass
elif len(sys.argv) == 4:  # for four arguments
	video_path = sys.argv[1]
	text = sys.argv[2]
	x = sys.argv[3]  # checking if argument 3 defines location or background
	if "," in x or ".txt" in x.lower():
		locations = x
	else:
		background = x
elif len(sys.argv) == 3:  # for three arguments
	video_path = sys.argv[1]
	text = sys.argv[2]
elif len(sys.argv) < 3:
	print(Help)
	exit()

subtitles = None
if text[-4:] == ".srt":
	subtitles = pysrt.open(text)  # loads subtitles

try:  # fix value of background rectangle transparency/darkness
	background = float(str(background).strip())
	if background <= 1: background *= 255
	background = int(background)
except:
    if "F" in background.upper():
        background = 0
    else:
        background = 255

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
result = cv2.VideoWriter(output_path,  
						 cv2.VideoWriter_fourcc(*'mp4v'),
						 fps, (width, height))


# load locations.txt file and creating a dictionary with all subtitles indexes to there locations
if locations[-4:] == ".txt":
	with open(locations) as f:
		locations_txt = f.read()
	locations = "txt"
	location = {}
	for line in locations_txt.replace(" ", "").split("\n"):
	    if not line: continue
	    try:
	    	# extract location within the brackets in location.txt file
	        current_location = line.split('(', 1)[1].split(')')[0]
	    except:
	        continue
	    # removing the brackets and location in a line of subtitles.txt file, only keeping indexes of subtitles
	    subtitle_indexes = (line.split('(')[0]+','+line.split(')')[1]).split(",")
	    for index in subtitle_indexes:
	        if not index: continue
	        if "to" in index:  # range index like "5 to 10"
	            start_index,end_index = index.split("to")
	            try:
	                start_index,end_index = int(start_index),int(end_index)
	            except:
	                print("Warning:", start_index, "to", end_index)
	                continue
	            for k in range(min(start_index,end_index),max(start_index,end_index)+1):
	                location[k] = current_location
	        else:  # index is a number and not a range
	            try:
	                location[int(index)] = current_location
	            except:
	                print("Warning:", index)
	                continue
else:
	rect_x, rect_y, rect_width, rect_height, rect_angle = get_rect_from_location(locations)

if "/" not in font_path and "\\" not in font_path:
	font_path = "Fonts/" + font_path

ERROR_COUNT = 0
previous_text = ""
previous_font_size = ""
percent = 0
ii = 0
times =[]
while(cap.isOpened()):
	t0 = time.time()
	ii+=1
	if subtitles:
		try:
			subtitle = subtitles.at(seconds=ii/fps)[0]
			text = subtitle.text.replace("\n", " ")
		except:
			text = None
	timed = 0 
	ret, frame = cap.read()
	if ret == True:
		if int(ii/length*100) > percent:
			print(f"{ii/length*100:.0f}% ", end="", flush=True)
			percent+=1

		if text:
			if locations == "txt":
				try:
					current_location = location[subtitle.index]
				except:
					current_location = '0'
				try:
					rect_x, rect_y, rect_width, rect_height, rect_angle = get_rect_from_location(current_location)
				except:
					ERROR_COUNT += 1
					if ERROR_COUNT == 2:
						print("ERROR in location", current_location, ", it's subtitle number:",
							   subtitle.index, "and subtitle is:", subtitle.text)
					current_location = '0'
					rect_x, rect_y, rect_width, rect_height, rect_angle = get_rect_from_location(current_location)
			im = Image.new("RGBA", (rect_width, rect_height), (0,0,0,0))
			draw = ImageDraw.Draw(im)

			if previous_text == text:
				font_size = previous_font_size
			else:
				font_size = rect_height # height//2  # Max font size
				font = ImageFont.truetype(font_path, height//2)
				while font_size > 1:
					bbox = draw.textbbox((rect_width//2, rect_height//2), text, font=font, anchor="mm")
					if bbox[0] > 0 and bbox[1] > 0 and bbox[2] < rect_width and bbox[3] < rect_height:
						break
					font_size -= 1
					font = font.font_variant(size=font_size)
				previous_text = text
				previous_font_size = font_size

			draw.rounded_rectangle((0, 0,rect_width-1, rect_height-1), fill=(0,0,0,background), outline=(0,0,0,background),
                           width=1, radius=rect_height//8)
			draw.text((rect_width//2, rect_height//2), text, font=font, fill="white", anchor="mm")
			im = im.rotate(rect_angle, expand=1)

			image = Image.fromarray(frame)
			image.paste(im, (rect_x, rect_y), im)
			frame = np.asarray(image)

		result.write(frame)
	else:
		print('\nCompleted')
		break
	if ii<101:
		times.append(time.time()-t0)
	if ii==100:
		times.remove(max(times))
		print("\nTotal time =>", int(length*0.8*sum(times)/len(times)), "seconds") # 0.7
result.release() 
cap.release() 
cv2.destroyAllWindows()
