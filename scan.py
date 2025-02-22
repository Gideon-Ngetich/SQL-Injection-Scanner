import requests
from bs4 import BeautifulSoup
import sys
from urllib.parse import urljoin

s = requests.session()
s.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"

def get_forms(url):
    soup = BeautifulSoup(s.get(url).content, "html.parser")
    return soup.find_all("form")

def form_details(form):
    detailsOfForm = {}
    action = form.attrs.get("action")
    method = form.attrs.get("method", "get")
    inputs = []

    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append({
            "type": input_type,
            "name": input_name,
            "value": input_value,
        })
    
    detailsOfForm['action'] = action
    detailsOfForm['method'] = method
    detailsOfForm['inputs'] = inputs
    return detailsOfForm

def vulnerable(response):
    errors = {"quoted string not properly terminated",
              "unclosed quotation mark after the character string",
              "you have an error in your SQL syntax"}
    for error in errors:
        if error in response.content.decode().lower():
            return True
    return False

def sql_injection_scan(url):
    forms = get_forms(url)
    print(f"[+] Detected {len(forms)} forms on {url}.")

    for form in forms:
        details = form_details(form)
        
        if details is None:
            continue
        
        for i in "\"'":
            data = {}
            for input_tag in details.get("inputs", []):
                if input_tag["type"] == "hidden" or input_tag.get("value"):
                    data[input_tag['name']] = input_tag.get("value", "") + i
                elif input_tag["type"] != "submit":
                    data[input_tag['name']] = f"test{i}"
            print(url)

            action = details['action']
            post_url = urljoin(url, action)
            if details["method"].lower() == "post":
                res = s.post(post_url, data=data)
            elif details["method"].lower() == "get":
                res = s.get(post_url, params=data)
            
            if vulnerable(res):
                print("SQL injection attack vulnerability in link: ", post_url)
            else:
                print("NO SQL INJECTION ATTACK VULNERABILITY DETECTED")

if __name__ == "__main__":
    urlToBeChecked = "https://www.hackthissite.org/"
    sql_injection_scan(urlToBeChecked)
