import certifi
import json
import math
from datetime import datetime, timedelta, date
from urllib.parse import urlencode, quote_plus
from xml.etree.ElementTree import PI

import requests
import urllib3
from django.shortcuts import render
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()
)

#certifi 문제?
#여러 변수를 받기 위한 함수
def index(request):
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"

    serviceKeyDecoded = "a1+ueyWqfojp8TLmo3eE/fyZKd23AQldV28JjM7odiUWiqkSyv/3G//rOxAeJLxdf74/0b5TYuXUBn0//pywOw=="  # 공공데이터 포털에서 생성된 본인의 서비스 키를 복사 / 붙여넣기
    # 공데이터 포털에서 제공하는 서비스키는 이미 인코딩된 상태이므로, 디코딩하여 사용해야 함 (최근부터 디코딩 키 제공)

    now = datetime.now()

    today = datetime.today().strftime("%Y%m%d")
    y = date.today() - timedelta(days=1)
    yesterday = y.strftime("%Y%m%d")
    nx = 60  # 위도와 경도를 x,y좌표로 변경
    ny = 127

    if now.minute < 45:  # base_time와 base_date 구하는 함수 (30분단위의 자료를 매시각 45분이후 호출하므로 다음과 같은 if 설정)
        if now.hour == 0:
            base_time = "2330"
            base_date = yesterday
        else:
            pre_hour = now.hour - 1

            if pre_hour < 10:
                base_time = "0" + str(pre_hour) + "30"
            else:
                base_time = str(pre_hour) + "30"
            base_date = today
    else:
        if now.hour < 10:
            base_time = "0" + str(now.hour) + "30"
        else:
            base_time = str(now.hour) + "30"
    base_date = today
    queryParams = '?' + urlencode({quote_plus('serviceKey'): serviceKeyDecoded, quote_plus('base_date'): base_date,
                                   quote_plus('base_time'): base_time, quote_plus('nx'): nx, quote_plus('ny'): ny,
                                   quote_plus('dataType'): 'json',
                                   quote_plus('numOfRows'): '60'})  # 페이지로 안나누고 한번에 받아오기 위해 numOfRows=60으로 설정해주었다

    # 값 요청 (웹 브라우저 서버에서 요청 - url주소와 파라미터)
    res = requests.get(url + queryParams, verify=False)

    items = res.json().get('response').get('body').get('items')
    # print(items)# 테스트

    weather_data = dict()

    for item in items['item']:
        # 기온
        if item['category'] == 'T1H':
            weather_data['tmp'] = item['fcstValue']
        # 습도
        if item['category'] == 'REH':
            weather_data['hum'] = item['fcstValue']
        # 하늘상태: 맑음(1) 구름많은(3) 흐림(4)
        if item['category'] == 'SKY':
            weather_data['sky'] = item['fcstValue']
        # 1시간 동안 강수량
        if item['category'] == 'RN1':
            weather_data['rain'] = item['fcstValue']

    tmp = {'weather': weather_data}
    return render(request, 'weather/index.html',tmp)


def mapToGrid(request):

    lat = float(request.POST['lat'])
    lon = float(request.POST['lon'])

    Re = 6371.00877  ##  지도반경
    grid = 5.0  ##  격자간격 (km)
    slat1 = 30.0  ##  표준위도 1
    slat2 = 60.0  ##  표준위도 2
    olon = 126.0  ##  기준점 경도
    olat = 38.0  ##  기준점 위도
    xo = 210 / grid  ##  기준점 X좌표
    yo = 675 / grid  ##  기준점 Y좌표
    first = 0

    PI = math.asin(1.0) * 2.0
    DEGRAD = PI/ 180.0
    RADDEG = 180.0 / PI


    re = Re / grid
    slat1 = slat1 * DEGRAD
    slat2 = slat2 * DEGRAD
    olon = olon * DEGRAD
    olat = olat * DEGRAD

    sn = math.tan(PI * 0.25 + slat2 * 0.5) / math.tan(PI * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(PI * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(PI * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    first = 1

    ra = math.tan(PI * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > PI :
        theta -= 2.0 * PI
    if theta < -PI :
        theta += 2.0 * PI
    theta *= sn
    x = (ra * math.sin(theta)) + xo
    y = (ro - ra * math.cos(theta)) + yo
    grid_x = int(x + 1.5)
    grid_y = int(y + 1.5)

    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"

    serviceKeyDecoded = "a1+ueyWqfojp8TLmo3eE/fyZKd23AQldV28JjM7odiUWiqkSyv/3G//rOxAeJLxdf74/0b5TYuXUBn0//pywOw=="  # 공공데이터 포털에서 생성된 본인의 서비스 키를 복사 / 붙여넣기
    # 공데이터 포털에서 제공하는 서비스키는 이미 인코딩된 상태이므로, 디코딩하여 사용해야 함

    now = datetime.now()

    today = datetime.today().strftime("%Y%m%d")
    y = date.today() - timedelta(days=1)
    yesterday = y.strftime("%Y%m%d")
    nx = grid_x
    ny = grid_y

    if now.minute < 45:  # base_time와 base_date 구하는 함수 (30분단위의 자료를 매시각 45분이후 호출하므로 다음과 같은 if 설정)
        if now.hour == 0:
            base_time = "2330"
            base_date = yesterday
        else:
            pre_hour = now.hour - 1

            if pre_hour < 10:
                base_time = "0" + str(pre_hour) + "30"
            else:
                base_time = str(pre_hour) + "30"
            base_date = today
    else:
        if now.hour < 10:
            base_time = "0" + str(now.hour) + "30"
        else:
            base_time = str(now.hour) + "30"
    base_date = today
    queryParams = '?' + urlencode({quote_plus('serviceKey'): serviceKeyDecoded, quote_plus('base_date'): base_date,
                                   quote_plus('base_time'): base_time, quote_plus('nx'): nx, quote_plus('ny'): ny,
                                   quote_plus('dataType'): 'json',
                                   quote_plus('numOfRows'): '60'})  # 페이지로 안나누고 한번에 받아오기 위해 numOfRows=60으로 설정해주었다

    # 값 요청 (웹 브라우저 서버에서 요청 - url주소와 파라미터)
    res = requests.get(url + queryParams, verify=False)
    res_json = json.loads(res.content)
    print(res_json)
    items = res_json["response"]['body']['items']

    weather_data = dict()

    for item in items['item']:
        # 기온
        if item['category'] == 'T1H':
            weather_data['tmp'] = item['fcstValue']


    current_tmp = {'weather': weather_data}



    return render(request, 'weather/latlot.html', current_tmp)


def start(request):

    return render(request,'weather/maptogrid.html')