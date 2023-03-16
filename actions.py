import requests,random,json,time
from colorama import init, Fore, Back, Style
from concurrent.futures import ThreadPoolExecutor,as_completed
from config import proxies
from bs4 import BeautifulSoup as bs



def boost_karma(cookies={},headers={},sub_reddit={},token="",username="",proxies={}):
    try:
        headers = {
            'authority': 'oauth.reddit.com',
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': f'Bearer {token}',
            'origin': 'https://www.reddit.com',
            'referer': 'https://www.reddit.com/',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
            'x-reddit-loid': f'{cookies["loid"]}',
            'x-reddit-session': f'{cookies["session"]}',
        }

        params = {
            'redditWebClient': 'mweb2x',
            'layout': 'classic',
            'raw_json': '1',
            'withAds': 'true',
            'subredditName': f'{sub_reddit}',
            'feature': 'link_preview',
            'sr_detail': 'true',
            'allow_over18': '',
            'app': '2x-client-production',
            'obey_over18': 'true',
        }

        posts = requests.get(f'https://oauth.reddit.com/r/{sub_reddit}.json', 
                            params=params, 
                            headers=headers,
                            proxies=proxies)
        
        if posts.status_code != 200 or "data" not in posts.json().keys():
            return False,f"error: couldn't get posts because{posts.text}"
        
        post = random.choice(posts.json()["data"]["children"])
        cmmt = post_comment(cookies=cookies,
                            post_id=post["data"]["name"],
                            text="upvote for upvote",
                            token=token,
                            username=username,
                            proxies=proxies)
        if cmmt[0] is False:return False, cmmt[1]
        else:print(cmmt[1])

        upvt = upvote(cookies=cookies,
                        post_id=post["data"]["name"],
                        token=token,
                        username=username,
                        proxies=proxies)
        if upvt[0]:return True,upvt[1]
        else:return False, upvt[1]
    except Exception as error:
        return False,error


def upvote(cookies={},headers={},post_id="",token="",username="",proxies={}):
    print(f"sending an upvote on {username}")
    try:
        headers = {
            'authority': 'oauth.reddit.com',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': f'Bearer {token}',
            'origin': 'https://www.reddit.com',
            'referer': 'https://www.reddit.com/',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'x-reddit-loid': f'{cookies["loid"]}',
            'x-reddit-session': f'{cookies["session"]}',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        }

        params = {
        'redditWebClient': 'desktop2x',
        'app': 'desktop2x-client-production',
        'raw_json': '1',
        'gilding_detail': '1',
        }

        data = {
            'id': f'{post_id}',
            'dir': '1',
            'api_type': 'json',
        } 
        response = requests.post('https://oauth.reddit.com/api/vote', 
                                 params=params, 
                                 headers=headers, 
                                 data=data,
                                 proxies=proxies)
        
        assert response.status_code == 200
        return True,f"succesfully upvoted {post_id}"
    
    except Exception as error:
        return False, error


def post_comment(cookies={},headers={},post_id="",text="",token="",username="",proxies={}):
    print(f"sending a comment on {username}")
    try:
        headers = {
            'authority': 'oauth.reddit.com',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': f'Bearer {token}',
            'origin': 'https://www.reddit.com',
            'referer': 'https://www.reddit.com/',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'x-reddit-loid': f'{cookies["loid"]}',
            'x-reddit-session': f'{cookies["session"]}',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        }
        
        params = {
            'rtj': 'only',
            'emotes_as_images': 'true',
            'redditWebClient': 'desktop2x',
            'app': 'desktop2x-client-production',
            'raw_json': '1',
            'gilding_detail': '1'
        }

        data = {
            'api_type': 'json',
            'return_rtjson': 'true',
            'thing_id': f'{post_id}',
            'text': f'{text}'
        }

        response = requests.post('https://oauth.reddit.com/api/comment.json',
                                params=params, 
                                headers=headers, 
                                data=data,
                                proxies=proxies)
        flow = response.json()
        if response.status_code == 200 and "json" in flow.keys():
            return False,flow["json"]["errors"]
        
        assert response.status_code == 200
        return True,f"successfully commented on {post_id}"
    except Exception as error:
        return False,error
    

def login(cookies={},headers={},username="",password="",token="",proxies={}):
    try:
        print(f"logging {username} in")
        with requests.Session() as session:
            headers["content-type"] = "application/x-www-form-urlencoded"
            session.cookies.update(cookies)
            session.headers.update(headers)
            session.proxies.update(proxies)
            
            data = {
                'app_name': 'mweb',
                'csrf_token': f'{token}',
                'otp': '',
                'password': f'{password}',
                'dest': 'https://www.reddit.com',
                'username': f'{username}'
            }
            response = session.post('https://www.reddit.com/account/login',data=data)
            if response.status_code == 200 and "dest" in response.json():
                session.get(f"{response.json()['dest']}")
                flow = session.get(f"https://www.reddit.com/user/{username}/")

                data = bs(flow.text,"html.parser")

                data = data.find("script",id="data").string
                start_index = data.find("{")
                end_index = data.rfind("}") + 1
                data = data[start_index:end_index]
                data_dict = json.loads(data)

                with open("test.json","w",encoding="utf-8-sig") as f:
                    json.dump(data_dict,f,ensure_ascii=False,indent=4)
            
                user = {
                    "user_id":data_dict["accounts"][username.lower()]["id"],
                    "profile_id":data_dict["accounts"][username.lower()]["subredditId"],
                    "commentKarma":data_dict["accounts"][username.lower()]["commentKarma"],
                    "karma":data_dict["accounts"][username.lower()]["karma"],
                    "access_token":{
                                    "token":data_dict["session"]["accessToken"],
                                    "expires":data_dict["session"]["expires"]
                                    }
                }

                return True,{"cookies":session.cookies.get_dict(),
                             "headers":dict(session.headers),"user_details":user},f"login successful on {username}"
            else:return False,response.text,f"login unsuccessful on {username}"
    except Exception as error:
        return False,error,f"login unsuccessful on {username}"
    

def send_dm():
    print("\n==================================commencing DM==================================")
    try:
        all_scraped = []
        all_cookies = []

        print(f"\nhow many users do you want to scrape")
        limit = input("Enter count: ").strip()
        while limit == "" or not limit.isdigit():
            limit = input("Enter count: ").strip()
        limit = int(limit)

        print(f"\nwhat subreddit(s) do you want to scrape from?")
        sub_reddits = input("Enter subreddit(s): ").strip()
        while sub_reddits == "" or sub_reddits.isdigit():
            sub_reddits = input("Please enter subreddit(s): ").strip()

        sub_reddits = sub_reddits.strip().split(" ")
        limits = [limit//len(sub_reddits) for _ in range(len(sub_reddits))]
        if sum(limits) < limit:limits[random.randrange(0,len(limits)-1)] += limit - sum(limits)
        sub_reddits = list(zip(sub_reddits,limits))

        with open("cookies/cookies.json","r",encoding="utf-8-sig") as f:
            all_cookies = json.load(f)["data"]

        kwargs =[{
            "cookies":random.choice(all_cookies),
            "sub_reddit":sub_reddit[0],
            "limit":sub_reddit[1],
            "proxies":random.choice(proxies)
        }for sub_reddit in sub_reddits]

        with ThreadPoolExecutor(max_workers=len(sub_reddits)) as executor:
            print("\n----------------------------started scraping accounts-----------------------------")
            futures = []
            for kwargs in kwargs:
                future = executor.submit(scrape_users, **kwargs)
                futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                if result[0]:
                    print(result[1])
                    for scraped in result[2]:
                        if scraped not in all_scraped: all_scraped.append(scraped)
                else:print(result[1])
            print(f"total {len(all_scraped)} users scraped")

        


    except Exception as error:
        return False,error
    

def scrape_users(cookies={},sub_reddit="",limit=0,proxies={}):
    try:
        token = cookies["user_details"]["access_token"]["token"]
        cookies = cookies["cookies"]
        headers = {
            'authority': 'oauth.reddit.com',
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': f'Bearer {token}',
            'origin': 'https://www.reddit.com',
            'referer': 'https://www.reddit.com/',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
            'x-reddit-loid': f'{cookies["loid"]}',
            'x-reddit-session': f'{cookies["session"]}',
        }

        params = {
            'redditWebClient': 'mweb2x',
            'layout': 'classic',
            'id': f'{sub_reddit}',
            'api_type': 'json',
            'raw_json': '1',
            'app': '2x-client-production',
        }

        t_users = requests.get(f'https://oauth.reddit.com/r/{sub_reddit}/about.json', params=params, headers=headers)
        if t_users.status_code != 200:
            return False,t_users.text,[]
        t_users = t_users.json()["data"]["active_user_count"]

        if t_users < limit:
            print(Fore.YELLOW + f"\nNote: not enough users in {sub_reddit}, limit has been reduced to match the no. of users\n" + Style.RESET_ALL)

        after = ""
        scraped = []
        st = 0

        while len(scraped) < limit and after != 'null':
            params = {
                'redditWebClient': 'mweb2x',
                'layout': 'classic',
                'raw_json': '1',
                'withAds': 'true',
                'subredditName': f'{sub_reddit}',
                'after': f'{after}',
                'feature': 'link_preview',
                'sr_detail': 'true',
                'allow_over18': '1',
                'app': '2x-client-production',
                'obey_over18': 'true',
            }


            posts = requests.get(f'https://oauth.reddit.com/r/{sub_reddit}/hot.json', 
                                params=params, 
                                headers=headers,
                                proxies=proxies)
            
            if posts.status_code != 200  or "data" not in posts.json().keys():
                return False,f"error: couldn't get posts because{posts.text}",scraped
            
            posts = [post["data"]["name"] for post in posts.json()["data"]["children"]]

            for post in posts:
                if len(scraped) < limit:
                    params = {
                        'redditWebClient': 'mweb2x',
                        'layout': 'classic',
                        'raw_json': '1',
                        'profile_img': 'true',
                        'raw_media_syntax': 'true',
                        'depth': '8',
                        'id': f'{post}',
                        'rtj': 'true',
                        'feature': 'link_preview',
                        'sr_detail': 'true',
                        'allow_over18': '1',
                        'app': '2x-client-production',
                        'obey_over18': 'true',
                    }

                    users = requests.get(f'https://oauth.reddit.com/comments/{post[3:]}.json', params=params, headers=headers)
                    if users.status_code != 200:
                        print(f"unable to get users {users.text}")
                        continue
                    all_users =  users.json()[1]["data"]["children"]


                    mores = [user["data"]["children"] for user in all_users if user["kind"] == "more"]
                    mores = sum(mores,[])
                    more = str(mores).replace("[","").replace("]","").replace("'","").replace(" ","")

                    users = [{"username":user["data"]["author"],
                            "user_id":user["data"]["author_fullname"]} 
                            for user in  all_users
                            if "author_fullname" in user["data"].keys() and user["kind"] == "t1"]
                    
                    for user in users:
                        if user not in scraped and len(scraped) < limit:scraped.append(user)

                    while len(more) > 1 and len(scraped) < limit:
                        headers.update({
                            "content-type":"application/x-www-form-urlencoded",
                            "content-length":f"{len(more)}"
                        })
                    
                        params = {
                            'redditWebClient': 'mweb2x',
                            'layout': 'classic',
                            'raw_json': '1',
                            'profile_img': 'true',
                            'raw_media_syntax': 'true',
                            'depth': '8',
                            'sort': 'confidence',
                            'feature': 'link_preview',
                            'sr_detail': 'true',
                            'api_type': 'json',
                            'link_id': f'{post}',
                            'allow_over18': '1',
                            'app': '2x-client-production',
                            'obey_over18': 'true',
                        }
                        data = {"children":f'{more}'}
                        more_users = requests.post('https://oauth.reddit.com/api/morechildren.json', params=params, headers=headers, data=data)
                        if more_users.status_code != 200:
                            return False,f'error: unable to get more users {more_users.text}',scraped
                        
                        more_users = more_users.json()["json"]["data"]["things"]
                        more = more_users[len(more_users)-1]
                        more = more["data"]["children"] if  more["kind"] == "more" else ""
                        more = str(more).replace("[","").replace("]","").replace("'","").replace(" ","")

                        users = [{"username":user["data"]["author"],
                        "user_id":user["data"]["author_fullname"]} 
                        for user in  more_users
                        if "author_fullname" in user["data"].keys() and user["kind"] == "t1"]
                        
                        for user in users:
                            if user not in scraped and len(scraped) < limit:scraped.append(user)
                    if "content-type" in headers.keys():
                        headers.pop("content-type") 
                        headers.pop("content-length")
                        
            print(f"scraped {len(scraped)} users from {sub_reddit}")
            after = post[len(post)-1]

            if st == len(scraped):limit = len(scraped)
            st = len(scraped)

        return True,f"successfully scraped {len(scraped)} accounts from {sub_reddit}",scraped
    
    except Exception as error:
        print(error)
        return False,error,scraped
    
