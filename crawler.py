from urllib.request import urlopen, Request
import json
from tqdm import tqdm
from time import sleep


def urlget(url: str):
    return json.loads(urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'})).read().decode())


def convert(data):
    return data['station_train_code'], data['train_no'], data['from_station'], data['to_station']


def get_list(date: str):
    result = set()
    letters = ['', 'C', 'D', 'G', 'K', 'L', 'S', 'T', 'Y', 'Z']
    for letter in tqdm(letters, position=0, leave=False):
        for number in tqdm(range(1, 100), position=1, leave=False):
            while True:
                try:
                    url = f'https://search.12306.cn/search/v1/train/search?keyword={
                        letter}{number}&date={date}'
                    result.update(map(convert, urlget(url)["data"]))
                    break
                except Exception as e:
                    sleep(5)
        json.dump(sorted(result), open(
            'list.json', 'w'), indent=4, ensure_ascii=False)
    return sorted(result)


def get_timetable():
    trains = json.load(open('list.json'))
    result = json.load(open('trains_ori.json'))
    t = 0
    for train in tqdm(trains):
        try:
            b: bytes = urlopen('https://shike.gaotie.cn/checi.asp?checi=' +
                               train[0]).read()
            s = b.decode('gbk', errors='ignore')
            s = s.split(
                '<table width="960"   border="0" align="center" cellpadding="0" cellspacing="1" bgcolor="#66CCFF">')[1]
            s = s.split('</table>')[0].replace('\r',
                                               '').replace('\n', '').replace(' ', '')
            l = []
            for i in s.split('>'):
                if i and not i.startswith('<'):
                    l.append(i.split('<')[0])
            ll = []
            for i in range(11, len(l), 11):
                ll.append(l[i+1:i+11])
            result.append([train[0], ll])
            t += 1
            if t % 100 == 0:
                json.dump(result, open('trains_ori.json', 'w'),
                          ensure_ascii=False, separators=(',', ':'))
        except:
            print(train[0])
    json.dump(result, open('trains_ori.json', 'w'),
              ensure_ascii=False, separators=(',', ':'))


def str2time(s):
    h, m = map(int, s.split(':'))
    return h*60+m


def arrange():
    trains = json.load(open('trains_ori.json'))
    result = {}
    repeat = 0
    illegal = 0
    for train in tqdm(trains):
        ll = []
        try:
            lasttime = lastprice = -1
            for stop in train[1]:
                stop[0] = stop[0][:-1]
                del stop[2]
                if stop[1] == '始发站':
                    stop[1] = stop[2]
                    stop[6] = '0'
                if stop[2] == '终点站':
                    stop[2] = stop[1]
                stop[3] = int(stop[3])-1
                arrive = str2time(stop[1])+stop[3]*1440
                leave = str2time(stop[2])+stop[3]*1440
                if arrive > leave:
                    leave += 1440
                assert arrive > lasttime
                lasttime = leave
                p = []
                for i in stop[6:]:
                    p.extend(i.split('/'))
                del stop[4:]
                price = min(map(float, filter(lambda x: x != '-', p)))
                assert price > lastprice
                lastprice = price
                stop.append(int(price) if price == int(
                    price) else round(price, 1))
                ll.append(stop)
            ll = tuple(tuple(i) for i in ll)
            if ll in result:
                repeat += 1
            else:
                result[ll] = train[0]
        except:
            illegal += 1
    print(f'有效：{len(result)} 重复：{repeat} 非法：{illegal}')
    final_result = []
    for stop, name in result.items():
        final_result.append([name, stop])
    final_result.sort(key=lambda x: (x[0][0], len(x[0]), x[0]))
    json.dump(final_result, open('trains_fin.json', 'w'),
              ensure_ascii=False, separators=(',', ':'))


def json2txt():
    trains = json.load(open('trains_fin.json'))
    with open('trains.txt', 'w') as f:
        print(len(trains), file=f)
        for train in tqdm(trains):
            print(file=f)
            print(train[0], len(train[1]), file=f)
            for station in train[1]:
                print(*station, file=f)


date = '20241211'

print('Step 1/3：获取车次列表')
get_list(date)

print('Step 2/3：获取时刻表')
get_timetable()

print('Step 3/3：整理导出')
arrange()
json2txt()
