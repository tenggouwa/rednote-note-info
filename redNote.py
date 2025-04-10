import time
import json
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

def extract_note_detail(browser, url):
    browser.get(url)
    time.sleep(2)

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    # 标题
    title_tag = soup.find('div', id='detail-title')
    title = title_tag.get_text(strip=True) if title_tag else ''

    # 描述
    desc_tag = soup.find('div', id='detail-desc')
    description = desc_tag.get_text(strip=True) if desc_tag else ''

    # 发布时间
    date_tag = soup.find('span', class_='date')
    publish_date = date_tag.get_text(strip=True) if date_tag else ''

    # 图片
    img_tags = soup.find_all('img', class_='note-slider-img')
    image_urls = [img.get('src') for img in img_tags if img.get('src')]

    # 👍 点赞数
    like_span = soup.select_one('span.like-wrapper span.count')
    likes = like_span.get_text(strip=True) if like_span else '0'

    # ⭐ 收藏数
    collect_span = soup.select_one('span.collect-wrapper span.count')
    collects = collect_span.get_text(strip=True) if collect_span else '0'

    # 💬 评论数
    comment_span = soup.select_one('span.chat-wrapper span.count')
    comments = comment_span.get_text(strip=True) if comment_span else '0'

    return {
        'detail_title': title,
        'description': description,
        'publish_date': publish_date,
        'images': image_urls,
        'likes': likes,
        'collects': collects,
        'comments': comments
    }

def scrape_notes(keyword='露营', max_scroll=6, max_notes=10):
    url = f'https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_explore_feed'
    
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")

    browser = uc.Chrome(options=options)
    browser.get(url)

    print("🔐 请在弹出的浏览器中登录小红书，登录完成后按回车继续...")
    input("✅ 登录完成后按回车...")

    # 滚动加载页面内容
    for _ in range(max_scroll):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    soup = BeautifulSoup(browser.page_source, 'html.parser')
    cards = soup.find_all('section', class_='note-item')

    print(f"📦 搜索页共找到 {len(cards)} 条内容")

    results = []

    for idx, card in enumerate(cards):
        if len(results) >= max_notes:
            break
        try:
            # 列表页：提取标题、封面、作者、链接
            title_tag = card.find('a', class_='title')
            title = title_tag.get_text(strip=True) if title_tag else ''

            img_tag = card.find('a', class_='cover').find('img')
            image = img_tag['src'] if img_tag else ''

            author_span = card.find('span', class_='name')
            author = author_span.get_text(strip=True) if author_span else ''

            link_tag = card.find('a', class_='cover')
            relative_url = link_tag['href'] if link_tag else ''
            link = 'https://www.xiaohongshu.com' + relative_url

            note = {
                'title': title,
                'image': image,
                'author': author,
                'link': link
            }

            print(f"➡️ 抓取详情页 {idx + 1}: {title}")
            detail = extract_note_detail(browser, link)
            note.update(detail)

            results.append(note)

        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            continue

    browser.quit()

    return results

if __name__ == "__main__":
    data = scrape_notes(keyword='露营', max_scroll=20, max_notes=150)

    with open('xhs_camping_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 共抓取 {len(data)} 条笔记，已保存至 xhs_camping_data.json")