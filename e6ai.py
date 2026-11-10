import os
import sys
import re
import requests
import json

from urllib.parse import urlparse

login = ""
api_host = "https://e6ai.net"
api_key = ""

if len(sys.argv) < 2:
    print("Please provide an artist/director name, or any single tag. Example: >python e6ai.py \"loona_(helluva_boss)\"")

    sys.exit(1)
else:
    tag = sys.argv[1]

outputDir = f"{os.getcwd()}/e6ai_downloads/{tag}"

headers = {"user-agent": f"{login}_dl/0.1"}

def get_urls(jsonData):
    urlList = []

    for post in jsonData["posts"]:
        url = post["file"]["url"]

        urlList.append(url)

    return urlList

def get_json_data(page):
    api_url = f"{api_host}/posts.json"

    params = {
        "login": login,
        "api_key": api_key,
        "limit": "100",
        "tags": tag,
        "page": page
    }

    response = requests.get(api_url, params=params, headers=headers)

    posts = response.text

    jsonData = json.loads(posts)

    return jsonData

def download_files(jsonData, currentPostCount):
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    for post in jsonData["posts"]:
        url = post["file"]["url"]

        fileName = f"{outputDir}/{os.path.basename(urlparse(url).path)}"

        if os.path.exists(fileName):
            print(f"File exists. Skipping {fileName}")
        else:
            post_id = post["id"]

            if is_url(url):
                record_json(post, fileName)

                print(f"Downloading file {currentPostCount} of {postCount} [ID {post_id}]: {url}")

                response = requests.get(url)

                with open(fileName, mode="wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
            else:
                print(f"Skipping post {post_id}, no valid file URL found!")

        currentPostCount += 1

def record_json(post, fileName):
    fileNameJson = re.sub(r"(.*)\..*", "\\1.json", fileName)

    if os.path.exists(fileNameJson):
        print(f"File exists. Skipping {fileNameJson}")
    else:
        with open(fileNameJson, "a", encoding="utf-8") as file:
            file.write(json.dumps(post, indent=4))

def get_post_count():
    api_url = f"{api_host}/tags.json"

    params = {
        "search[name_matches]": tag
    }

    response = requests.get(api_url, params=params, headers=headers)

    tagData = response.text

    jsonTagData = json.loads(tagData)

    postCount = jsonTagData[0]["post_count"]

    return postCount

def is_url(url):
    try:
        result = urlparse(url)

        return all([result.scheme, result.netloc])
    except ValueError:
        return False

postCount = get_post_count()

print(f"{postCount} posts found, starting downloads...")

page = 1

currentPostCount = 1

while page:
    jsonData = get_json_data(page)

    download_files(jsonData, currentPostCount)

    if len(jsonData["posts"]) == 0:
        page = 0

        print("All done!")
    else:
        page = f"b{jsonData["posts"][-1]["id"]}"