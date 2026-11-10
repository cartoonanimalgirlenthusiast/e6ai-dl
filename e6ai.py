import os
import sys
import re
import requests
import json
import configparser
import time

from urllib.parse import urlparse

config = configparser.RawConfigParser()
config.read("config.txt")

api_host = "https://e6ai.net"
login = config.items("CREDENTIALS")[0][1]
api_key = config.items("CREDENTIALS")[1][1]

if len(sys.argv) < 2:
    print("Please provide an artist/director name, or any single tag. Example: >python e6ai.py \"loona_(helluva_boss)\"")

    sys.exit(1)
else:
    tag = sys.argv[1]

output_dir = f"{os.getcwd()}/e6ai_downloads/{tag}"

headers = {"user-agent": f"{login}_dl/0.1"}

def get_urls(json_data):
    url_list = []

    for post in json_data["posts"]:
        url = post["file"]["url"]

        url_list.append(url)

    return url_list

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

    json_data = json.loads(posts)

    return json_data

def download_files(json_data, current_post_count):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for post in json_data["posts"]:
        url = post["file"]["url"]

        file_name = f"{output_dir}/{os.path.basename(urlparse(url).path)}"

        if os.path.exists(file_name):
            print(f"File exists. Skipping {file_name}")
        else:
            post_id = post["id"]

            if is_url(url):
                record_json(post, file_name)

                print(f"Downloading file {current_post_count} of {post_count} [ID {post_id}]: {url}")

                response = requests.get(url)

                with open(file_name, mode="wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
            else:
                print(f"Skipping post {post_id}, no valid file URL found!")

        current_post_count += 1

    return current_post_count

def record_json(post, file_name):
    file_name_json = re.sub(r"(.*)\..*", "\\1.json", file_name)

    if os.path.exists(file_name_json):
        print(f"File exists. Skipping {file_name_json}")
    else:
        with open(file_name_json, "a", encoding="utf-8") as file:
            file.write(json.dumps(post, indent=4))

def get_post_count():
    api_url = f"{api_host}/tags.json"

    params = {
        "search[name_matches]": tag
    }

    response = requests.get(api_url, params=params, headers=headers)

    tag_data = response.text

    json_tag_data = json.loads(tag_data)

    post_count = json_tag_data[0]["post_count"]

    return post_count

def is_url(url):
    try:
        result = urlparse(url)

        return all([result.scheme, result.netloc])
    except ValueError:
        return False

post_count = get_post_count()

print(f"{post_count} posts found, starting downloads...")

page = 1

current_post_count = 1

while page:
    start_time = time.time()

    json_data = get_json_data(page)

    current_post_count = download_files(json_data, current_post_count)

    if len(json_data["posts"]) == 0:
        page = 0

        print("All done!")
    else:
        page = f"b{json_data["posts"][-1]["id"]}"

    end_time = time.time()

    elapsed_time = 5 if end_time - start_time > 5 else end_time - start_time

    time.sleep(5 - elapsed_time)