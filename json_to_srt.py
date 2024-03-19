
import json, argparse
from datetime import timedelta

def fix_comma_precision(time):  # format the time in HH:MM:SS,SSS
    HHMMSS = str(timedelta(seconds=time/10000000))
    if '.' in HHMMSS:
        b1,b2 = HHMMSS.split(".")
        time = b1+','+b2[:3]
    else:
        time = HHMMSS+',000'
    return time

def parse(words_dict):
    subtitles_list = []
    max_characters = 25
    max_time_difference = 5000000  # 0.5 seconds
    c = {} # temp
    c['start'] = words_dict[0]['Offset']
    c['end'] = words_dict[0]['Offset']+words_dict[0]['Duration']
    c['words'] = ''
    for i in words_dict:
        if len(c['words'] + i['Word']) < max_characters and i['Offset']-c['end'] < max_time_difference: # join the words if less then max_characters and less than max_time_difference
            if i['Word'] == 'i': i['Word'] = 'I'
            c['words'] += ' ' + i['Word']
            c['end'] = i['Offset']+i['Duration']
        else: # create a new subtitle
            c['words'] = c['words'].strip()
            subtitles_list.append(c)
            c = {}
            c['start'] = i['Offset']
            c['end'] = i['Offset']+i['Duration']
            c['words'] = i['Word']
    subtitles_list.append(c)

    # Subtitles are created now its time to format them correctly.
    subtitles = ""
    index_count = 0
    for c in subtitles_list:
        index_count+=1
        # format the subtitles
        subtitles += str(index_count)+'\n'+fix_comma_precision(c['start'])+' --> '+fix_comma_precision(c['end'])+'\n'+c['words']+'\n\n'
    return subtitles


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()

    parser.add_argument("-j", "--json", default="words.json")
    parser.add_argument("-s", "--srt", default="words_subtitles.srt")

    args = parser.parse_args()

    input_file = args.json
    output_file = args.srt

    with open(input_file) as f:
        words = json.load(f)

    subtitles = parse(words)
    
    with open(output_file, 'w', encoding="utf-8") as f:
        f.write(subtitles)