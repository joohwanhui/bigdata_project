알겠습니다. 네이버 웹툰 메인 페이지 (https://comic.naver.com/webtoon)에 있는 웹툰 목록 중 순위가 표시되는 "실시간 인기 웹툰" 섹션을 기준으로 정보를 가져오겠습니다.

크롤링할 정보:

순위 (Rank)
썸네일 이미지 URL (Thumbnail Image URL)
웹툰 URL (Webtoon URL) (사용자 요청에는 없었지만, 일반적으로 필요하여 포함)
제목 (Title) (사용자 요청에는 없었지만, 명확성을 위해 포함)
작가명 (Author)
평점 (Rating): "실시간 인기 웹툰" 섹션에는 별점이 직접 표시되지 않습니다. 해당 위치에 평점이 없으므로 "N/A (메인 페이지 목록)"로 표시하거나, 각 웹툰 상세 페이지로 이동해야 정확한 평점을 가져올 수 있습니다. 이 코드에서는 메인 페이지에 보이는 정보만 가져오므로 "N/A"로 처리하겠습니다. 만약 각 웹툰의 상세 평점이 꼭 필요하다면 코드가 더 복잡해집니다. (사용자 요청에 "평점"이 두 번 언급되어, 중요하게 생각하시는 것 같지만, 현재 대상 섹션에는 없습니다.)
주의사항:

웹사이트의 HTML 구조는 네이버에서 업데이트할 경우 변경될 수 있으며, 이 경우 CSS 선택자가 동작하지 않아 코드를 수정해야 합니다. (현재 코드는 2025년 5월 기준입니다.)
과도한 크롤링은 서비스 제공자에게 부담을 줄 수 있으므로, 적절한 간격(예: time.sleep)을 두거나 API 사용 가능 여부를 확인하는 것이 좋습니다. (이 코드에서는 간단한 예시로 최소한의 대기만 포함합니다.)
필요 라이브러리 설치 (이미 설치하셨다면 생략):

Bash

pip install selenium webdriver-manager pandas
Python 코드:

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

def get_naver_main_popular_webtoons():
    """
    네이버 웹툰 메인 페이지의 '실시간 인기 웹툰' 목록에서 정보를 크롤링합니다.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"웹 드라이버 설정 중 오류 발생: {e}")
        return None

    base_url = "https://comic.naver.com/webtoon"
    driver.get(base_url)

    webtoon_data = []

    try:
        # '실시간 인기 웹툰' 목록을 포함하는 부모 요소 대기 (2025년 5월 기준 선택자)
        # 이 섹션은 <aside> 태그 내에 위치하며, 제목이 "실시간 인기 웹툰" 임을 확인했습니다.
        # 해당 리스트의 부모 wrapper 선택자
        popular_list_wrapper_selector = "div.AsideEpisode__episode_list_wrap--J06c9" # ul 태그의 부모 div
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, popular_list_wrapper_selector))
        )

        # '실시간 인기 웹툰'의 각 아이템 (li) 가져오기
        webtoon_items_selector = f"{popular_list_wrapper_selector} > ul > li.AsideEpisode__item--i30Zc"
        webtoon_items = driver.find_elements(By.CSS_SELECTOR, webtoon_items_selector)

        if not webtoon_items:
            print("실시간 인기 웹툰 아이템을 찾을 수 없습니다. CSS 선택자를 확인해주세요.")
            driver.quit()
            return None

        print(f"총 {len(webtoon_items)}개의 실시간 인기 웹툰을 찾았습니다. 정보 수집을 시작합니다...")

        for item in webtoon_items:
            try:
                # 순위 (Rank)
                # 순위는 li 태그 내의 span.AsideEpisode__ranking_number--f3sS1 에 있음
                rank_element = item.find_element(By.CSS_SELECTOR, "span.AsideEpisode__ranking_number--f3sS1")
                rank = rank_element.text.strip()

                # 웹툰 링크, 썸네일, 제목, 작가명을 포함하는 a 태그
                # a.Poster__link_area--LgU26.Poster__link_area--aside_episode--W1Y7R
                link_anchor = item.find_element(By.CSS_SELECTOR, "a.Poster__link_area--LgU26")
                webtoon_url = link_anchor.get_attribute('href')

                # 썸네일 이미지 URL
                # div.Poster__thumbnail_area--NzY07 > img.Poster__image--d9XoQ
                thumbnail_element = link_anchor.find_element(By.CSS_SELECTOR, "img.Poster__image--d9XoQ")
                thumbnail_url = thumbnail_element.get_attribute('src')

                # 제목 (Title)
                # strong.Poster__title--ihk_x.Poster__title--aside_episode--s0h7z
                title_element = link_anchor.find_element(By.CSS_SELECTOR, "strong.Poster__title--ihk_x")
                title = title_element.text.strip()

                # 작가명 (Author)
                # span.Poster__author--jD0Rk
                author_element = link_anchor.find_element(By.CSS_SELECTOR, "span.Poster__author--jD0Rk")
                author = author_element.text.strip()

                # 평점 (Rating) - 해당 섹션에는 별점 정보가 없음
                rating = "N/A (메인 페이지 목록)"

                webtoon_info = {
                    "rank": rank,
                    "title": title,
                    "author": author,
                    "thumbnail_url": thumbnail_url,
                    "webtoon_url": webtoon_url,
                    "rating": rating
                }
                webtoon_data.append(webtoon_info)

            except NoSuchElementException as e:
                # print(f"항목 내 일부 요소 누락 (웹툰 제목: {title if 'title' in locals() else '알 수 없음'}): {e}")
                print(f"실시간 인기 웹툰 목록 내 일부 요소 누락. 해당 항목 건너뜁니다. 오류: {e}")
                continue
            except Exception as e:
                print(f"개별 웹툰 정보 수집 중 알 수 없는 오류 발생: {e}")
                continue
        
    except TimeoutException:
        print("실시간 인기 웹툰 목록 로딩 시간 초과. 페이지 구조나 선택자를 확인해주세요.")
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
    finally:
        driver.quit()

    return pd.DataFrame(webtoon_data)

if __name__ == "__main__":
    print("네이버 웹툰 메인 페이지 '실시간 인기 웹툰' 정보 크롤링을 시작합니다...")
    start_time = time.time()

    df_popular_webtoons = get_naver_main_popular_webtoons()

    end_time = time.time()
    print(f"크롤링 완료. 총 소요 시간: {end_time - start_time:.2f}초")

    if df_popular_webtoons is not None and not df_popular_webtoons.empty:
        print("\n--- 수집된 실시간 인기 웹툰 정보 ---")
        print(df_popular_webtoons)
        try:
            df_popular_webtoons.to_csv("naver_main_popular_webtoons.csv", index=False, encoding='utf-8-sig')
            print("\n데이터가 naver_main_popular_webtoons.csv 파일로 저장되었습니다.")
        except Exception as e:
            print(f"CSV 파일 저장 중 오류 발생: {e}")
    elif df_popular_webtoons is not None and df_popular_webtoons.empty:
        print("수집된 웹툰 정보가 없습니다. 웹사이트 구조 변경, 네트워크 문제 또는 선택자를 확인해주세요.")
    else:
        print("데이터 수집에 실패했습니다.")