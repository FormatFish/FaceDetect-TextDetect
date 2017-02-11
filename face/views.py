#coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
import requests
import json
import base64
import time
from PIL import Image , ImageDraw
# Create your views here.

def index(reqest):
	return render_to_response('index.html', {'flag':False})

def getData(reqest):
    img = reqest.FILES['image']
    filename = time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.png'
    folder = "static/img/"
    with open(folder + filename , 'wb+') as des:
        des.write(img.read())

    pathToFile = folder + filename

    type = reqest.POST['type']
    
    if type == 'face':
        info = getFaceInfo(pathToFile)
        print info

        # 人脸数目
        result_num = info['result_num']
        if result_num >= 1:
            left = int(info['result'][0]['location']['left'])
            top = int(info['result'][0]['location']['top'])
            width = int(info['result'][0]['location']['width'])
            height = int(info['result'][0]['location']['height'])

            image = Image.open(pathToFile)
            draw = ImageDraw.ImageDraw(image)
            draw.rectangle((left , top , left + width , top + height))
            image.save(pathToFile)

            age = float(info['result'][0]['age'])
            beauty = info['result'][0]['beauty']
            expression = info['result'][0]['expression']
            map = {0: u'不笑', 1:u'微笑',2:u'大笑'}
            expr = map[expression]
            glasses = info['result'][0]['glasses']
            if glasses == 1:
                glass = u'戴眼镜'
            else:
                glass = u'不戴眼镜'

            gender = info['result'][0]['gender']

            if gender == 'male':
                gender = u'男'
            else:
                gender = u'女'


            faceshape = info['result'][0]['faceshape'][0]['type']
            map2 = {'square':u'大方脸' , 'triangle':u'瓜子脸', 'oval':u'椭圆脸','heart':u'心形脸','round':u'圆脸'}


            context = {'result_num': result_num , 'age': age , 'beauty':beauty , 'expr':expr , 'glasses':glass , 
                    'gender':gender , 'faceshape':faceshape , 'flag':True , 'filename':filename ,'error':False}

            return render_to_response('index.html' , context = context)
        else:
            #assert False
            return render_to_response('index.html' , {'error': True , 'info':u'抱歉！没有识别到人脸' , 'filename':filename , 'flag':True})
    else:
        info = getTextInfo(pathToFile)
        wordsRes = info['words_result']
        words = wordsRes[0]['words']
        location = wordsRes[0]['location']

        captha = Image.open(pathToFile)
        draw = ImageDraw.ImageDraw(captha)
        x = location['left']
        y = location['top']
        w = location['width']
        h = location['height']
        draw.rectangle((x , y , x + w , y + h) , outline = 'black')

        chars = wordsRes[0]['chars']
        charMap = {}
        for item in chars:
            charMap[item['char']] = item['location']
        for item in charMap.values():
            x = item['left']
            y = item['top']
            w = item['width']
            h = item['height']
            draw.rectangle((x , y , x + w , y + h) , outline = 'blue')

        captha.save(folder + 'temp.png')
        context = {'flag': False , 'istext':True , 'words':words , 'filename':filename}
        return render_to_response('index.html' , context = context)

def getAccessToken():
    clientId = "YOUR Client ID"
    clientSecret = "YOUR API KEY"
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id="+ clientId + "&client_secret=" + clientSecret
    access = requests.post(url)

    token = json.loads(access.text)

    return token['access_token']

def getTextInfo(filename):
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    baseUrl = u"https://aip.baidubce.com/rest/2.0/ocr/v1/general?access_token=" + getAccessToken()
    data = {'image': base64.b64encode(open(filename , 'rb').read())}
    data['recognize_granularity'] = 'small'
    data['detect_direction'] = True
    data['vertexes_location'] = True

    r = requests.post(baseUrl , data = data , headers = headers)
    info = json.loads(r.text)
    '''
    wordsRes = info['words_result']
    words = wordsRes[0]['words']
    location = wordsRes[0]['location']

    captha = Image.open(filename)
    draw = ImageDraw.ImageDraw(captha)
    x = location['left']
    y = location['top']
    w = location['width']
    h = location['height']
    draw.rectangle((x , y , x + w , y + h) , outline = 'black')

    chars = wordsRes[0]['chars']
    charMap = {}
    for item in chars:
        charMap[item['char']] = item['location']
    for item in charMap.values():
        x = item['left']
        y = item['top']
        w = item['width']
        h = item['height']
        draw.rectangle((x , y , x + w , y + h) , outline = 'blue')
    '''
    return info

def getFaceInfo(filename):
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    baseUrl = u"https://aip.baidubce.com/rest/2.0/face/v1/detect?access_token=" + getAccessToken()
    data = {'image': base64.b64encode(open(filename , 'rb').read()) , 'face_fields':'age,beauty,expression,faceshape,gender,glasses,landmark,race,qualities'}
    r = requests.post(baseUrl , data = data , headers = headers)

    info = json.loads(r.text)

    return info


