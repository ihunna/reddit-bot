import random,string,os,time,requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup as bs 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType


options = Options()
options.add_argument('--start-maximized')
options.add_argument('--no-sandbox')
options.add_argument("--mute-audio")
options.add_argument("--log-level=OFF")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--disable-gpu')
options.add_argument('disable-infobars')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
options.add_argument("--disable-extensions")
options.add_argument("--headless")

from capmonster_python import RecaptchaV2Task


load_dotenv()

def generate_sensor_data(type="password"):
    if type == "password":
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    elif type == "csrf":
        return ''.join(random.choices(string.digits + string.ascii_letters, k=32)).lower()

    elif type == "gt":
        return ''.join(random.choices(string.digits, k=19))

    elif type == "random_string":
        return  ''.join(random.choices('_' + string.digits + string.ascii_letters + '_', k=30))
    
def load_proxies():
    with open('proxies.txt','r') as pro_file:
        proxies = []
        for proxy in pro_file:
            proxy = proxy.replace("\n","").split(":")
            proxy = f"{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
            proxies.append({
                "http":f"http://{proxy}",
                "https":f"http://{proxy}"
            })
    return proxies

def solve_captcha(url="",site_key=""):
    try:
        api_key = os.getenv("CAPI_KEY")
        capmonster = RecaptchaV2Task(api_key)
        task_id = capmonster.create_task(url,site_key)
        result = capmonster.join_task_result(task_id).get("gRecaptchaResponse")
        return True,result
    except Exception as error:
        return False,error


def handle_email(type="get_email",site="reddit.com",email_type="gmail.com",sender="reddit.com",ans_type="JSON",subject="Verify your Reddit email address",task_id=""):
    try:
        api_key = os.getenv("MAPI_KEY")
        if type == "get_email":
            email = requests.get(f"http://api.kopeechka.store/mailbox-get-email?site={site}&mail_type={email_type}&sender={sender}&regex=&token={api_key}&soft=&investor=&type={ans_type}&subject={subject}&clear=&api=2.0")
            if email.status_code == 200:
                return True,email.json()
            return False,email.text
        elif type == "read_mail":
            mail = requests.get(f"http://api.kopeechka.store/mailbox-get-message?full=1&id={task_id}&token={api_key}&type={ans_type}&api=2.0")
            e_mail = mail.text if ans_type == "TEXT" else mail.json()
            if mail.status_code == 200:
                return True,e_mail
            return False,e_mail
    except Exception as error:
        return False,{"error":error}

def get_cookies(url,proxies={}):
    print("\n---------------------------getting guest token---------------------------")

    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': proxies["http"],
        'sslProxy': proxies["http"],
    })

    Options.Proxy = proxy
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)
    
    cookies = {}
    for cookie in driver.get_cookies():
        cookies[cookie["name"]] = cookie["value"]
    driver.quit()
    cookies['at_check'] = 'true'

    print(f'guest token {cookies["gt"]}')
    return cookies
