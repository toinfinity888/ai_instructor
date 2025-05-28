import requests
from bs4 import BeautifulSoup
from typing import Dict

def parser_post_page(url) -> Dict:
    try:
        response = requests.get(url)
        print(response.status_code)
    except Exception as e:
        print(f"Error: {e}")
        
    soup = BeautifulSoup(response.text, 'lxml')

    title_tag = soup.find('div', class_='lia-message-subject')
    title = title_tag.get_text(strip=True) if title_tag else 'No Title'

    main_post = soup.find('div', class_='lia-message-body-content')
    question = main_post.get_text(strip=True) if main_post else 'No Content'

    replies = []
    reply_posts = soup.find_all('div', class_='lia-message-body-content')[1:]
    for reply in reply_posts:
        replies.append(reply.get_text(strip=True))

    return {
        'title': title,
        'question': question,
        'answer': replies
    }