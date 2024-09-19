import requests
from urllib import parse

from bs4 import BeautifulSoup

import pandas as pd
import sqlite3

discordwebhook="https://discordapp.com/api/webhooks/1208728872863006770/XR4MBxsjyh2wNOagnNFFVoter8fGkIWTcCvBjo6SuYWCusNmj5LhX8fGmTE_YAtx2nkt"

def Sendmsg(msg, mycategory, myurl, mytitle, mywriter, mydate):     
    data = {
        "content" : "[ " + mycategory + " ] " + msg,
    }

    data["embeds"] = [
        {
            "description" : "작성자 : " + mywriter + "\n작성일 : " + mydate,
            "title" : mytitle,
            "url" : myurl
        }
    ]

    result = requests.post(discordwebhook, json = data)

# 신규 데이터 DB 저장 함수
def DatatoSQL(df):
    con = sqlite3.connect("plus.db")
    df.to_sql('ITEM', con, if_exists='append', index=False)
    con.close()


# 이전에 저장한 DB와 비교를 위해 불러옴
def Check():
    try:
        con = sqlite3.connect("plus.db") # db 파일명 사용자 임의 선정
        df = pd.read_sql("SELECT * from ITEM ", con=con)
        con.close()

        item_name = df['ID'].tolist()
        return item_name

    except Exception as e:
        return []

# 검색 함수
def Search():
    data = {'Category' : [],
            'Title' : [],
            'Writer' : [],
            'Date' : [],
            'Link' : [],
            'ID' : []}

    url = 'https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&lang=kor'

    # 봇으로 접근 시 차단될 수도 있어 유저 정보를 같이 보내기 위함함
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.content, 'html.parser')
    # print(soup)

    contents = soup.find('tbody').find_all('tr')
    # print(contents)

    for i in contents:
        C_category = i.select('td')[1].select('a')[0] # 공지사항 카테고리
        C_title = i.select('td')[1].select('a')[1] # 제목
        C_writer = i.select('td')[2]  # 글쓴이
        C_date = i.select('td')[4]   # 날짜
        C_link = i.select('a')[1]['href'] # 링크

        # print(C_category.text.strip())
        # print(C_title.text.strip())

        data['Category'].append(C_category.text.strip())
        data['Title'].append(C_title.text.strip())
        data['Writer'].append(C_writer.text.strip())
        data['Date'].append(C_date.text.strip())
        data['Link'].append(C_link)
        data['ID'].append(C_link.split('&')[1][6:]) # DB의 기존 자료와 비교하기 위한 식별자

    df = pd.DataFrame(data)
    print(df)
    
    check_list = Check() # 기존 저장된 링크 주소 리스트 불러오기

    for idx in data['ID']: #data['id']의 리스트를 하나씩 idx로 반복문을 돌림
        # 크롤링으로 받은 데이터의 링크의 마지막 주소가 기존 리스트에 없으면 메시지 전송/데이터 저장
        if idx not in check_list:
            # 메시지 내용 : 게시글 제목 + 작성자 + 날짜 + 링크 URL
            pos = data['ID'].index(idx)

            #******************************************************** 디스코드 메세지 전송 function
            
            # 로그 남기는 용도
            log_msg = '컴퓨터학부 공지 게시판에 새로운 글이 올라왔어요! \n\n{}\n{}\n{}\n{}\n{}\n{}'.format(data['Category'][pos], data['Title'][pos], data['Writer'][pos], data['Date'][pos], data['Link'][pos], data['ID'][pos])
            print(log_msg)

            # 실질적인 디스코드 메세지 부분
            discord_msg = '컴퓨터학부 공지 게시판에 새로운 글이 올라왔어요!'
            discord_url = data['Link'][pos]
            discord_category = data['Category'][pos]
            discord_title = data['Title'][pos]
            discord_writer = data['Writer'][pos]
            discord_date = data['Date'][pos]

            Sendmsg(discord_msg, discord_category, discord_url, discord_title, discord_writer, discord_date)
            #********************************************************
            
            DatatoSQL(df.loc[df['ID']==idx])
    
if __name__ == '__main__' :
    Search()