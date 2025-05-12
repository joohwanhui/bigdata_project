from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_monday_webtoons(chromedriver_path, headless=True):
    # ChromeOptions 설정
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    wait = WebDriverWait(driver, 10)

    # 네이버 웹툰 요일별 페이지 접속
    driver.get("https://comic.naver.com/webtoon/weekday.nhn")
    # ‘월요일’ 섹션이 로드될 때까지 대기
    sections = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.col_inner")))
    monday_section = sections[0]  # 0: 월, 1: 화, …

    results = []
    items = monday_section.find_elements(By.CSS_SELECTOR, "li")
    for item in items:
        # 제목 및 상세 URL
        title_el = item.find_element(By.CSS_SELECTOR, "a.title")
        title = title_el.text.strip()
        detail_url = title_el.get_attribute("href")

        # 썸네일 이미지 URL
        thumb_url = item.find_element(By.TAG_NAME, "img").get_attribute("src")

        # 상세 페이지 이동 → 작가명, 평점 수집
        driver.get(detail_url)
        author = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.wrt_nm"))).text.strip()
        rating = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.rating_type strong"))).text.strip()

        results.append({
            "title": title,
            "thumbnail": thumb_url,
            "author": author,
            "rating": rating
        })

        # 리스트 페이지로 돌아가기
        driver.back()
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.col_inner")))

    driver.quit()
    return results

if __name__ == "__main__":
    # 1) chromedriver_path를 실제 경로로 바꿔주세요.
    # 2) pip install selenium
    chromedriver_path = "/path/to/chromedriver"
    data = scrape_monday_webtoons(chromedriver_path)

    for entry in data:
        print(f"제목: {entry['title']}")
        print(f"썸네일: {entry['thumbnail']}")
        print(f"작가: {entry['author']}")
        print(f"평점: {entry['rating']}")
        print("="*40)
