#!/usr/bin/env python3

"""
東京都の新型コロナデータから感染者数データを取得。
期間を指定、年代を選択することで、範囲内の感染者数を計算。
streamlitを使ったwebアプリです。

出典：東京都 新型コロナウイルス陽性患者発表詳細オープンデータ
https://stopcovid19.metro.tokyo.lg.jp/data/130001_tokyo_covid19_patients.csv
"""

# 必要なモジュールのインポート
import streamlit as st
from streamlit import caching

from datetime import datetime
from datetime import date
from datetime import timedelta

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import japanize_matplotlib


st.title('東京都の新型コロナ感染者数')

# 東京都 新型コロナウイルス陽性患者発表詳細オープンデータ
url = 'https://stopcovid19.metro.tokyo.lg.jp/data/130001_tokyo_covid19_patients.csv'

# オープンデータ読取、公表年月日をdatetime型に変換する関数
@st.cache(ttl=300)
def load_data():
    df = pd.read_csv(url, skiprows=range(1, 500))
    df["公表_年月日"] = pd.to_datetime(df["公表_年月日"]).dt.date
    return df

# オープンデータ読取実行
data_load_state = st.text('Loading data...')
df = load_data()
data_load_state.text('Loading data...Done!')


st.write('東京都 新型コロナウイルス陽性患者発表詳細オープンデータ')
st.write('公表年月日ごとの感染者数データ')

# 公表_年月日でグループ分け
df_date = df.groupby('公表_年月日').count()
df_date.rename(columns={'No': '感染者数'}, inplace=True)

st.dataframe(df_date.sort_index(ascending=False), width=1000, height=200)

st.write('最新の入力日', df_date.index[-1])

today_time = datetime.now() + timedelta(hours=9)
today = today_time.strftime('%Y-%m-%d')
if df_date.index[-1].strftime('%Y-%m-%d') == today:
    st.write('※備考　今日のデータも入力済みです')
else:
    st.write('※注意　今日のデータは未入力です')

# 先週の感染者数の合計
lastweek_start = (today_time - timedelta(days=13)).date()
lastweek_end = (today_time - timedelta(days=7)).date()
df_lastweek = df_date.loc[lastweek_start: lastweek_end, '感染者数']
lastweek_sum = df_lastweek.sum()
lastweek_mean = df_lastweek.mean()
st.write(f'先週の感染者数( {lastweek_start} から {lastweek_end} ): 合計 {lastweek_sum} 人, 平均 {"{:.3f}".format(lastweek_mean)} 人です')

# 今週の感染者数の合計
thisweek_start = (today_time - timedelta(days=6)).date()
thisweek_end = (today_time - timedelta(days=0)).date()
df_thisweek = df_date.loc[thisweek_start: thisweek_end, '感染者数']
thisweek_sum = df_thisweek.sum()
thisweek_mean = df_thisweek.mean()
st.write(f'今週の感染者数( {thisweek_start} から ※今日のデータ未入力かどうか注意): 合計 {thisweek_sum} 人, 平均 {"{:.3f}".format(thisweek_mean)} 人です')

# 感染者数のグラフを作成
fig1 = plt.figure(figsize=[20, 10])
plt.bar(df_date.index, df_date['感染者数'], color="blue", label='一日当たりの感染者数')
plt.title('東京都の感染者数', fontsize=30, fontweight='bold', color='blue')
plt.xlabel("公表年月日", style ="italic" , size = "xx-large", color ="blue")
plt.ylabel("感染者数", style ="italic" , size = "xx-large", color ="blue", rotation = "horizontal")

plt.xticks(rotation=60)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.gcf().autofmt_xdate()

plt.tight_layout()
plt.legend()
plt.show()

st.pyplot(fig1)


# 感染者数を計算（期間を指定してください）
st.sidebar.write('★感染者数を計算する期間を入力')
start_date1 = st.sidebar.date_input('開始日を指定してください',
                             min_value=date(2020, 1, 1),
                             max_value=today_time.date(),
                             value=today_time.date(),
                             )
st.sidebar.write('開始日:', start_date1)

end_date1 = st.sidebar.date_input('終了日を指定してください',
                             min_value=date(2020, 1, 1),
                             max_value=today_time.date(),
                             value=today_time.date(),
                             )
st.sidebar.write('終了日:', end_date1)
st.sidebar.markdown('''
***
''')

# 期間で抽出
df_span = df_date.loc[start_date1: end_date1, '感染者数']
# 期間の合計感染者数
span_sum = df_span.sum()
span_mean = df_span.mean()

st.write('<span style="color:blue">期間を指定して感染者数を計算します</span>', unsafe_allow_html=True)
st.write(f'<span style="color:blue">指定期間の感染者数の合計は {span_sum} 人, 平均は {"{:.3f}".format(span_mean)} 人です。</span>', unsafe_allow_html=True)
st.markdown('''
***
''')


# 感染者の年代を選択してください
st.sidebar.write('★感染者の年代を選択してください')
age = st.sidebar.selectbox('感染者の年代を選択してください',
    ["10歳未満", "10代", "20代", "30代", "40代", "50代", "60代", "70代", "80代", "90代", "100歳以上"])
st.sidebar.write(f'選択した年代: {age}')

# 年代で抽出
df_age = df[df['患者_年代'] == age]

# 公表年月日でグループ分け
df_age_date = df_age.groupby('公表_年月日').count()
df_age_date.rename(columns={'No': '感染者数'}, inplace=True)

st.write('<span style="color:green">年代別の感染者数データを表示します</span>', unsafe_allow_html=True)
st.write(f'<span style="color:green">({age})公表年月日ごとの感染者数データ</span>', unsafe_allow_html=True)
st.dataframe(df_age_date.sort_index(ascending=False), width=1000, height=200)

# 年代別の感染者数グラフを作成
fig2 = plt.figure(figsize=[20, 10])
plt.title(f'東京都の感染者数({age})', fontsize=30, fontweight='bold', color='green')
plt.bar(df_age_date.index, df_age_date['感染者数'], color="green",  label='1日当たりの感染者数')
plt.xlabel("公表年月日", style ="italic" , size = "xx-large", color ="green")
plt.ylabel("感染者数", style ="italic" , size = "xx-large", color ="green", rotation = "horizontal")

plt.xticks(rotation=60)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.gcf().autofmt_xdate()

plt.tight_layout()
plt.legend()
plt.show()

st.pyplot(fig2)

# 期間で抽出
df_age_span = df_age_date.loc[start_date1: end_date1, '感染者数']
# 年代別・期間の合計感染者数
age_span_sum = df_age_span.sum()
age_span_mean = df_age_span.mean()

st.write(f'<span style="color:green">期間を指定して({age})の感染者数を計算します</span>', unsafe_allow_html=True)
st.write(f'<span style="color:green">({age})感染者数の指定期間の合計は {age_span_sum} 人, 平均は {"{:.3f}".format(age_span_mean)} 人です。</span>', unsafe_allow_html=True)
st.write(f'<span style="color:green">全年代に占める割合は {"{:.3f}".format(age_span_sum / span_sum *100)} % です。</span>', unsafe_allow_html=True)
st.markdown('''
***
''')
st.markdown('''
[東京都 新型コロナHP](https://stopcovid19.metro.tokyo.lg.jp/)
***
[東京都福祉保健局 最新リリースHP](https://www.fukushihoken.metro.tokyo.lg.jp/)
''')

