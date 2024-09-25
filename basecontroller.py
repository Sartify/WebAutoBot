import datetime
import getpass
import json
import os
import re
import threading
import time
from typing import List
from basemodel import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

class BaseController:

    def __init__(self, title: str, recurse: bool = False, launch_on_init: bool = True, private=False):
        self._class_name = type(self).__name__
        self.__title = title
        self.__recurse = recurse
        self.__threads = []
        self.__pagination = 1
        self.__results: List[BaseModel] = []
        self._storage_dir = os.path.expanduser("~")
        self._base_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
        self._pydroid_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/")
        self._class_name = type(self).__name__
        self._class_dir = f"{self._base_directory}/{self._class_name}"
        if launch_on_init: self.__main()

    def __main(self):
        try:
            self._graphic_base_title()
            self.__print_main_menu()
            if self.__should_recurse():
                self.__main()
        finally:
            self.__reset()

    def __should_recurse(self) -> bool:
        return self.__recurse or self._get_menu_items() is not None

    def _graphic_base_title(self):
        self._graphic_title(self.__title)

    def _execute(self):
        pass

    def _execute_selection(self, choice: int):
        pass

    def _graphic_title(self, title: str):
        star_len = self.__get_star_length(title)
        offset = self.__get_menu_offset(title)
        even_text = len(title) % 2 == 0
        postfix_offset = offset if even_text else offset + 1
        print("*" * star_len)
        print(f"*{' ' * offset}{title}{' ' * postfix_offset}*")
        print("*" * star_len)

    def _get_menu_items(self) -> None|list:
        return None

    @staticmethod
    def __get_menu_offset(text: str, star_len: int = 50) -> int:
        return int(((star_len - 2) - len(text)) / 2)

    @staticmethod
    def __get_star_length(text: str) -> int:
        default_len = 50
        text_len = len(text)
        return text_len + 7 if text_len > default_len else default_len

    def __get_longest_menu_title(self) -> str:
        longest_title = ""
        for title in self._get_menu_items():
            longest_title = title if len(longest_title) < len(title) else longest_title
        return longest_title

    def __print_main_menu(self):
        menu_items = self._get_menu_items()
        if menu_items is None:
            self._execute()
            return
        longest_title = self.__get_longest_menu_title()
        star_len = self.__get_star_length(longest_title)
        for index in range(len(menu_items)):
            full_title = f"{index + 1}: {menu_items[index]}"
            item_offset = star_len - (len(full_title) + 3)
            print(f"* {full_title}{' ' * item_offset}*")
        print("*" * star_len)
        self.__make_selection()

    def __make_selection(self):
        selection = self._user_input("Select Option: ")
        choice = int(selection)
        self._execute_selection(choice)
        self.__reset()
        self.__main()

    def _user_input(self, prompt: str) -> str:
        keyword = input(prompt)
        if keyword == "":
            print("[-] Invalid Input\n")
            return self._user_input(prompt)
        return keyword

    def _user_password(self) -> str:
        password = getpass.getpass()
        if password == "":
            print("[-] Invalid Password\n")
            return self._user_password()
        return password

    def _append_thread(self, method, args: list = None, threads: int = None):
        if args is None: args = []
        thread = threading.Thread(target=method, args=args)
        self.__threads.append(thread)
        if threads is None: return
        threads_len = len(self.__threads)
        if threads_len % threads != 0: return
        self.__start_threads(threads)

    def _wait_thread_completion(self, threads: int = 10, start: int = 0):
        if not self.__threads: return
        self.__start_threads(threads, start)
        self.__threads.clear()

    @staticmethod
    def _start_thread(method, args: list = None):
        if args is None: args = []
        thread = threading.Thread(target=method, args=args)
        thread.start()

    def __start_threads(self, threads: int, start: int = 0):
        thread_len = len(self.__threads)
        for index, thread in enumerate(self.__threads):
            try:
                if not start is None and index < start: continue
                thread.start()
                print(f"[+] {thread.name} of {thread_len} Started")
                time.sleep(0.1)
                if index != 0 and index % threads == 0:
                    self.__join_threads()
            except RuntimeError:
                continue
            except Exception as e:
                print(f"[-] {e}")
        self.__join_threads()

    def __join_threads(self):
        for thread in self.__threads:
            try:
                thread.join()
            except RuntimeError:
                continue
            except Exception as e:
                print(f"[-] {e}")

    def _append_result(self, diction: dict):
        self.__results.append(BaseModel(diction))

    def _get_results(self) -> list:
        return [result.to_dict() for result in self.__results]

    def _clear_results(self):
        self.__results.clear()

    @staticmethod
    def __regex(pattern: str):
        return re.compile(pattern)

    def _regex_single(self, pattern: str, text: str):
        return self.__regex(pattern).search(text)

    def _regex_multiple(self, pattern: str, text: str) -> list:
        return self.__regex(pattern).findall(text)

    @staticmethod
    def _make_filename(name: str) -> str:
        file_name = []
        for index in range(len(name)):
            if name[index] == "_": continue
            file_name.append(name[index] if name[index].isalnum() else "_")
        return "".join(word.lower() for word in file_name)

    @staticmethod
    def _create_folder(folder: str):
        if os.path.exists(folder): return
        os.makedirs(folder, exist_ok=True)

    @staticmethod
    def _path_exists(path: str) -> bool:
        return os.path.exists(path)

    def _save_json(self, file_name: str):
        results = self.__results
        if len(results) == 0: return
        formatted_name = self._make_filename(file_name)
        path = f"{self._class_dir}/{formatted_name}.json"
        self._create_folder(self._class_dir)
        print("[*] Saving JSON...")
        with open(path, "wb") as file:
            data_map = [result.to_dict() for result in results]
            json_data = json.dumps(data_map, indent=4) if type(data_map) is bytes else json.dumps(data_map, indent=4).encode()
            file.write(json_data)
        print(f"[+] {path} Saved")

    def _add_pagination(self):
        self.__pagination += 1
        self._graphic_title(f"Page {self.__pagination}")

    @staticmethod
    def _current_time() -> datetime:
        return datetime.datetime.now()

    def _get_json_data(self, index:int = None):
        if not os.path.exists(self._class_dir): return []
        files = os.listdir(self._class_dir)
        files = [file for file in files if file.endswith("json")]
        if len(files) == 0: return []
        jsons = [file for file in files if file.endswith("json")]
        if index is None:
            statement = "\n".join(f"[{index + 1}] {file}" for index, file in enumerate(jsons))
            print(statement)
            choice = self._user_input("Select JSON: ")
            index = int(choice)
        selected_json = jsons[index - 1]
        data_file = open(f"{self._class_dir}/{selected_json}")
        result = data_file.read()
        data_file.close()
        return json.loads(result)

    def _print_json_data(self, *skips: int):
        json_data = self._get_json_data()
        for index, data in enumerate(json_data):
            if index in skips: continue
            print(f"[ {index + 1} ]")
            for key, value in data.items():
                print(f"{key}: {value}")
            print()

    def _launch(self, target: str):
        os.system(target)

    def _save_pdf_images(self, filename: str, images: list):
        if not images: return
        file_path = f"{self._class_dir}/{filename}.pdf"
        self._create_folder(self._class_dir)
        canva = canvas.Canvas(file_path, pagesize=A4)
        canva.setFillColor(colors.blue)
        canva.setFont("Helvetica", 16)
        canva.drawCentredString(50, 700, self._class_name)
        for image in images:
            canva.drawImage(image, 50, 400)
        canva.save()

    def __reset(self):
        self.__results.clear()
        self.__pagination = 1
        self.__threads.clear()
