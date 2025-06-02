from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time

def crawl_letterboxd(keyword):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get("https://letterboxd.com/")
    search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.results')))
    first_result = driver.find_element(By.CSS_SELECTOR, 'ul.results li a[href*="/film/"]')
    movie_url = first_result.get_attribute('href')
    driver.get(movie_url)

    title = driver.find_element(By.CSS_SELECTOR, "h1.headline-1.primaryname").text
    year = driver.find_element(By.CSS_SELECTOR, "div.releaseyear a").text

    try:
        director = driver.find_element(By.CSS_SELECTOR, "p.credits span.directorlist a").text
    except:
        director = "N/A"

    try:
        description = driver.find_element(By.CSS_SELECTOR, ".truncate").text
    except:
        description = ""

    poster = driver.find_element(By.CSS_SELECTOR, 'a[data-js-trigger="postermodal"]').get_attribute("href")

    try:
        rating_element = driver.find_element(By.CSS_SELECTOR, "a.display-rating.-highlight")
        average_rating = rating_element.text
        tooltip_text = rating_element.get_attribute("data-original-title")
        match = re.search(r'based on ([\d,]+)', tooltip_text)
        total_ratings = match.group(1).replace(',', '') if match else "0"
    except:
        average_rating = "N/A"
        total_ratings = "N/A"

    # 評分分布
    rating_distribution = {}
    try:
        bars = driver.find_elements(By.CSS_SELECTOR, 'a.tooltip')
        for bar in bars:
            tooltip = bar.get_attribute('data-original-title')
            match = re.search(r'([\d,]+)&nbsp;(.+?) ratings', tooltip)
            if match:
                count = int(match.group(1).replace(',', ''))
                star_text = match.group(2).strip()

                if "½" in star_text:
                    stars = str(star_text.count("★")) + ".5"
                else:
                    stars = str(star_text.count("★")) + ".0"

                rating_distribution[stars] = count
    except:
        rating_distribution = {}

    # 評論區
    try:
        reviews_url = movie_url.rstrip('/') + "/reviews/"
        driver.get(reviews_url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.listitem")))
    except:
        reviews = []
    else:
        review_elements = driver.find_elements(By.CSS_SELECTOR, "div.listitem")[:10]
        reviews = []

        for item in review_elements:
            try:
                reviewer_id = item.find_element(By.CSS_SELECTOR, "a.displayname").text
                date = item.find_element(By.CSS_SELECTOR, "time.timestamp").get_attribute("datetime")
                rating_el = item.find_element(By.CSS_SELECTOR, "span.rating").get_attribute("class")
                rating_match = re.search(r"rated-(\d+)", rating_el)
                rating = float(rating_match.group(1)) / 2 if rating_match else None
                content = item.find_element(By.CSS_SELECTOR, "div.body-text").text.strip()
                like_data = item.find_element(By.CSS_SELECTOR, ".review-actions p.like-link-target")
                likes = int(like_data.get_attribute("data-count")) if like_data else 0
                reviews.append({
                    "reviewer_id": reviewer_id,
                    "review_date": date,
                    "rating": rating,
                    "content": content,
                    "likes": likes
                })
            except:
                continue

    driver.quit()
    return {
        "title": title,
        "year": year,
        "director": director,
        "description": description,
        "poster": poster,
        "average_rating": average_rating,
        "total_ratings": total_ratings,
        "rating_distribution": rating_distribution,
        "reviews": reviews
    }
