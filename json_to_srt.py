
import json
from datetime import timedelta

def fix_comma_precision(time):
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
    c = {} # temp
    c['start'] = words_dict[0]['Offset']
    c['end'] = words_dict[0]['Offset']+words_dict[0]['Duration']
    c['words'] = ''
    for i in words_dict:
        if len(c['words'] + i['Word']) < max_characters:
            if i['Word'] == 'i': i['Word'] = 'I'
            c['words'] += ' ' + i['Word']
            c['end'] = i['Offset']+i['Duration']
        else:
            c['words'] = c['words'].strip()
            subtitles_list.append(c)
            c = {}
            c['start'] = i['Offset']
            c['end'] = i['Offset']+i['Duration']
            c['words'] = i['Word']
    subtitles_list.append(c)

    subtitles = ""
    index_count = 0
    for c in subtitles_list:
        index_count+=1
        subtitles += str(index_count)+'\n'+fix_comma_precision(c['start'])+' --> '+fix_comma_precision(c['end'])+'\n'+c['words']+'\n\n'
    return subtitles


if __name__ == '__main__':
    

    input_file = 'words.json'
    output_file = 'words_subtitles.srt'

    with open(input_file) as f:
        words = json.load(f)

    subtitles = parse(words)

    with open(output_file, 'w') as f:
        f.write(subtitles)