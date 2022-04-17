# 20211209：
# ・複数の.pyファイルに分けていたコードを一つにまとめました。(HSVaR.py、DeltaNormal.py、MakePortfolio.py → Group2.py)
# ・yahoo_finance_api2を使い、今週の株価データを取得してcsvファイルに保存するコードを追加しました。(###で囲った範囲)
# 20211216:
# ・datetimeを使って、今週と先週の日付を自動的に取得し表示できるようにしました。
import pandas as pd
import numpy as np
import math
import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import datetime

thisweek = datetime.date.today()
lastweek = thisweek - datetime.timedelta(days=7)
ThisWeek = thisweek.strftime('%Y%m%d')
LastWeek = lastweek.strftime('%Y%m%d')
print('ThisWeek:', ThisWeek)
print('LastWeek:', LastWeek)

###
Nintendo_code = 7974
Capcom_code = 9697
# 今週の株価データ（終値）の取得
my_share_Nintendo = share.Share(str(Nintendo_code) + ".T")
my_share_Capcom = share.Share(str(Capcom_code) + ".T")
symbol_data_Nintendo = None
symbol_data_Capcom = None
try:
    symbol_data_Nintendo = my_share_Nintendo.get_historical(share.PERIOD_TYPE_DAY,
                                            1,
                                            share.FREQUENCY_TYPE_DAY,
                                            1)
    symbol_data_Capcom = my_share_Capcom.get_historical(share.PERIOD_TYPE_DAY,
                                            1,
                                            share.FREQUENCY_TYPE_DAY,
                                            1)
except YahooFinanceError as e:
    print(e.message)
print('Nintendo:',symbol_data_Nintendo['close'][-1])
print('Capcom:',symbol_data_Capcom['close'][-1])
# 2つの株価データ（終値）をCSVファイルに保存
FP = open('Market_'+ThisWeek+'.csv','w')
FP.write(str(symbol_data_Nintendo['close'][-1])+','+str(symbol_data_Capcom['close'][-1]))
FP.close()
###

# 今週のポートフォリオの作成
M_LastWeek = pd.read_csv('Market_'+LastWeek+'.csv', header=None)
M_ThisWeek = pd.read_csv('Market_'+ThisWeek+'.csv', header=None)
P_LastWeek = pd.read_csv('Portfolio_'+LastWeek+'.csv', header=None)
Va = (M_ThisWeek[0][0]/M_LastWeek[0][0])*P_LastWeek[0][0]
Vb = (M_ThisWeek[1][0]/M_LastWeek[1][0])*P_LastWeek[1][0]
print('Value_Nintendo,Capcom:',Va,Vb)
NPV_ThisWeek = Va+Vb+P_LastWeek[2][0]
NPV_LastWeek = P_LastWeek[0][0]+P_LastWeek[1][0]+P_LastWeek[2][0]
print('NPV_ThisWeek,LastWeek:',NPV_ThisWeek,NPV_LastWeek)
# 計算した値をCSVファイルに保存
FP = open('Portfolio_'+ThisWeek+'.csv','w')
FP.write(str(Va)+','+str(Vb)+','+str(P_LastWeek[2][0]))
FP.close()

P = pd.read_csv('Portfolio_' + ThisWeek + '.csv', header=None)
X1 = P[0][0]
X2 = P[1][0]
V0 = X1 + X2

def valuelist():
    TestEquity = pd.read_table(FN, sep='\n', header=None)
    S1 = TestEquity
    daycounter = 0  # = は0を入れる # == は比べて同じかどうか確かめる
    v_S1 = S1.values  # .valuesは辞書の中に含まれるすべての値を取り出す
    for u in v_S1:  # 順に取り出す
        if daycounter == 0:
            r=[]  # 空のハコ
            daycounter = 1
        else:
            valuetoday = S1[0][daycounter]
            valueyesterday = S1[0][daycounter -1]
            returntoday = (valuetoday-valueyesterday)/valueyesterday
            r.append(returntoday)
            daycounter += 1  # daycounterの値を1つ増やす
    return r

if __name__ == '__main__':
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
    # DNVaR1 = 2.33 * sigmaP - muP
    DNVaR5 = 2.33 * np.sqrt(5) * sigmaP - 5 * muP  # タイムホライゾン5日のVaR
    print('DNVaR:', DNVaR5)
    # DNVaR15 = 2.33 * np.sqrt(15) * sigmaP - 15 * muP  # タイムホライゾン15日のVaR
# ヒストリカルシミュレーション法
    daycounter = 0
    for u in r1:  # r1に入っている要素の分だけ
        if daycounter == 0:
            vt=[]
            daycounter = 1
        else:
            R1 = r1[daycounter]
            R2 = r2[daycounter]
            valuetomorrow = V0 + X1 * R1 +X2 * R2
            vt.append(valuetomorrow)
            daycounter +=1
    vt.sort()   # 昇順に並び替え
    # print(vt)   # 仮想的なポートフォリオの明日の価値(昇順)
    i = math.floor(len(vt) * 0.01)  # i:仮想的な価値の小さい方から1％、math.floor：小数点以下を切り捨て
    vi = vt[i-1]   # vtの中の「仮想的な価値の小さい方から1％」=(4)番目の値
    HSVaR1 = V0 - vi  # タイムホライゾン1日のVaR
    HSVaR5 = np.sqrt(5) * HSVaR1   # タイムホライゾン5日のVaR
    print('HSVaR:', HSVaR5)
    # HSVaR15 = np.sqrt(15) * HSVaR1  # タイムホライゾン15日のVaR
