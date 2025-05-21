import requests
from bs4 import BeautifulSoup

DOC_URL = "https://docs.google.com/document/d/e/2PACX-1vRVM9z4ZMZdsmEygLvEAe_jYWzSyvBRPvQu2xPOs2EGXRZPU9x310YMMcUQie4RLHb_1L_jbmsMKwUp/pub"
INDEX_HTML = "index.html"

def fetch_google_doc_body(doc_url):
    print("Fetching Google Doc...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(doc_url, headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print("Response Text Preview:")
        print(response.text[:500])
        raise Exception("Failed to fetch Google Doc")

    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find("div", {"id": "contents"})
    if not content_div:
        raise Exception("Could not find content in the published doc")
    return content_div

def update_index_html(new_content):
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    old_body = soup.body
    old_body.clear()
    for tag in new_content.contents:
        old_body.append(tag)

    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

    print("✅ index.html updated.")

if __name__ == "__main__":
    try:
        new_content = fetch_google_doc_body(DOC_URL)
        update_index_html(new_content)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
