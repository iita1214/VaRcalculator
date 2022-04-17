# ※日付の自動入力を無効にした場合、マーケット情報を自動生成しないため、既存のcsvファイルの日付を指定しなければならない。
# ※日付の自動入力を有効にした場合、起動に時間がかかる場合がある。
# ・日付の自動入力で取得してくる日付は直近の木曜日に設定してあるため、csvファイルが存在していればいつでも動くようになっている。

import pandas as pd
import numpy as np
import math
import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import datetime
import tkinter.messagebox
import tkinter as tkinter

root0 = tkinter.Tk()
root0.withdraw()
autodate = tkinter.messagebox.askyesno(title="Autodate", message="日付を自動入力にしますか？")
root0.destroy()
root0.mainloop()

if autodate:
    def get_target_date(date, target_week):
        week = ['月', '火', '水', '木', '金', '土', '日']
        # 曜日を数値型で取得
        weekday = date.weekday()
        if weekday == 3:
            target_date = datetime.date.today()
            print(target_date)
        elif weekday > 3:
            sub_days = weekday - week.index(target_week)
            target_date = date - datetime.timedelta(days=sub_days)
        elif weekday < 3:
            sub_days = 1 + weekday + week.index(target_week)
            target_date = date - datetime.timedelta(days=sub_days)
        else:
            print('不正な数値')
        return target_date
    today = datetime.date.today()
    # 指定した日(今日)よりも前の木曜日の日付を取得
    # 今日が木曜日なら今日を取得
    thisweek = get_target_date(today, '木')
    lastweek = thisweek - datetime.timedelta(days=7)
    # print(thisweek)     #class 'datetime.date'
    # print(lastweek)
    Thisweek = thisweek.strftime('%Y-%m-%d')
    Lastweek = lastweek.strftime('%Y-%m-%d')
    timehorizon = 5

    code_1 = '7974.T'  # Nintendo
    code_2 = '9697.T'  # Capcom
    def get_close(FetchDate, code):
        # Fetch 10y data from yahoo finance
        my_share = share.Share(code)
        symbol_data = None
        try:
            symbol_data = my_share.get_historical(
                share.PERIOD_TYPE_DAY, 50,
                share.FREQUENCY_TYPE_DAY, 1)
        except YahooFinanceError as e:
            print(e.message)
            sys.exit(1)
        # convert to pandas dataframe object
        df = pd.DataFrame(symbol_data)
        df["datetime"] = pd.to_datetime(df.timestamp, unit="ms")  # ms=ミリ秒
        # convert to Japanese Standard Time
        df["datetime_JST"] = df["datetime"] + datetime.timedelta(hours=9)
        # write to a csv file with name [code]_[Date].csv
        FetchDate_Obj_S = datetime.datetime.strptime(FetchDate + ' 00:00',
                                                     "%Y-%m-%d %H:%M")  # convert the date str to date object
        FetchDate_Obj_E = datetime.datetime.strptime(FetchDate + ' 23:59', "%Y-%m-%d %H:%M")
        timestamp_S = int(round(FetchDate_Obj_S.timestamp())) * 1000
        timestamp_E = int(round(FetchDate_Obj_E.timestamp())) * 1000
        df = df[timestamp_S <= df['timestamp']]
        df = df[df['timestamp'] <= timestamp_E]
        # print('timestamp_S=', timestamp_S)
        # print('timestamp_E=', timestamp_E)
        # print('df[]=')
        # print(df['timestamp'])
        # df = df[df['timestamp'] <= E_timestamp]
        df = df.reset_index(drop=True)  # indexに番号振り直す？
        # print('fetched data:')
        # print(df)
        # print('close:', df['close'][0])
        return df['close'][0]
    FP = open('Market_' + Thisweek + '.csv', 'w')
    FP.write(str(get_close(Thisweek, code_1)) + ',' + str(get_close(Thisweek, code_2)))
    FP.close()
    FP = open('Market_' + Lastweek + '.csv', 'w')
    FP.write(str(get_close(Lastweek, code_1)) + ',' + str(get_close(Lastweek, code_2)))
    FP.close()

if not autodate:
    root1 = tkinter.Tk()
    root1.title("Date Setting")
    root1.geometry("400x300")
    root1.attributes("-topmost", True)
    Label1 = tkinter.Label(text=u'※日付の入力形式:YYYY-MM-DD')
    Label1.place(x=40, y=40)
    Entry1 = tkinter.Entry(width=50)  # widthプロパティで大きさを変える
    Entry1.insert(tkinter.END, '2022-01-13')  # 最初から文字を入れておく
    Entry1.place(x=40, y=80)
    Entry2 = tkinter.Entry(width=50)  # widthプロパティで大きさを変える
    Entry2.insert(tkinter.END, '2021-12-23')  # 最初から文字を入れておく
    Entry2.place(x=40, y=120)
    Label2 = tkinter.Label(text='▼　タイムホライゾン　▼')
    Label2.place(x=40, y=160)
    Entry3 = tkinter.Entry(width=50)
    Entry3.place(x=40, y=200)
    def enter():
        global Thisweek
        global Lastweek
        global timehorizon
        Thisweek = str(Entry1.get())
        Lastweek = str(Entry2.get())
        timehorizon = int(Entry3.get())
        root1.destroy()
    Button = tkinter.Button(master=root1, text='ENTER', command=enter)
    Button.place(x=40, y=250)

    root1.mainloop()
print('ThisWeek:', Thisweek)
print('LastWeek:', Lastweek)


# 今週のポートフォリオ作成
M_Lastweek = pd.read_csv('Market_' + Lastweek + '.csv', header=None)
M_Thisweek = pd.read_csv('Market_' + Thisweek + '.csv', header=None)
P_Lastweek = pd.read_csv('Portfolio_' + Lastweek + '.csv', header=None)
Va = (M_Thisweek[0][0] / M_Lastweek[0][0]) * P_Lastweek[0][0]
Vb = (M_Thisweek[1][0] / M_Lastweek[1][0]) * P_Lastweek[1][0]
print(Va, Vb)
NPV_Thisweek = Va + Vb + P_Lastweek[2][0]
NPV_Lastweek = P_Lastweek[0][0] + P_Lastweek[1][0] + P_Lastweek[2][0]
print('NPV_Thisweek:', NPV_Thisweek)
print('NPV_Lastweek:', NPV_Lastweek)
# 計算した値をCSVファイルに保存
FP = open('Portfolio_' + Thisweek + '.csv', 'w')
FP.write(str(Va) + ',' + str(Vb) + ',' + str(P_Lastweek[2][0]))
FP.close()
P = pd.read_csv('Portfolio_' + Thisweek + '.csv', header=None)
X1 = P[0][0]
X2 = P[1][0]
V0 = X1 + X2

def calculate():
    def valuelist():
        TestEquity = pd.read_table(FN, sep='\n', header=None)
        S1 = TestEquity
        daycounter = 0  # = は0を入れる # == は比べて同じかどうか確かめる
        v_S1 = S1.values  # .valuesは辞書の中に含まれるすべての値を取り出す
        for u in v_S1:  # 順に取り出す
            if daycounter == 0:
                r = []  # 空のハコ
                daycounter = 1
            else:
                valuetoday = S1[0][daycounter]
                valueyesterday = S1[0][daycounter - 1]
                returntoday = (valuetoday - valueyesterday) / valueyesterday
                r.append(returntoday)
                daycounter += 1  # daycounterの値を1つ増やす
        return r
    FN = 'Nintendo2.dat'
    r1 = valuelist()  # nintendoのdatファイルを読み込んだ際のrの値
    FN = 'CAPCOM2.dat'
    r2 = valuelist()  # capcomのdatファイルを読み込んだ際のrの値
# デルタノーマル法
    mu1 = np.mean(r1)  # mean:期待値
    sigma1 = np.std(r1)  # std:標準偏差
    mu2 = np.mean(r2)  # mean:期待値
    sigma2 = np.std(r2)  # std:標準偏差
    cor = np.corrcoef(r1, r2)  # ρ：相関係数
    rho = cor[0][1]  # ρ = rho
    muP = X1 * mu1 + X2 * mu2
    sigmaP = np.sqrt((X1 * sigma1) ** 2 + (X2 * sigma2) ** 2 + 2 * X1 * X2 * sigma1 * sigma2 * rho)
    DNVaR5 = 2.33 * np.sqrt(int(timehorizon)) * sigmaP - int(timehorizon) * muP  # タイムホライゾン5日のVaR
    print('DNVaR:', DNVaR5)
# ヒストリカルシミュレーション法
    daycounter = 0
    for u in r1:  # r1に入っている要素の分だけ
        if daycounter == 0:
            vt = []
            daycounter = 1
        else:
            R1 = r1[daycounter]
            R2 = r2[daycounter]
            valuetomorrow = V0 + X1 * R1 + X2 * R2
            vt.append(valuetomorrow)
            daycounter += 1
    vt.sort()  # 昇順に並び替え
    # print(vt)   # 仮想的なポートフォリオの明日の価値(昇順)
    i = math.floor(len(vt) * 0.01)  # i:仮想的な価値の小さい方から1％、math.floor：小数点以下を切り捨て
    vi = vt[i - 1]  # vtの中の「仮想的な価値の小さい方から1％」=(4)番目の値
    HSVaR1 = V0 - vi  # タイムホライゾン1日のVaR
    HSVaR5 = np.sqrt(int(timehorizon)) * HSVaR1  # タイムホライゾン5日のVaR
    print('HSVaR:', HSVaR5)
    entry1.insert(tkinter.END, Va)
    entry2.insert(tkinter.END, Vb)
    entry3.insert(tkinter.END, NPV_Thisweek)
    entry4.insert(tkinter.END, DNVaR5)
    entry5.insert(tkinter.END, HSVaR5)

root = tkinter.Tk()
root.title(u"Group2 HSVaR calculator")
root.geometry("350x500")
root.attributes("-topmost", True)
label_thisweek = tkinter.Label(text="Thisweek "+Thisweek)
label_thisweek.place(x=40, y=20)
label_lastweek = tkinter.Label(text="Lastweek "+Lastweek)
label_lastweek.place(x=40, y=40)
label1 = tkinter.Label(text="Nintendo(Va)")
label1.place(x=40, y=80)
label2 = tkinter.Label(text="Capcom(Vb)")
label2.place(x=40, y=130)
label3 = tkinter.Label(text="NPV")
label3.place(x=40, y=180)
label4 = tkinter.Label(text="DNVaR")
label4.place(x=40, y=230)
label5 = tkinter.Label(text="HSVaR")
label5.place(x=40, y=280)
entry1 = tkinter.Entry(width=25)
entry1.place(x=120, y=80)
entry2 = tkinter.Entry(width=25)
entry2.place(x=120, y=130)
entry3 = tkinter.Entry(width=25)
entry3.place(x=120, y=180)
entry4 = tkinter.Entry(width=25)
entry4.place(x=120, y=230)
entry5 = tkinter.Entry(width=25)
entry5.place(x=120, y=280)
button = tkinter.Button(master=root, text='RUN', command=calculate)
button.place(x=150, y=400)

root.mainloop()
