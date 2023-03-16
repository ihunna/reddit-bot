from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui


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



import requests,random,time,json,csv
from bs4 import  BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor,as_completed
from config import proxies
from utils import generate_sensor_data,solve_captcha,handle_email
from actions import login,boost_karma

def main():
    print(f"\nhow many accounts to want to create")
    limit = input("Enter count: ").strip()
    while limit == "" or not limit.isdigit():
        limit = input("Enter count: ").strip()
    limit = int(limit)

    boost_count  = input("Enter upvote action count: ").strip()
    while  boost_count  == "" or not  boost_count .isdigit():
         boost_count  = input("Enter count: ").strip()
    boost_count  = int( boost_count )

    print(f"\nwhat subreddit do you want to use for karma boosting?")
    sub_reddit = input("Enter subreddit: ").strip()
    while sub_reddit == "" or sub_reddit.isdigit():
        sub_reddit = input("Please enter subreddit: ").strip()

    cookies = []
    accounts = []
    max = limit // 2 if limit > 1 else limit
    with ThreadPoolExecutor(max_workers=limit) as executor:
        print("\n==================================creating accounts==================================\n")
        
        kwargs = [{
            "url": "https://www.reddit.com/register",
            "proxies":random.choice(proxies)
        }for _ in range(limit)]

        futures = []
        for kwargs in kwargs:
            future = executor.submit(generate_account, **kwargs)
            futures.append(future)

        for future in as_completed(futures):
            result = future.result()
            if not result[0]:
                print(result[1])
                continue
            accounts.append(result[1])
            cookies.append(result[2])
        
        with open('cookies/cookies.json','r+',encoding='utf-8-sig') as u_cookies:
            cookies_file = json.load(u_cookies)
            cookies_file["data"] += cookies 
            u_cookies.seek(0)
            u_cookies.truncate()
            json.dump(cookies_file,u_cookies,ensure_ascii=False,indent=4)
        
        with open('accounts.csv','a',encoding='utf-8-sig', newline='') as f:
            for account in accounts:
                writer = csv.writer(f)
                writer.writerow(account)
                
        if len(cookies) > 0:
            print("\n==================================commencing karma boosting==================================\n")
            
            while boost_count > 0:                
                kwargs = [{
                    "cookies":cookie["cookies"],
                    "headers":cookie["headers"],
                    "sub_reddit":sub_reddit,
                    "token":cookie["user_details"]["access_token"]["token"],
                    "username":cookie["user_details"]["username"],
                    "proxies":random.choice(proxies)
                }for cookie in cookies]

                with ThreadPoolExecutor(max_workers=len(cookies)) as executor:
                    futures = []
                    for kwargs in kwargs:
                        future = executor.submit(boost_karma, **kwargs)
                        futures.append(future)

                    for future in as_completed(futures):
                        result = future.result()
                        if result[0]:print(result[1])
                        else:print(result[1])
                boost_count -= 1
                time.sleep(600)

def generate_account(url="",proxies={}):
    try:
        email = handle_email(type="get_email",email_type=random.choice(["gmail.com","outlook.com"]))
        if not email[0]:
            return False,[]
        email,task_id = email[1]["mail"],email[1]["id"]
        password = generate_sensor_data(type="password")

        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': proxies["http"],
            'sslProxy': proxies["http"],
        })

        Options.Proxy = proxy
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        time.sleep(10)
        csrf = bs(driver.page_source,"html.parser")
        csrf_token = csrf.find('form',id="globals").find('input',attrs={'name': 'csrf_token'})['value']
        print(f'csrf_token: {csrf_token}')


        reg_form = ui.WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'form[action="/register"]')))
        
        reg_email = reg_form.find_element(By.NAME,"email")
        time.sleep(2)
        reg_email.send_keys(email)

        sub_btn = driver.find_element(By.CSS_SELECTOR,'button[type="submit"]')
        time.sleep(2)
        sub_btn.click()

        u_div = ui.WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div[class="Onboarding__usernameWrapper"]')))
        usernames = [username.get_attribute("data-username") for username in u_div.find_elements(By.TAG_NAME,"a")]
        username = random.choice(usernames)

        user_details = {
            "username":username,
            "password":password,
            "email":email,
            "csrf_token":csrf_token,
            "email_verified":True
            }

        reg_username = driver.find_element(By.NAME,"username")
        time.sleep(2)
        reg_username.send_keys(username)

        reg_password = driver.find_element(By.NAME,"password")
        time.sleep(2)
        reg_password.send_keys(password)

        capt_res =  solve_captcha(url="https://www.reddit.com/account/register/",
                      site_key="6LeTnxkTAAAAAN9QEuDZRpn90WwKk_R1TRW_g-JC")
        if not capt_res[0]:
            return False,f"error: {capt_res[1]}",[]
        print(f"captcha solved on {username}")
        g_response = capt_res[1]

        time.sleep(2)
        driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')
        driver.execute_script("""document.getElementById("g-recaptcha-response").innerHTML = arguments[0]""", g_response)
        driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="none";')

        time.sleep(2)
        reg_password.send_keys(Keys.RETURN)

        time.sleep(10)
        msg = handle_email(type="read_mail",task_id=f"{task_id}",ans_type="TEXT")
        i = 0
        while "WAIT" and i < 2:
            msg = handle_email(type="read_mail",task_id=f"{task_id}",ans_type="TEXT")
            i += 1
            time.sleep(10)

        print(f"account created on {username}, verifying email")
        if not msg[0] or "WAIT" in msg[1]:
            user_details["email_verified"] = False

        if not user_details["email_verified"]: print(f"email verification unsuccessful on {username}")
        else:
            link = bs(msg[1],"html.parser").find("a",class_="link c-white")["href"]
            driver.get(str(link))
            print(f"email verification successful on {username}")
        
        print(f"account verification successful {email},{username},{password}")
        time.sleep(5)

        cookies = {}
        for cookie in driver.get_cookies():
            cookies[cookie["name"]] = cookie["value"]

        headers = {
                'authority': 'www.reddit.com',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.reddit.com',
                'referer': 'https://www.reddit.com/account/register/?mobile_ui=on&experiment_mweb_google_sso_gis_parity=enabled&experiment_mwebshreddit_onetap_auto=enabled&experiment_mwebshreddit_am_modal_design_update=enabled',
                'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
            }

        loggedIn = login(cookies=cookies,
                      headers=headers,
                      username=username,
                      password=password,
                      token = csrf_token,
                      proxies=proxies)
                
        if loggedIn[0]:
            user_details.update(loggedIn[1]["user_details"])
            cookies ={
            "cookies":loggedIn[1]["cookies"],
            "headers":loggedIn[1]["headers"],
            "user_details":user_details
            }
            print(loggedIn[2])
        else:print(f'{loggedIn[2]} because {loggedIn[1]}')
        

        return True,[email,username,password],cookies
    
    except Exception as error:
        return False,error,[]




def register():
    try:
        cookies = {}

        email = handle_email(type="get_email",email_type=random.choice(["gmail.com","outlook.com"]))
        if not email[0]:
            print(f"error:{email[1]}")
            return False,[]
        email,task_id = email[1]["mail"],email[1]["id"]

        with requests.Session() as session:
            session.proxies.update(random.choice(proxies))

            csrf = session.get('https://www.reddit.com/account/register')
            csrf = bs(csrf.text,'html.parser')
            csrf_token = csrf.find('form',id="globals").find('input',attrs={'name': 'csrf_token'})['value']
            print(f'csrf_token: {csrf_token}')

            session.headers.update({
                'authority': 'www.reddit.com',
                'content-length': '77',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.reddit.com',
                'referer': 'https://www.reddit.com/account/register/?mobile_ui=on&experiment_mweb_google_sso_gis_parity=enabled&experiment_mwebshreddit_onetap_auto=enabled&experiment_mwebshreddit_am_modal_design_update=enabled',
                'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
            })

            data = {
                'csrf_token': f'{csrf_token}',
                'email': f'{email}',
            }
            check_email = session.post('https://www.reddit.com/check_email',data=data)
            if check_email.status_code != 200:return False,f"error with email: {check_email.text}"

            session.headers.pop("content-type")          
            session.headers.pop("content-length")

            usernames = session.get('https://www.reddit.com/api/v1/generate_username.json').json()
            if "usernames" in usernames.keys():
                username = random.choice(usernames['usernames'])
            else:print(f"error obtaining username: {usernames}")
            password = generate_sensor_data(type="password")

            session.headers.update({
                'content-length': '75',
                'content-type': 'application/x-www-form-urlencoded'
            })

            data = {
                'csrf_token': f'{csrf_token}',
                'user': f'{username}',
            }
            check_username = session.post('https://www.reddit.com/check_username',data=data)
            if check_username.status_code != 200:return False,f"error with username: {check_username.text}"

            user_details = {"username":username,"password":password,"email":email}

            capt_res =  solve_captcha(url="https://www.reddit.com/account/register/",
                      site_key="6LeTnxkTAAAAAN9QEuDZRpn90WwKk_R1TRW_g-JC")
            if not capt_res[0]:
                print(f"error: {capt_res[1]}")
                return False,[]
            print(f"captcha solved on {username}")
            capt_res = capt_res[1]
            
            session.headers.update({
                'content-length': '1544',
                'content-type': 'application/x-www-form-urlencoded'
            })
            
            data = {
                'app_name': 'mweb',
                'csrf_token': f'{csrf_token}',
                'g-recaptcha-response': f'{capt_res}',
                'password': f'{password}',
                'dest': 'https://www.reddit.com/',
                'lang': 'en-GB',
                'username': f'{username}',
                'email': f'{email}',
            }
            flow = session.post('https://www.reddit.com/account/register',data=data)

            if flow.status_code == 200:
                session.headers.pop("content-type")
                session.headers.pop("content-length")
                flow = session.get('https://www.reddit.com')

                loggedIn = login(cookies=session.cookies.get_dict(),
                      headers=session.headers,
                      username=username,
                      password=password,
                      token = csrf_token,
                      proxies=session.proxies)
                
                if loggedIn[0]:
                    user_details.update(loggedIn[1]["user_details"])
                    cookies ={
                    "cookies":loggedIn[1]["cookies"],
                    "headers":loggedIn[1]["headers"],
                    "user_details":user_details
                    }
                    print(loggedIn[2])
                else:print(f'{loggedIn[2]} because {loggedIn[1]}')

                session.headers.update({
                    "authorization":f"Bearer {user_details['access_token']['token']}",
                    "content-type":"application/json"
                    })
                json_data = {
                    'gender': 'FEMALE',
                    'submitStatus': True,
                }
                gender = session.post('https://www.reddit.com/counters/gender-collection',json=json_data)
                if  gender.status_code == 200:
                    print(f"gender chosen on {username}")
                else:print(f"couldn't choose gender: {gender.text}")

                params = {
                    'redditWebClient': 'mweb2x',
                    'layout': 'classic',
                    'action': 'sub',
                    'api_type': 'json',
                    'sr': 't5_2qhn3,t5_2rxue,t5_2s3i3,t5_31wlf,t5_2u06v,t5_2yo2z,t5_2qwzb,t5_2r6jl,t5_3g7sw,t5_2s8o5,t5_3ec0o,t5_2tnuv,t5_34m7m,t5_2teac,t5_2qnlg,t5_2tma3,t5_2ra25,t5_2t30a,t5_3bhx8,t5_2qh33,t5_2y1j5,t5_2xbrg,t5_2vi9f,t5_2wfjv,t5_2u2bh,t5_3blco,t5_34o9s,t5_2t0no,t5_2u04j,t5_2qmsf,t5_2y8kx,t5_2t79l,t5_2wn4a,t5_2sa9a,t5_2sgxv,t5_2s1me,t5_2t03a,t5_2sej3,t5_2rrd8,t5_2xxyj,t5_2ti4h,t5_2szyo,t5_2tycb,t5_2qh0u,t5_2qqjc,t5_2qhsa,t5_2qh1i,t5_310rm,t5_2tp0t,t5_2qjpg,t5_2vegg,t5_3gcwj,t5_2v2cd,t5_2s7tt,t5_3gl3k,t5_3deqz,t5_2y3e1,t5_2qh72,t5_2vc9u,t5_37xo2,t5_2rww2,t5_3jayp,t5_3jiim,t5_2qrwc,t5_3m2bs,t5_30msm,t5_2uctp,t5_2r0cn,t5_2s6ky,t5_2s30g,t5_2rxrw,t5_2qhb1,t5_2s4kl,t5_3aeuk,t5_2w7mz,t5_2qhnh',
                    'app': '2x-client-production',
                }

                sub = session.post('https://oauth.reddit.com/api/subscribe', params=params)
                if  sub.status_code == 200:
                    params = {
                        'redditWebClient': 'mweb2x',
                        'layout': 'classic',
                        'sort': 'mine/subscriber',
                        'limit': '100',
                        'sr_detail': 'true',
                        'api_type': 'json',
                        'raw_json': '1',
                        'app': '2x-client-production',
                    }
                    sub = session.get('https://oauth.reddit.com/subreddits/mine/subscriber.json', params=params)
                    if  sub.status_code == 200:print(f"subscribed to subreddits on {username}")
                    else:return False,f"couldn't subscribed to subreddits: {sub.text}"
                else:print(f"couldn't subscribed to subreddits: {sub.text}")
                
                
                print(f"account created, verying email address: {email} {username} {password}")
                time.sleep(10)

                msg = handle_email(type="read_mail",task_id=f"{task_id}",ans_type="TEXT")
                i = 0
                while "WAIT" in msg[1] and i < 2:
                    msg = handle_email(type="read_mail",task_id=f"{task_id}",ans_type="TEXT")
                    if not msg[0]:
                        return False,f"error: {msg[1]}"
                    i += 1

                link = bs(msg[1],"html.parser").find("a",class_="link c-white")["href"]
                print(link)
                token = link.split('?')[0].split('/')[4]

                session.headers.update({
                    'referer': f'{link}'
                })
                session.headers.pop("authorization")

                params = {
                    'redditWebClient': 'mweb2x',
                    'layout': 'classic',
                    'allow_over18': '',
                    'app': '2x-client-production',
                    'obey_over18': 'true',
                    'raw_json': '1',
                }
                json_data = {}
                
                verify =session.post(
                    f"https://www.reddit.com/api/v1/verify_email/{token}.json",
                    params=params,
                    json=json_data,
                )

                if verify.status_code != 200:return False,f"error creating account {verify.text}"
                print(verify.json())
                # assert flow.status_code == 200

                # with open("test.html","w",encoding="utf-8") as f:
                #     flow = bs(flow.text,"html.parser")
                #     f.write(flow.prettify())

                print("\n------------account created and verification successful---------------")
                print(f"(email: {email}, username: {username}, password: {password})\n")
                return True,[email,username,password],cookies
            else:
                return False,f"unable to register account: {flow.json()}",[]
    except Exception as error:
        print(error)
        return False,error,[]



if __name__ == "__main__":
    main()
