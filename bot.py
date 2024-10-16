import requests
import json
import os
import urllib.parse
from colorama import *
from datetime import datetime
import time
import pytz

wib = pytz.timezone('Asia/Jakarta')

class Coub:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
        }

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Coub - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def load_data(self, query: str):
        query_params = urllib.parse.parse_qs(query)
        query = query_params.get('user', [None])[0]

        if query:
            user_data_json = urllib.parse.unquote(query)
            user_data = json.loads(user_data_json)
            first_name = user_data.get('first_name', 'unknown')
            return first_name
        else:
            raise ValueError("User data not found in query.")
    
    def load_task_list(self):
        try:
            with open('tasks.json', 'r') as file:
                data = json.load(file)
                return data.get('task_list', [])
        except FileNotFoundError:
            self.log(f"{Fore.RED + Style.BRIGHT}Error: 'task_list.json' not found.{Style.RESET_ALL}")
            return []
        except json.JSONDecodeError:
            self.log(f"{Fore.RED + Style.BRIGHT}Error: Failed to parse 'task_list.json'.{Style.RESET_ALL}")
            return []
        
    def login(self, query: str, retries=5, delay=3):
        url = 'https://coub.com/api/v2/sessions/login_mini_app'
        data = query
        self.headers.update({
            'Content-Length': str(len(data)),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'coub.com',
            'Origin': 'https://coub.com',
            'Referer': 'https://coub.com/tg-app',
            'Sec-Fetch-Site': 'same-origin',
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers, data=data)
                result = response.json()
                if response.status_code == 200:
                    return result['api_token']
                else:
                    return None
            except Exception as e:
                if "RemoteDisconnected" in str(e) or "requests.exceptions" in str(e):
                    if attempt < retries - 1:
                        print(
                            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ HTTP ERROR ]{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}[{attempt + 1}/{retries}]{Style.RESET_ALL}",
                            end="\r",
                            flush=True
                        )
                        time.sleep(delay * (2 ** attempt))
                else:
                    return None
    
    def get_token(self, api_token: str, retries=5, delay=3):
        url = 'https://coub.com/api/v2/torus/token'
        self.headers.update({
            'Content-Length': '0',
            'X-Auth-Token': api_token,
            'Host': 'coub.com',
            'Origin': 'https://coub.com',
            'Referer': 'https://coub.com/tg-app',
            'Sec-Fetch-Site': 'same-origin',
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers)
                result = response.json()
                if response.status_code == 200:
                    return result['access_token']
                else:
                    return None
            except Exception as e:
                if "RemoteDisconnected" in str(e) or "requests.exceptions" in str(e):
                    if attempt < retries - 1:
                        print(
                            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ HTTP ERROR ]{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}[{attempt + 1}/{retries}]{Style.RESET_ALL}",
                            end="\r",
                            flush=True
                        )
                        time.sleep(delay * (2 ** attempt))
                else:
                    return None
        
    def user_rewards(self, token: str, query: str, retries=5, delay=3):
        url = 'https://rewards.coub.com/api/v2/get_user_rewards'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'X-Tg-Authorization': query,
            'Host': 'rewards.coub.com',
            'Origin': 'https://coub.com',
            'Referer': 'https://coub.com/',
            'Sec-Fetch-Site': 'same-site',
        })

        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers)
                result = response.json()
                if response.status_code == 200:
                    return result
                else:
                    return None
            except Exception as e:
                if "RemoteDisconnected" in str(e) or "requests.exceptions" in str(e):
                    if attempt < retries - 1:
                        print(
                            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ HTTP ERROR ]{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}[{attempt + 1}/{retries}]{Style.RESET_ALL}",
                            end="\r",
                            flush=True
                        )
                        time.sleep(delay * (2 ** attempt))
                else:
                    return None
    
    def refferal_rewards(self, token: str, query: str, retries=5, delay=3):
        url = 'https://rewards.coub.com/api/v2/referal_rewards'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'X-Tg-Authorization': query,
            'Host': 'rewards.coub.com',
            'Origin': 'https://coub.com',
            'Referer': 'https://coub.com/',
            'Sec-Fetch-Site': 'same-site',
        })

        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers)
                result = response.json()
                if response.status_code == 200:
                    return result
                else:
                    return None
            except Exception as e:
                if "RemoteDisconnected" in str(e) or "requests.exceptions" in str(e):
                    if attempt < retries - 1:
                        print(
                            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ HTTP ERROR ]{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}[{attempt + 1}/{retries}]{Style.RESET_ALL}",
                            end="\r",
                            flush=True
                        )
                        time.sleep(delay * (2 ** attempt))
                else:
                    return None
    
    def complete_tasks(self, token: str, query: str, task_id, retries=5, delay=3):
        url = "https://rewards.coub.com/api/v2/complete_task"
        params = {"task_reward_id": task_id}
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'X-Tg-Authorization': query,
            'Host': 'rewards.coub.com',
            'Origin': 'https://coub.com',
            'Referer': 'https://coub.com/',
            'Sec-Fetch-Site': 'same-site',
        })
        
        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, params=params)
                result = response.json()
                if response.status_code == 200:
                    return result
                else:
                    return None
            except Exception as e:
                if "RemoteDisconnected" in str(e) or "requests.exceptions" in str(e):
                    if attempt < retries - 1:
                        print(
                            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ HTTP ERROR ]{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}[{attempt + 1}/{retries}]{Style.RESET_ALL}",
                            end="\r",
                            flush=True
                        )
                        time.sleep(delay * (2 ** attempt))
                else:
                    return None
    
    def process_query(self, query: str):
        
        first_name = self.load_data(query)
        api_token = self.login(query)
        token = self.get_token(api_token)
        
        if token:
            user = self.user_rewards(token, query)
            reff = self.refferal_rewards(token, query)
            user_rewards = sum(point['points'] for point in user)
            user_rewards -= 80
            reff_rewards = reff['referal_balance']

            total_rewards = user_rewards + reff_rewards

            if total_rewards:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {first_name} {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}] [ Balance{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {total_rewards} $COUB {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}]{Style.RESET_ALL}"
                )

            tasks = self.load_task_list()
            if tasks:
                for task in tasks:
                    task_id = task['id']
                    title = task['title']
                    reward = task['reward']
                    status = task['status']

                    if status in ["ready-to-start", "ready-to-claim"]:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {task_id} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {title} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}] [ Status{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {status} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                        )

                        complete_task = self.complete_tasks(token, query, task_id)
                        if complete_task:
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {title} {Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT}is Completed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {reward} $COUB {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {title} {Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT}is Failed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} or {Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT}Already Completed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} ]{Style.RESET_ALL}"
                            )

                    time.sleep(1)
        
    def main(self):
        try:
            with open('query.txt', 'r') as file:
                queries = [line.strip() for line in file if line.strip()]

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(queries)}{Style.RESET_ALL}"
                )
                self.log(f"{Fore.CYAN + Style.BRIGHT}-----------------------------------------------------------------------{Style.RESET_ALL}")

                for query in queries:
                    query = query.strip()
                    if query:
                        self.process_query(query)
                        self.log(f"{Fore.CYAN + Style.BRIGHT}-----------------------------------------------------------------------{Style.RESET_ALL}")

                seconds = 1800
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    time.sleep(1)
                    seconds -= 1

        except KeyboardInterrupt:
            self.log(f"{Fore.RED + Style.BRIGHT}[ EXIT ] Coub - BOT{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    coub = Coub()
    coub.main()