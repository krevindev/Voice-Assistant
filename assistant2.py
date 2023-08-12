from array import array
from xml.dom import INDEX_SIZE_ERR
import speech_recognition as sr
import pyttsx3
from bs4 import BeautifulSoup
import requests
import pyttsx3
import os
from playsound import playsound
import time
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('volume', 1)
engine.setProperty('rate', 190)

curr_dir = os.getcwd()

print(curr_dir)
def speakText(text):
    #engine.say(text)
    engine.say('<pitch middle="-100">'+text+'</pitch>')
    engine.runAndWait()

def inputVoice():
    with sr.Microphone() as source:
        r = sr.Recognizer()
        audio = r.listen(source)
        try:
            return  r.recognize_google(audio)
        except sr.UnknownValueError:
            print('???')
        except sr.RequestError:
            speakText('Sorry, my speech service is down, I cannot recognize any voice at the moment')
        except sr.ConnectionResetError:
            speakText('Sorry, the connection to my API has been reset, I cannot recognize any voice at the moment')

# TOMORROW'S FORECAST
def tomFC(indx):
    td_url = 'https://weather.com/en-PH/weather/tenday/l/908832d8b5b7b2c020af2365d85ee982961af09fa163499312273fa9961a5c19'
    td_html_text = requests.get(td_url).text
    td_soup = BeautifulSoup(td_html_text, 'lxml')
    td_cards = td_soup.find_all('details', class_ = 'DaypartDetails--DayPartDetail--1up3g Disclosure--themeList--25Q0H')
    next_date = td_cards[indx].find('span', class_ = 'DailyContent--daypartDate--2A3Wi')
    td_location = td_soup.find('span', class_ ='LocationPageTitle--PresentationName--1QYny').text
    days_dict = {
            'sun': 'sunday',
            'mon': 'monday',
            'tue': 'tuesday',
            'wed': 'wednesday',
            'thu': 'thursday',
            'fri': 'friday',
            'sat': 'saturday'
            }
    fcast = {
        'location': td_location,
        'date': next_date.text.split(' '),  
        'day': {
            'narrative': td_cards[indx].find_all('p', class_ = 'DailyContent--narrative--hplRl')[0].text.split('.')[0],
            'temperature': td_cards[indx].find_all('span', class_ = 'DailyContent--temp--3d4dn')[0].text
        },
        'night':{
            'narrative': td_cards[indx].findAll('p', class_ = 'DailyContent--narrative--hplRl')[1].text.split('.')[0],
            'temperature': td_cards[indx].find_all('span', class_ = 'DailyContent--temp--3d4dn')[1].text
        }
    }
    day = 'tomorrow' if indx == 1 else days_dict[fcast['date'][0].lower()]
    
    print(f"{fcast['date'][0]} {fcast['date'][1]}, in {td_location}")
    print(f"DAY:\t{fcast['day']['narrative']}\n\t{fcast['day']['temperature']}")
    print(f"NIGHT:\t{fcast['night']['narrative']}\n\t{fcast['night']['temperature']}")

    speakText("According to Weather.com")
    speakText(f"The weather forecast for {day} {fcast['date'][1]} in {fcast['location']}...")
    speakText(f"At daytime, {fcast['day']['narrative']} at {fcast['day']['temperature']} temperature")
    speakText(f"At night time, {fcast['night']['narrative']} at {fcast['night']['temperature']} temperature")
# TODAY'S FORECAST
def todayFC():
    url = 'https://weather.com/en-PH/weather/today/l/908832d8b5b7b2c020af2365d85ee982961af09fa163499312273fa9961a5c19'

    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    current_weather = soup.find('div', class_ = 'CurrentConditions--phraseValue--2Z18W').text
    current_temp = soup.find('span', class_ = 'CurrentConditions--tempValue--3a50n').text
    feels_like = soup.find('span', class_ = 'TodayDetailsCard--feelsLikeTempValue--Cf9Sl').text
    location = soup.find('h1', class_ = 'CurrentConditions--location--kyTeL').text
    print(f"\n{location}\n{current_weather}:{current_temp}\nFeels like:{feels_like}")
    speakText("According to Weather.com")
    speakText('The weather for today in '+location+' is '+current_weather+" at "+current_temp)
    speakText('However, due to other relevant environmental data, the temperature outside today feels like '+feels_like)
# DEFINITIONS
def dictionary(searchword):
    url = f'https://www.merriam-webster.com/dictionary/{searchword}'

    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    box = soup.find('span', class_ = 'dt')

    if box != None:
        wordinfo = {
        'word': box.find('span', class_ = 'dtText').text.split(':')[1],
        'examples': box.find_all('span', class_ = 'ex-sent')
        }
        
        print(searchword.upper()+" means\n\""+wordinfo['word']+"\"")
        speakText(searchword.upper()+" means\""+wordinfo['word']+"\"")

        if len(wordinfo['examples']) >= 1:
            print("Example:\n")
            speakText("For example")
            for example in wordinfo['examples']:
                
                print(example.text)
                print("")
                speakText(example.text)
                if example.text.replace(' ','')[0] == '-':
                    speakText('that is according to '+example.text)
                    os.system('pause')
        else:
            pass
    else:
        print(searchword+" not found")
        speakText("Sorry I don't know what "+searchword+" means")

# TIME TODAY
time_categ = ''
def getTime():
    
    t_url = "https://dayspedia.com/time/ph/Manila/"
    html_text = requests.get(t_url).text
    soup = BeautifulSoup(html_text, 'lxml')
    hours = soup.find('div', class_ = 'time__hours').text.replace('\n', '').replace(' ', '')
    
    minutes = soup.find('div', class_ = 'time__minutes').text.replace('\n', '').replace(' ', '')
    #seconds = soup.find('div', class_ = 'time__seconds').text.replace('\n', '').replace(' ','')

    return {
        'hours': (int(hours)-12) if int(hours) > 12 else hours,
        'minutes':minutes,
        #'seconds': seconds,
        'ampm': 'pm' if int(hours) >= 12 else 'am'}
def replaceMulti(rstring, to_replace, replacement):
    for c in to_replace:
        rstring = rstring.replace(c, replacement)
    return rstring
def cleanTitle(title_str):
    junk_str = ['720p','1080p','hd']
    for i in range(1000,2022):
        if title_str.__contains__(str(i)):
            year = i
            title_str = title_str.split(str(i))[0].replace('.', ' ')+" "+str(year)
    for j in junk_str:
        if title_str.__contains__(j):
            title_str = title_str.split(str(j))[0].replace('.', ' ')

    return title_str
    
# PLAY MOVIE
def playMovie():
    movies_path = "C:"
    speakText('Give a unique keyword for the video')
    while True:
        os.system('cls')
        print("Keyword: ", end=' ')
        try:
            title = inputVoice()
            if title == None:
                speakText('Sorry, can you repeat?')
            else:
                print(title+"?")
                break
        except(TypeError):
            speakText('Sorry, I did not get that')
            print('Sorry, can you repeat?')

    # Scanning...
    results = []
    speakText("Searching for "+title+", please wait")
    for (dir_path, dir_names, file_names) in os.walk(movies_path):
        os.system('cls')
        print(f"Scanning movies with {title}, please wait")
        print('')
        for file in file_names:
            print(file)
            if file.lower().__contains__(title):
                found = dir_path+"\\"+file
                if found.split('\\')[-1].split('.')[-1] in ['mkv','mp4','avi']:
                    results.append(found)

    os.system('cls')
    #os.chdir(vlc_path)
    if len(results) > 0:
        if len(results) == 1:
            for result in results:
                result_string = str(result.split('\\')[-1].split('.')[0:-1])
                result_string = replaceMulti(result_string,[',',']','[','\''], '')
                if result.split('.')[-1] in ['mp4','avi', 'mkv']:
                    print('Playing: '+cleanTitle(result_string))
                    speakText('Now playing, '+cleanTitle(result_string))
                    os.system(f'("{result}" & videoplay.py )')
                else:
                    results.remove(result)
        elif len(results) > 1:
            
            for i in range(len(results)):
                print(str(i+1)+':'+results[i].split('\\')[-1]+'"')

            print(f"I found {len(results)} results")
            speakText(f"I found {len(results)} results")
            speakText("Which of these would you like to play?")
            

            strnums = ['first','second', 'third','fourth','fifth','fifth','sixth','seventh']
            
            while True:
                try:
                    print(">", end=' ')
                    no = str(inputVoice())
                    print(no+"?")
                    if no.lower() in strnums:
                        no = int(strnums.index(no))
                        result_str = results[no].split('\\')[-1]
                        result_str = replaceMulti(result_str,['['], '')
                        print(cleanTitle(result_str))
                        speakText('Now Playing: '+cleanTitle(result_str))
                        os.system('\"'+results[no]+'\" ')
                        break
                    else:
                        speakText('Can you repeat?')
                except(TypeError):
                    print("Error")
                    continue
    else:
        print("Videos with keyword '"+title+"' Not Found!")
        speakText(title+' not found')


            
weather_today = ['check the weather today',
                         'check the weather for today',
                         'what is the weather today',
                         'what is the weather forecast for today',
                         'what\'s the weather today']
weather_tomorrow = ['check the weather tomorrow',
                    'check the weather for tomorrow',
                    'what is the weather tomorrow',
                    'what is the weather forecast for tomorrow',
                    'what is the weather for tomorrow',
                    'what\'s the weather tomorrow',
                    'what\'s the weather forecast for tomorrow',
                    'what is the weather forecast tomorrow']


# CALL SCRAPER COMMANDS
def callScraper(command):
    playsound('ok1.mp3')
    voice_data = command
    if voice_data in weather_today:
        todayFC()
    elif voice_data in weather_tomorrow:
        tomFC(1)
    elif voice_data[0:4] == 'open':
        site = voice_data.split(' ')[-1]
        speakText(f'opening {site}.com, please wait')
        os.system(f'start brave {site}.com')
    elif voice_data[0:5] == 'close':
        app_name = voice_data.split(' ')[-1]
        speakText(f'locating and terminating {app_name} application')
        os.system(f'taskkill /im {app_name}.exe /f')
    elif voice_data.__contains__('search for'):
        keyword = voice_data.split(' ')[-1]
        url = f'https://www.google.com/search?q={keyword}&source=lnms&tbm=isch&sa=X&ved=2ahUKEwi8yIf967H4AhXIA94KHaVTAdUQ_AUoAXoECAIQAw&biw=1366&bih=699&dpr=1'
        os.system(f'start brave {url}')
    elif voice_data.__contains__('what is the definition of'):
        word = voice_data.replace('what is the definition of', '')
        dictionary(word)
    elif voice_data == 'what time is it':
        print(f"The time today is {getTime()['hours']}:{getTime()['minutes']} {getTime()['ampm']}")
        speakText(f"The time today is {getTime()['hours']}:{getTime()['minutes']}{getTime()['ampm'].replace('', ' ')} in the {time_categ}")
    elif voice_data in ['play a video', 'play video', 'play a movie']:
        playMovie()
    elif voice_data == 'hello':
        speakText('hi')
    elif voice_data == 'exit':
        speakText('goodbye')
        quit()
    elif voice_data == 'sleep':
        speakText('alright')
    elif voice_data == 'close yourself':
        speakText('alright, goodbye')
        quit()
    else:
        speakText(f'did you just say {voice_data}? I don\'t know how to respond to that')

# greetings on startup
try:
    ampm = getTime()['ampm'].lower()
    hour = int(getTime()['hours'])
    playsound('ok2.mp3')
    if  ampm == 'pm':
        if hour == 12 or hour == 1:
            speakText('good noon')
            time_categ = 'noon'
        elif hour >= 2 and hour <= 5:
            speakText('good afternoon')
            time_categ = 'afternoon'
        else:
            speakText('good evening')
            time_categ = 'evening'
    elif ampm == 'am':
        speakText('good morning')
        time_categ = 'morning'
except:
    speakText('')


while True:
    os.system('cls')
    print('Speak Now')
    print('...')

    voice_data = inputVoice()
    voice_data = '' if voice_data == None else voice_data


    if voice_data == 'voice test':
        playsound('ok2.mp3')
        print("Yes, I'm listening")
        speakText('yes, I\'m listening')
        callScraper(inputVoice())
    elif voice_data == 'exit':
        speakText('alright, goodbye!')
        playsound('ok2.mp3')
        quit()
    elif voice_data.split(' ')[0] in ['friday', 'creeper', 'reeper', 'paper', 'aper']:
        command = voice_data.replace(voice_data.split(' ')[0], '')
        command = command[1:len(command)]
        print(command)
        callScraper(command)
    else:
        print(voice_data)