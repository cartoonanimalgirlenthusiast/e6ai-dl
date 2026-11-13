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

headers = {"user-agent": f"{login}_dl/0.1"}

rate_limit_time = 2

def get_json_data(page):
    api_url = f"{api_host}/posts.json"

    params = {
        "login": login,
        "api_key": api_key,
        "limit": "320",
        "tags": tag,
        "page": page
    }

    response = requests.get(api_url, params=params, headers=headers)

    posts = response.text

    json_data = json.loads(posts)

    return json_data

def download_files(json_data, post_count, current_post_count):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for post in json_data["posts"]:
        url = post["file"]["url"]

        post_id = post["id"]

        if is_url(url):
            print(f"Downloading file {current_post_count} of {post_count} [Tag: {tag}] [ID {post_id}]: {url}")

            download_file(post)

            record_json(post)
        else:
            print(f"Skipping post {post_id}, no valid file URL found!")

        current_post_count += 1

    return current_post_count

def download_file(post):
    file_name = f"{output_dir}/{post["file"]["md5"]}.{post["file"]["ext"]}"

    if os.path.exists(file_name):
        print(f"File exists. Skipping {file_name}")
    else:
        url = post["file"]["url"]

        response = requests.get(url)

        with open(file_name, mode="wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

def record_json(post):
    file_name = f"{output_dir}/{post["file"]["md5"]}.json"

    if os.path.exists(file_name):
        print(f"File exists. Skipping {file_name}")
    else:
        with open(file_name, "a", encoding="utf-8") as file:
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

def get_directors():
    page = 1
 
    api_url = f"{api_host}/tags.json"

    params = {
        "login": login,
        "api_key": api_key,
        "limit": "320",
        "search[category]": "1",
        "page": page
    }

    response = requests.get(api_url, params=params, headers=headers)

    response_text = response.text

    response_json = json.loads(response_text)

    director_names = []

    total_post_count = 0

    for director in response_json:
        director_names.append(director["name"])

        total_post_count += director["post_count"]

    print(f"Found {len(director_names)} directors with a total of {total_post_count} posts.")

    return director_names

def loop_pages(tag):
    post_count = get_post_count()

    print(f"{post_count} posts found tagged with \"{tag}\", starting downloads...")

    page = 1

    current_post_count = 1

    while page:
        start_time = time.time()

        json_data = get_json_data(page)

        current_post_count = download_files(json_data, post_count, current_post_count)

        if len(json_data["posts"]) == 0:
            page = 0
        else:
            page = f"b{json_data["posts"][-1]["id"]}"

            delay(start_time)

def delay(start_time):
    end_time = time.time()

    elapsed_time = rate_limit_time if end_time - start_time > rate_limit_time else end_time - start_time

    time.sleep(rate_limit_time - elapsed_time)

def is_url(url):
    try:
        result = urlparse(url)

        return all([result.scheme, result.netloc])
    except ValueError:
        return False

if len(sys.argv) < 2:
    print("WARNING: You didn't provide a tag. This will cause the script to download EVERYTHING from the site!")

    inp = input("Continue? [y/N]" or "n")

    if inp.lower() == "n":
        sys.exit(1)

    tags = get_directors()

    output_dir = f"{os.getcwd()}/e6ai_downloads"
else:
    tag = sys.argv[1]

    tags = [tag]

    output_dir = f"{os.getcwd()}/e6ai_downloads/{tag}"

for tag in tags:
    start_time = time.time()

    loop_pages(tag)

    delay(start_time)

print("All done!")