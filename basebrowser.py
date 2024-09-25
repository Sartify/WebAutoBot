import json
import random
import sys

import bs4
import requests
import basecontroller
import ssl

class BaseBrowser(basecontroller.BaseController):

    def __init__(self, title: str, url: str, recurse: bool = False, use_ssl: bool = False, launch_on_init: bool = True, private=False):
        self.__base_url = f"{'https' if use_ssl else 'http'}://{url}"
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False  
        ssl_context.verify_mode = ssl.CERT_NONE  
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')

        class CustomAdapter(requests.adapters.HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                kwargs['ssl_context'] = ssl_context
                return super().init_poolmanager(*args, **kwargs)

        self.__session = requests.Session()
        self.__session.mount('https://', CustomAdapter())
        
        self.__headers = self.__random_header()
        self.__proxy = {}
        self.__private = private
        super().__init__(title, recurse, launch_on_init)

    def __random_header(self) -> dict:
        if type(self).__name__ == "Google":
            return {"User-Agent": "Firefox"}
        try:
            with open("agents.agents", "r") as file:
                agents = file.read().split("\n")
                random_index = random.randint(0, len(agents))
                device, agent = agents[random_index].split(":")
                self._graphic_title(f"Browsing as {device}")
                return {"User-Agent": agent}
        except:
            return {"User-Agent": "Firefox"}

    @staticmethod
    def __random_proxy() -> dict:
        with open("proxies.proxies", "r") as file:
            proxies = file.read().split("\n")
            random_index = random.randint(0, len(proxies))
            selected_proxy = proxies[random_index]
            return {
                "http": f"http://{selected_proxy}",
                "https": f"https://{selected_proxy}"
            }

    def _get_base_url(self) -> str:
        return self.__base_url

    def __response(self, url: str, get_request: bool = True, data = None) -> requests.Response:
        if data is None: data = {}
        try:
            print(f"[*] {url}")
            return self.__response_type(url, get_request, data)
        except requests.exceptions.ConnectTimeout:
            print("[-] Connection Timeout, Retrying...")
            return self.__response(url, get_request, data)
        except requests.exceptions.SSLError:
            print("[-] SSL Error: SSL Verification Failed")
            sys.exit()
        except requests.exceptions.TooManyRedirects:
            print("[-] Too Many Redirects")
            sys.exit()
        except Exception as e:
            print(f"[-] {e}\nRetrying...")
            return self.__response(url, get_request, data)

    def __response_type(self, url: str, get_request: bool, data) -> requests.Response:
        timeout = 100
        if get_request:
            return self.__session.get(url, headers=self.__headers, params=data, proxies=self.__proxy, timeout=timeout, verify=False)
        else:
            return self.__session.post(url, headers=self.__headers, data=data, proxies=self.__proxy, timeout=timeout, verify=False)

    def _get(self, url: str, data = None) -> requests.Response:
        if data is None: data = {}
        return self.__response(url, data=data)

    def _post(self, url: str, data = None) -> requests.Response:
        if data is None: data = {}
        return self.__response(url, get_request=False, data=data)

    def _join_base(self, link: str) -> str:
        return f"{self.__base_url}{link}"

    def __soup(self, response: requests.Response) -> bs4.BeautifulSoup:
        return self._parse_soup(response.text)

    def _get_soup(self, url: str, data = None) -> bs4.BeautifulSoup:
        if data is None: data = {}
        return self.__soup(self._get(url, data=data))

    def _post_soup(self, url: str, data = None) -> bs4.BeautifulSoup:
        if data is None: data = {}
        return self.__soup(self._post(url, data=data))

    def _base_soup(self, data = None) -> bs4.BeautifulSoup:
        if data is None: data = {}
        return self._get_soup(self.__base_url, data=data)

    def _parse_soup(self, content: str) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(content, "html.parser")

    def _get_json(self, url: str) -> str:
        return json.loads(self._get(url).text)

    @staticmethod
    def _print_source(soup: bs4.BeautifulSoup) -> None:
        print(soup.prettify())

    def _write_source(self, soup: bs4.BeautifulSoup) -> None:
        file_name = f"{type(self).__name__}.txt"
        self._create_folder(self._pydroid_directory)
        print("[*] Writing to file...")
        with open(f"{self._pydroid_directory}/{file_name}", "w") as file:
            file.write(soup.prettify())
            print("[+] File Written")
        print(soup.prettify())

    def _write_base_source(self) -> None:
        self._write_source(self._base_soup())

    def _print_base_source(self) -> None:
        self._print_source(self._base_soup())

    def _print_forms(self, url: str) -> None:
        soup = self._get_soup(url)
        for form in soup.select("form"):
            print(form.prettify())

    def _print_home_forms(self) -> None:
        self._print_forms(self.__base_url)

    def _download_file_url(self, path: str, url: str) -> None:
        download_path = f"{self._class_dir}/{'.Downloads' if self.__private else 'Downloads'}/"
        download_file = f"{download_path}/{path}"
        try:
            content = self._get(url)
            with open(download_file, "wb") as file:
                file.write(content.content)
        except FileNotFoundError:
            self._create_folder(download_path)
            self._download_file_url(path, url)
