Python

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def get_monday_webtoons_data():
    """
    네이버 월요 웹툰 목록에서 웹툰 정보를 크롤링합니다.
    썸네일 이미지 URL, 웹툰 URL, 작가명, 평점을 가져옵니다.
    """
    # 웹드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
    options.add_argument('--disable-gpu') # GPU 가속 비활성화 (일부 시스템에서 필요)
    options.add_argument('--no-sandbox') # Sandbox 프로세스 사용 안함 (Linux에서 root로 실행시 필요)
    options.add_argument('--disable-dev-shm-usage') # /dev/shm 파티션 사용 안함 (메모리 부족 문제 방지)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36") # User-Agent 설정

    # ChromeDriverManager를 사용하여 ChromeDriver 자동 설치 및 서비스 시작
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"웹 드라이버 설정 중 오류 발생: {e}")
        print("ChromeDriver가 올바르게 설치되었는지 확인하거나, 직접 경로를 지정해주세요.")
        return None

    # 네이버 웹툰 월요 웹툰 페이지 URL
    url = "https://comic.naver.com/webtoon/weekdayList?week=mon"
    driver.get(url)

    webtoon_data = []

    try:
        # 웹툰 목록이 로드될 때까지 대기 (최대 20초)
        # 주의: 클래스명은 네이버 웹툰 페이지 업데이트에 따라 변경될 수 있습니다.
        # 2025년 5월 기준, 웹툰 리스트를 감싸는 ul 태그의 클래스명
        list_selector = "ul.WeekdayMainView__daily_list--R52lc"
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, list_selector))
        )

        # 각 웹툰 아이템을 선택합니다. (li 태그)
        # 2025년 5월 기준, 각 웹툰 아이템 li 태그의 클래스명
        webtoon_items = driver.find_elements(By.CSS_SELECTOR, f"{list_selector} > li.WeekdayMainView__item--Sn_s5")

        if not webtoon_items:
            print("웹툰 아이템을 찾을 수 없습니다. CSS 선택자를 확인해주세요.")
            driver.quit()
            return None

        print(f"총 {len(webtoon_items)}개의 월요 웹툰을 찾았습니다. 정보 수집을 시작합니다...")

        for item in webtoon_items:
            try:
                # 썸네일 이미지 URL
                # 2025년 5월 기준, 썸네일 이미지를 포함하는 div 내부의 img 태그
                thumbnail_element = item.find_element(By.CSS_SELECTOR, "div.Thumbnail__image_area--jG1Fc img.Thumbnail__image--K9J99")
                thumbnail_url = thumbnail_element.get_attribute('src')

                # 웹툰 링크 (주소) 와 제목
                # 2025년 5월 기준, 웹툰 링크 a 태그
                link_element = item.find_element(By.CSS_SELECTOR, "a.Poster__link--KNf69")
                webtoon_url = link_element.get_attribute('href')
                # title_text = link_element.get_attribute('title') # 웹툰 제목도 가져올 수 있음

                # 작가명
                # 2025년 5월 기준, 작가명을 포함하는 span 태그
                # 작가가 여러 명일 수 있으므로 find_elements 후 join 처리
                author_elements = item.find_elements(By.CSS_SELECTOR, "span.ContentAuthor__author--CTAAP")
                authors = ", ".join([author.text.strip() for author in author_elements if author.text.strip()])
                if not authors: # 간혹 구조가 다른 경우 (예: '글/그림' 같이 표시)
                    try:
                        # 대체 선택자 (더 일반적일 수 있지만, 정확도는 떨어질 수 있음)
                        author_alt_element = item.find_element(By.CSS_SELECTOR, "span.ContentMetaInfo__meta_info--H_info")
                        authors = author_alt_element.text.strip() # 이 경우 "글/그림 작가명" 형태일 수 있음
                    except NoSuchElementException:
                        authors = "N/A"


                # 평점
                # 2025년 5월 기준, 평점을 포함하는 span 태그
                try:
                    rating_element = item.find_element(By.CSS_SELECTOR, "span.Rating__star_num--N2ZOr")
                    rating = rating_element.text
                except NoSuchElementException:
                    rating = "N/A" # 평점이 없는 경우 (신작 등)

                webtoon_info = {
                    "thumbnail_image_url": thumbnail_url,
                    "webtoon_url": webtoon_url,
                    "author": authors,
                    "rating": rating
                }
                webtoon_data.append(webtoon_info)
                # print(f"수집 완료: {title_text if 'title_text' in locals() else '제목 미상'}")

            except NoSuchElementException as e:
                print(f"항목 내 일부 요소 누락: {e}")
                # title_for_error = "알 수 없음"
                # try:
                #     title_for_error = item.find_element(By.CSS_SELECTOR, "a.Poster__link--KNf69").get_attribute('title')
                # except:
                #     pass
                # print(f"웹툰 '{title_for_error}' 정보 수집 중 일부 요소 누락. 다음 항목으로 넘어갑니다.")
                continue # 일부 요소가 없더라도 다음 웹툰으로 계속 진행
            except Exception as e:
                print(f"개별 웹툰 정보 수집 중 오류 발생: {e}")
                continue

    except TimeoutException:
        print("웹툰 목록 로딩 시간 초과. 페이지가 완전히 로드되지 않았거나 선택자가 잘못되었을 수 있습니다.")
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
    finally:
        driver.quit()

    return pd.DataFrame(webtoon_data)

if __name__ == "__main__":
    print("네이버 월요 웹툰 정보 크롤링을 시작합니다...")
    start_time = time.time()

    df_webtoons = get_monday_webtoons_data()

    end_time = time.time()
    print(f"크롤링 완료. 총 소요 시간: {end_time - start_time:.2f}초")

    if df_webtoons is not None and not df_webtoons.empty:
        print("\n--- 수집된 웹툰 정보 ---")
        print(df_webtoons)
        # CSV 파일로 저장 (UTF-8, 한글 깨짐 방지)
        try:
            df_webtoons.to_csv("naver_monday_webtoons.csv", index=False, encoding='utf-8-sig')
            print("\n데이터가 naver_monday_webtoons.csv 파일로 저장되었습니다.")
        except Exception as e:
            print(f"CSV 파일 저장 중 오류 발생: {e}")
    elif df_webtoons is not None and df_webtoons.empty:
        print("수집된 웹툰 정보가 없습니다. 웹사이트 구조 변경 또는 네트워크 문제를 확인해주세요.")
    else:
        print("데이터 수집에 실패했습니다.")