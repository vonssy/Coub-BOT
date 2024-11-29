import requests
import aiohttp
import asyncio
import json
import os
import urllib.parse
from colorama import *
from datetime import datetime
import pytz

wib = pytz.timezone("Asia/Jakarta")

class Coub:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
        }

    def clear_terminal(self):
        os.system("cls" if os.name == "nt" else "clear")

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
        query = query_params.get("user", [None])[0]

        if query:
            user_data_json = urllib.parse.unquote(query)
            user_data = json.loads(user_data_json)
            account = user_data.get("first_name", "unknown")
            return account
        else:
            raise ValueError("User data not found in query.")
    
    def load_task_list(self):
        url = "https://raw.githubusercontent.com/vonssy/Response.JSON/refs/heads/main/coub_tasks.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('task_list', [])
        except requests.exceptions.RequestException as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Error: Failed to fetch data from URL. {e}{Style.RESET_ALL}")
            return []
        except json.JSONDecodeError:
            self.log(f"{Fore.RED + Style.BRIGHT}Error: Failed to parse JSON data.{Style.RESET_ALL}")
            return []
        
    async def login(self, query: str, retries=5, delay=3):
        url = "https://coub.com/api/v2/sessions/login_mini_app"
        data = query
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "coub.com",
            "Origin": "https://coub.com",
            "Referer": "https://coub.com/tg-app",
            "Sec-Fetch-Site": "same-origin",
        }

        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if response.status == 200:
                            return result["api_token"]
                        else:
                            return None
            except (aiohttp.ClientError, aiohttp.ContentTypeError) as e:
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
                    await asyncio.sleep(delay)
                else:
                    return None
    
    async def get_token(self, api_token: str, retries=5, delay=3):
        url = "https://coub.com/api/v2/torus/token"
        headers = {
            **self.headers,
            "Content-Length": "0",
            "X-Auth-Token": api_token,
            "Host": "coub.com",
            "Origin": "https://coub.com",
            "Referer": "https://coub.com/tg-app",
            "Sec-Fetch-Site": "same-origin",
        }

        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if response.status == 200:
                            return result["access_token"]
                        else:
                            return None
            except (aiohttp.ClientError, aiohttp.ContentTypeError) as e:
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
                    await asyncio.sleep(delay)
                else:
                    return None
        
    async def user_balance(self, token: str, query: str, retries=5, delay=3):
        url = "https://rewards.coub.com/api/v2/get_user_balance"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "X-Tg-Authorization": query,
            "Host": "rewards.coub.com",
            "Origin": "https://coub.com",
            "Referer": "https://coub.com/",
            "Sec-Fetch-Site": "same-site",
        }

        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        response.raise_for_status()
                        if response.status == 200:
                            return await response.json()
                        else:
                            return None
            except (aiohttp.ClientError, aiohttp.ContentTypeError) as e:
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
                    await asyncio.sleep(delay)
                else:
                    return None

    async def refferal_rewards(self, token: str, query: str, retries=5, delay=3):
        url = "https://rewards.coub.com/api/v2/referal_rewards"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "X-Tg-Authorization": query,
            "Host": "rewards.coub.com",
            "Origin": "https://coub.com",
            "Referer": "https://coub.com/",
            "Sec-Fetch-Site": "same-site",
        }

        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        response.raise_for_status()
                        if response.status == 200:
                            return await response.text()
                        else:
                            return None
            except (aiohttp.ClientError, aiohttp.ContentTypeError) as e:
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
                    await asyncio.sleep(delay)
                else:
                    return None

    async def claim_refferal(self, token: str, query: str, retries=5, delay=3):
        url = "https://rewards.coub.com/api/v2/claim_referral_rewards"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "X-Tg-Authorization": query,
            "Host": "rewards.coub.com",
            "Origin": "https://coub.com",
            "Referer": "https://coub.com/",
            "Sec-Fetch-Site": "same-site",
        }

        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        response.raise_for_status()
                        if response.status == 200:
                            return True
                        else:
                            return False
            except (aiohttp.ClientError, aiohttp.ContentTypeError) as e:
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
                    await asyncio.sleep(delay)
                else:
                    return None
    
    async def complete_tasks(self, token: str, query: str, task_id, retries=5, delay=3):
        url = "https://rewards.coub.com/api/v2/complete_task"
        params = {"task_reward_id": task_id}
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "X-Tg-Authorization": query,
            "Host": "rewards.coub.com",
            "Origin": "https://coub.com",
            "Referer": "https://coub.com/",
            "Sec-Fetch-Site": "same-site",
        }
        
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        response.raise_for_status()
                        if response.status == 200:
                            return await response.json()
                        else:
                            return None
            except (aiohttp.ClientError, aiohttp.ContentTypeError) as e:
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
                    await asyncio.sleep(delay)
                else:
                    return None
    
    async def process_query(self, query: str):
        account = self.load_data(query)
        api_token = await self.login(query)
        if not api_token:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {account} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}] [ Api Token{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Is None {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
            )
            return
        
        await asyncio.sleep(2)

        token = await self.get_token(api_token)
        if not token:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {account} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}] [ Access Token{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Is None {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
            )
            return
        
        await asyncio.sleep(2)
        
        if token:
            user = await self.user_balance(token, query)
            if not user:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {account} {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Reward Data Is None{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} ]{Style.RESET_ALL}"
                )
                return
            
            if user:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {account} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}] [ Balance{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {user['balance']} $COUB {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                )
                await asyncio.sleep(2)

                refferal = await self.refferal_rewards(token, query)
                if refferal:
                    refferal_data = json.loads(refferal)
                    rewards = refferal_data['referal_balance']
                    if rewards > 0:
                        claim = await self.claim_refferal(token, query)
                        if claim:
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Refferal{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}] [ Reward{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {rewards} $COUB {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Refferal{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} Isn't Claimed {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                    else:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}[ Refferal{Style.RESET_ALL}"
                            f"{Fore.YELLOW+Style.BRIGHT} No Available Reward to Claim {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}[ Refferal{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                await asyncio.sleep(2)

                tasks = self.load_task_list()
                if tasks:
                    for task in tasks:
                        task_id = task["id"]
                        title = task["title"]
                        reward = task["reward"]
                        status = task["status"]

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

                            complete_task = await self.complete_tasks(token, query, task_id)
                            if complete_task:
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT} {title} {Style.RESET_ALL}"
                                    f"{Fore.GREEN+Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT} {reward} $COUB {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                                )
                            else:
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT} {title} {Style.RESET_ALL}"
                                    f"{Fore.RED+Style.BRIGHT}Isn't Completed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT} or {Style.RESET_ALL}"
                                    f"{Fore.YELLOW+Style.BRIGHT}Already Completed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT} ]{Style.RESET_ALL}"
                                )
                            await asyncio.sleep(1)
                else:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                    )
        
    async def main(self):
        try:
            with open("query.txt", "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Accoun's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(queries)}{Style.RESET_ALL}"
                )
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

                for query in queries:
                    query = query.strip()
                    if query:
                        await self.process_query(query)
                        self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                        seconds = 60
                        while seconds > 0:
                            formatted_time = self.format_seconds(seconds)
                            print(
                                f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                                f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}",
                                end="\r"
                            )
                            await asyncio.sleep(1)
                            seconds -= 1

                seconds = 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'query.txt' tidak ditemukan.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = Coub()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Coub - BOT{Style.RESET_ALL}                                       "                              
        )