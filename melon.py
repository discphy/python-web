import re
import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime

today_date = datetime.today().strftime('%Y%m%d')
music_columns = ['제목', '아티스트', '앨범']

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
# 사용자 페이지

member_key = '56195228' #박한영10
# member_key = '56389814' #지태선
playlist_url = 'https://www.melon.com/mymusic/playlist/mymusicplaylist_list.htm'
music_url = 'https://www.melon.com/mymusic/playlist/mymusicplaylistview_inform.htm'

driver.get(playlist_url + '?memberKey=' + member_key)

# 플레이리스트 seq 가져오기 (page : 20)
playlist_total_count = int(driver.find_element(By.CSS_SELECTOR, '.no').text)
print("플레이리스트 총 개수", playlist_total_count)

playlist_total_page = int(playlist_total_count / 20 + (0 if playlist_total_count % 20 == 0 else 1))
print("플레이리스트 페이지", playlist_total_page)

# driver.execute_script
# javascript:pageObj.sendPage('1');

playlists = []
playlist_seqs = []

for offset in range(1, playlist_total_count + 1, 20):
    driver.execute_script("javascript:pageObj.sendPage('" + str(offset) + "')")
    time.sleep(1)

    elements = driver.find_elements(By.CSS_SELECTOR, 'dt a')
    for element in elements:
        playlists.append(element.get_attribute('href'))
        break


for playlist in playlists:
    # 정규 표현식을 사용하여 숫자 추출
    playlist_seq = re.findall(r'\d+', playlist)[1]
    playlist_seqs.append(playlist_seq)

print("시퀀스 목록", playlist_seqs)

data_frame_list = []

for playlist in playlist_seqs:
    driver.get(music_url + '?plylstSeq=' + playlist)

    playlist_title = driver.find_element(By.CSS_SELECTOR, '.more_txt_title').text
    print("플레이리스트 타이틀", playlist_title)

    music_total = driver.find_element(By.CSS_SELECTOR, '.title .cnt').text
    music_total = int(re.search(r'\d+', music_total).group())
    print("수록곡", music_total)

    sheet_name = playlist_title
    data = []

    for offset in range(1, music_total, 50):
        driver.execute_script("javascript:pageObj.sendPage('" + str(offset) + "')")
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        soup.find()

        tr_tags = soup.find_all('tr')

        for tr in tr_tags:
            td_tags = tr.find_all('td', class_='t_left')

            if td_tags:
                if td_tags[0].find(class_='fc_gray') is None:
                    continue

                title = td_tags[0].find(class_='fc_gray').text.strip()
                artist = td_tags[1].find(id='artistName').text.strip()
                album = td_tags[2].find(class_='fc_mgray').text.strip()

                data.append([title, artist, album])

                print("Title : ", title, " / ", "Artist : ", artist, " / ", "Album : ", album)

    df = pd.DataFrame(data, columns=music_columns)
    data_frame_list.append({'sheet': sheet_name, 'data': df})

with pd.ExcelWriter('playlist_' + member_key + '_' + today_date + '.xlsx') as writer:
    for data_frame in data_frame_list:
        data_frame.get('data').to_excel(excel_writer=writer, sheet_name=data_frame.get('sheet'), index=False)

driver.quit()

