import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 상수 정의
WAIT_TIME = 10
FILENAME_PREFIX = 'youtube_'


# 함수 정의
def read_excel_data(filename):
    xls = pd.ExcelFile(filename)
    all_data = {}
    for sheet_name in xls.sheet_names:
        all_data[sheet_name] = pd.read_excel(xls, sheet_name)
    return all_data


def search_and_get_links(driver, data):
    for sheet_name, df in data.items():
        print(f"--- 시트: {sheet_name} ---")
        df['링크'] = ''
        for index, row in df.iterrows():
            keyword = f"{row.iloc[0]} {row.iloc[1]} topic"

            search = driver.find_element(By.NAME, "search_query")
            search.clear()
            search.send_keys(keyword)
            search.send_keys(Keys.ENTER)
            time.sleep(1)

            try:
                topic = WebDriverWait(driver, WAIT_TIME).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h3 a"))
                )
                link_url = topic.get_attribute("href")
                print(link_url)
                df.at[index, '링크'] = link_url
            except Exception as e:
                print(f"검색 결과를 찾을 수 없습니다: {e}")


def write_to_excel(data, filename):
    with pd.ExcelWriter(FILENAME_PREFIX + filename) as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


# 메인 코드
def main():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # headless 모드로 설정
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.youtube.com/")

    filename = 'playlist_56195228_20240322.xlsx'

    # Excel 파일에서 데이터 읽기
    data = read_excel_data(filename)

    # YouTube에서 검색 및 링크 가져오기
    search_and_get_links(driver, data)

    # Excel 파일로 쓰기
    write_to_excel(data, filename)

    # 브라우저 종료
    driver.quit()


if __name__ == "__main__":
    main()
