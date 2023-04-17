import json
import math
import urllib
from datetime import datetime, timedelta, date
from urllib.parse import urlencode, quote_plus
import requests

from django.shortcuts import render


def result(request):
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
    DEGRAD = PI / 180.0
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
    if theta > PI:
        theta -= 2.0 * PI
    if theta < -PI:
        theta += 2.0 * PI
    theta *= sn
    x = (ra * math.sin(theta)) + xo
    y = (ro - ra * math.cos(theta)) + yo
    grid_x = int(x + 1.5)
    grid_y = int(y + 1.5)

    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

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
            base_time = "2300"
            base_date = yesterday
        else:
            pre_hour = now.hour - 1

            if pre_hour < 10:
                base_time = "0" + str(pre_hour) + "00"
            else:
                base_time = str(pre_hour) + "00"
            base_date = today
    else:
        if now.hour < 10:
            base_time = "0" + str(now.hour) + "00"
        else:
            base_time = str(now.hour) + "00"
        base_date = today
    print(base_time,base_date)

    current_time = base_time[0:2] + '00'

    queryParams={'serviceKey':serviceKeyDecoded, 'pageNo':'1','numOfRows':'1000','dataType':'JSON','base_date':base_date,'base_time':base_time,'nx':nx,'ny':ny}

    # 값 요청 (웹 브라우저 서버에서 요청 - url주소와 파라미터)

    res = requests.get(url,params=queryParams,verify=False)
    res_json = json.loads(res.content)
    print(res_json)
    items = res_json["response"]['body']['items']

    weather_data = dict()

    for item in items['item']:

        if item['category'] == 'TMP' and item['baseDate'] == base_date and item['fcstTime'] == current_time :
            weather_data['tmp'] = item['fcstValue']
        if item['category'] == 'POP' and item['baseDate'] == base_date and item['fcstTime'] == current_time :
            weather_data['percent'] = item['fcstValue']
        if item['category'] == 'REH' and item['baseDate'] == base_date and item['fcstTime'] == current_time :
            weather_data['hum'] = item['fcstValue']

        if item['category'] == 'SKY'  and item['baseDate'] == base_date and item['fcstTime'] == current_time :
            if item['fcstValue'] == '1':
                weather_data['sky'] = '맑음'
                weather_data['img'] = 'free-icon-sun-7755606.png'
            elif item['fcstValue'] == '3':
                weather_data['sky'] = '구름많음'
                weather_data['img'] = 'free-icon-bright-9477120.png'
            elif item['fcstValue'] == '4':
                weather_data['sky'] = '흐림'
                weather_data['img'] = 'free-icon-rainy-7198663.png'

        if item['category'] == 'TMX' and item['baseDate'] == base_date :
            weather_data['max'] = item['fcstValue']

        if item['category'] == 'TMN' and item['baseDate'] == base_date :
            weather_data['min'] = item['fcstValue']

        if item['category'] == 'WSD' and item['baseDate'] == base_date:
            weather_data['wind'] = item['fcstValue']

    weather_data['time'] = now
    current_tmp = {'weather': weather_data}

    return render(request, 'weather/index.html', current_tmp)

def start(request):

    return render(request,'weather/maptogrid.html')

