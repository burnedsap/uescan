import requests
from bs4 import BeautifulSoup

DOC_URL = "https://docs.google.com/document/d/e/2PACX-1vRVM9z4ZMZdsmEygLvEAe_jYWzSyvBRPvQu2xPOs2EGXRZPU9x310YMMcUQie4RLHb_1L_jbmsMKwUp/pub"

def fetch_google_doc_body(url):
    print("📥 Fetching Google Doc...")
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Error: {response.text[:300]}")
        raise Exception("Failed to fetch Google Doc")

    soup = BeautifulSoup(response.text, 'html.parser')
    body = soup.find('body')
    return body.decode_contents()

def replace_index_body(content_html):
    print("🔧 Updating index.html...")
    with open("index.html", "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Replace the body contents
    body_tag = soup.find('body')
    if body_tag:
        body_tag.clear()
        body_tag.append(BeautifulSoup(content_html, 'html.parser'))

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(str(soup.prettify()))

    print("✅ index.html updated.")

if __name__ == "__main__":
    new_content = fetch_google_doc_body(DOC_URL)
    replace_index_body(new_content)
