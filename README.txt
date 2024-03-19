

Video Overlay adds text/subtitles to a video.






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









# CVXOPT-1.3.2