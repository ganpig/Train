from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
from subprocess import *
from math import log, tan, e, pi, hypot
import json
import os

try:
    from sys import _MEIPASS
except:
    _MEIPASS = '.'

geo_ori = json.load(open(os.path.join(_MEIPASS, 'geo.json')))
geo = {}
for station in geo_ori:
    geo[station['name']] = (station['lng'], station['lat'])

root = Tk()
root.title('铁路路径规划工具')
root.geometry('1200x600')
root.resizable(False, False)
root.iconbitmap(os.path.join(_MEIPASS, 'train.ico'))

cv = Canvas(root, width=840, height=600)
img = PhotoImage(file=os.path.join(_MEIPASS, 'map.png'))
cv.create_image(0, 0, anchor=NW, image=img)
cv.place(x=0, y=0)

Label(root, text='出发地：').place(x=840, y=20)
depInput = Entry(root, width=15)
depInput.insert(0, '北京')
depInput.place(x=890, y=20)

Label(root, text='目的地：').place(x=1010, y=20)
desInput = Entry(root, width=15)
desInput.insert(0, '上海')
desInput.place(x=1060, y=20)

depPreVar = IntVar(value=1)
depPreInput = Checkbutton(root, text='前缀匹配', variable=depPreVar)
depPreInput.place(x=890, y=45)

desPreVar = IntVar(value=1)
desPreInput = Checkbutton(root, text='前缀匹配', variable=desPreVar)
desPreInput.place(x=1060, y=45)

Label(root, text='出发时间：').place(x=840, y=70)
hInput = Combobox(root, values=[str(i).zfill(2) for i in range(24)], width=3)
hInput.set('08')
hInput.place(x=900, y=70)
Label(root, text=':').place(x=945, y=70)
mInput = Combobox(root, values=[str(i*5).zfill(2) for i in range(12)], width=3)
mInput.set('00')
mInput.place(x=953, y=70)

Label(root, text='换乘预留时间：').place(x=1010, y=70)
ttimeInput = Combobox(root, values=[str(i*5) for i in range(2, 13)], width=3)
ttimeInput.set('15')
ttimeInput.place(x=1095, y=70)
Label(root, text='分钟').place(x=1140, y=70)

Label(root, text='最多换乘次数：').place(x=840, y=100)
tcountInput = Combobox(root, values=[str(i) for i in range(11)], width=3)
tcountInput.set('2')
tcountInput.place(x=925, y=100)

Label(root, text='最多方案数：').place(x=980, y=100)
pcountInput = Combobox(root, values=[str(i) for i in range(1, 21)], width=3)
pcountInput.set('10')
pcountInput.place(x=1050, y=100)

progress = Progressbar(root)
progress.place(x=840, y=130, width=340)
progress['maximum'] = 1

pTable = Treeview(root, columns=['']*4, show='headings', selectmode='browse')


def pSort(col, reverse):
    l = [(pTable.set(x, col), x) for x in pTable.get_children()]
    try:
        l.sort(reverse=reverse, key=lambda x: float(x[0]))
    except:
        l.sort(reverse=reverse)
    for i, (v, x) in enumerate(l):
        pTable.move(x, '', i)
    for i in range(4):
        pTable.heading(i, command=lambda i_=i: pSort(
            i_, not reverse if i_ == col else False))


pTable.heading(0, text='方案', command=lambda: pSort(0, True))
pTable.heading(1, text='换乘次数', command=lambda: pSort(1, False))
pTable.heading(2, text='到达时间', command=lambda: pSort(2, True))
pTable.heading(3, text='总票价', command=lambda: pSort(3, False))
pTable.column(0, width=40, anchor=N)
pTable.column(1, width=100, anchor=N)
pTable.column(2, width=100, anchor=N)
pTable.column(3, width=100, anchor=N)
pTable.place(x=840, y=160)

tTable = Treeview(root, height=8, columns=[
                  '']*5, show='headings', selectmode='none')
tTable.heading(0, text='车次')
tTable.heading(1, text='上车时间')
tTable.heading(2, text='下车时间')
tTable.heading(3, text='上车站')
tTable.heading(4, text='下车站')
tTable.column(0, width=50, anchor=N)
tTable.column(1, width=80, anchor=N)
tTable.column(2, width=80, anchor=N)
tTable.column(3, width=65, anchor=N)
tTable.column(4, width=65, anchor=N)
tTable.place(x=840, y=400)


tot = 0
p = None
ready = True
plans = []


def readline():
    return p.stdout.readline().strip()


def time2str(x):
    t = ''.join(chr(0x200B+ord(i)-48) for i in bin(x)[2:].zfill(20))
    d = x//1440
    x %= 1440
    if d == 0:
        s = ''
    elif d == 1:
        s = '次日'
    else:
        s = f'第{d+1}天'
    return t+s+f'{x//60:02d}:{x % 60:02d}'


def submit():
    global ready, tot, p
    if not ready:
        return

    departure = depInput.get()
    destination = desInput.get()
    depPre = str(depPreVar.get())
    desPre = str(desPreVar.get())
    h = hInput.get()
    m = mInput.get()
    minTransTime = ttimeInput.get()
    maxTransCount = tcountInput.get()
    maxPlanCount = pcountInput.get()

    try:
        h = int(h)
        m = int(m)
        assert 0 <= h <= 23 and 0 <= m <= 59
        startTime = str(h*60+m)
        assert int(minTransTime) >= 0
        assert int(maxTransCount) >= 0
        assert int(maxPlanCount) > 0
    except:
        showwarning('输入有误', '请检查输入内容！')
        return

    p = Popen([os.path.join(_MEIPASS, 'train.exe'), departure, destination, depPre, desPre, startTime,
              minTransTime, maxTransCount, maxPlanCount], cwd=_MEIPASS, stdout=PIPE, universal_newlines=True)
    tot = int(readline())
    ready = False
    cv.delete(ALL)
    cv.create_image(0, 0, anchor=NW, image=img)
    pTable.delete(*pTable.get_children())
    tTable.delete(*tTable.get_children())
    track()


def track():
    global ready, plans
    now = int(readline())
    progress['value'] = now/tot
    if now == tot:
        ready = True
        n = int(readline())
        plans = []
        for _ in range(n):
            k, price = readline().split()
            k = int(k)
            price = float(price)
            path = []
            for __ in range(k):
                train, onTime, offTime, *stops = readline().split()
                path.append((train, int(onTime), int(offTime), stops))
            plans.append((path, price))
        for i, (path, price) in enumerate(plans):
            pTable.insert('', END, str(i), values=(
                i+1, len(path)-1, time2str(path[-1][2]), price))
    else:
        root.after(1, track)


def Mercator(N):
    return log(tan((90+N)*pi/360), e)


def calXY(E, N):
    L = 73.5
    R = 135
    U = Mercator(53.5)
    D = Mercator(18.1)
    N = Mercator(N)
    X = (E-L)/(R-L)*820
    Y = (N-U)/(D-U)*600
    return X, Y


def pShow():
    if not pTable.selection():
        return
    path = plans[pTable.item(pTable.selection()[0])['values'][0]-1][0]
    tTable.delete(*tTable.get_children())
    for train, onTime, offTime, stops in path:
        tTable.insert('', END, values=(train, time2str(onTime),
                      time2str(offTime), stops[0], stops[-1]))
    Stops = [path[0][3][0]]
    for train, onTime, offTime, stops in path:
        Stops.extend(stops[1:])
    Stops = [i for i in Stops if i in geo]
    flag = True
    while flag:
        flag = False
        for i in range(len(Stops)-2, 0, -1):
            e0, n0 = geo[Stops[i-1]]
            e1, n1 = geo[Stops[i]]
            e2, n2 = geo[Stops[i+1]]
            if min(hypot(e1-e0, n1-n0), hypot(e1-e2, n1-n2)) > hypot(e0-e2, n0-n2):
                del Stops[i]
                flag = True
    cv.delete(ALL)
    cv.create_image(0, 0, anchor=NW, image=img)

    def color(t):
        if t < 0.5:
            r = int(510 * t)
            g = 127
        else:
            r = 255
            g = int(255 * (1 - t))
        return f'#{r:02X}{g:02X}00'

    for i in range(len(Stops)-1):
        cv.create_line(*calXY(*geo[Stops[i]]), *
                       calXY(*geo[Stops[i+1]]), fill=color(i/len(Stops)), width=3)

    def draw(stop, r, color):
        if stop not in geo:
            return
        x, y = calXY(*geo[stop])
        cv.create_oval(x-r, y-r, x+r, y+r, fill=color)

    for stop in Stops:
        draw(stop, 2, '#FFFFFF')

    draw(path[0][3][0], 4, '#00FF00')
    for i in range(len(path)-1):
        draw(path[i][3][-1], 4, '#FFFF00')
    draw(path[-1][3][-1], 4, '#FF0000')


pTable.bind('<1>', lambda _: root.after(10, pShow))
pTable.bind('<Key>', lambda _: root.after(10, pShow))

Button(root, text='开始规划！', command=submit, width=10).place(x=1100, y=98)

root.mainloop()
