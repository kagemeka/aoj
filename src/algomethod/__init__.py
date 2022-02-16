from __future__ import annotations

import dataclasses
import importlib.metadata
import json
import time

import bs4
import requests
import selenium.webdriver

__version__ = importlib.metadata.version("algomethod")


_SITE_URL = "https://algo-method.com"
_TASKS_URL = f"{_SITE_URL}/tasks"
_LECTURE_URL = f"{_SITE_URL}/lecture_groups"


def _get_tasks_page() -> requests.Response:
    return requests.get(_TASKS_URL)


@dataclasses.dataclass
class Lecture:
    id: int
    title: str


def _scrape_lectures(html: str) -> list[Lecture]:
    soup = _parse_html(html)
    datas = json.loads(soup.find(id="__NEXT_DATA__").text)
    return [
        Lecture(**lecture)
        for lecture in datas["props"]["pageProps"]["lecture_groups"]
    ]


def _get_lecture_page(lecture_id: int) -> requests.Response:
    return requests.get(f"{_LECTURE_URL}/{lecture_id}")


def _scrape_task_ids(html: str) -> list[int]:
    soup = _parse_html(html)
    datas = json.loads(soup.find(id="__NEXT_DATA__").text)
    lectures = datas["props"]["pageProps"]["lgs"]["lectures"]
    task_ids = []
    for lecture in lectures:
        task_ids.extend([int(task["id"]) for task in lecture["tasks"]])
    return task_ids


def fetch_task_ids() -> list[int]:
    response = _get_tasks_page()
    lectures = _scrape_lectures(response.text)
    task_ids = []
    for lecture in lectures:
        response = _get_lecture_page(lecture.id)
        task_ids.extend(_scrape_task_ids(response.text))
    task_ids.sort()
    return task_ids


@dataclasses.dataclass
class Submission:
    id: int
    task_id: int
    # datetime: datetime.datetime
    # username: str
    language: str
    # status: str
    # exec_time_ms: int
    # memory_usage_kb: int
    # code_size_bytes: int
    code: str | None = None


def fetch_submissions(
    driver: selenium.webdriver.Chrome,
    task_id: int,
    username: str,
) -> list[Submission]:
    url = f"{_TASKS_URL}/{task_id}/submissions"
    params = {
        "user": username,
        "rowsPerPage": 100,
    }
    param_string = "&".join(f"{key}={value}" for key, value in params.items())
    driver.get(f"{url}?{param_string}")
    time.sleep(0.5)
    soup = _parse_html(driver.page_source)
    rows = soup.table.tbody.find_all("tr")
    submissions = []
    for row in rows:
        infos = row.find_all("td")
        submission = Submission(
            id=int(infos[-1].a.get("href").split("/")[-1]),
            task_id=task_id,
            language=infos[2].text,
        )
        submissions.append(submission)
    return submissions


def fetch_submission_code(
    driver: selenium.webdriver.Chrome,
    submission_id: int,
) -> str:
    url = f"{_SITE_URL}/submissions/{submission_id}"
    driver.get(url)
    time.sleep(1)
    soup = _parse_html(driver.page_source)
    # pattern = re.compile(r"^\d+(.*)$")
    code = ""
    for span in soup.pre.code.find_all("span"):
        classes = span.get("class")
        if classes and "linenumber" in classes:
            continue
        code += span.text
    return code


@dataclasses.dataclass
class Language:
    name: str
    id: int
    extensions: list[str] | None = None


@dataclasses.dataclass
class LoginCredentials:
    mail: str
    password: str


def input_login_credentials() -> LoginCredentials:
    import getpass

    mail = input("Mail: ")
    password = getpass.getpass("Password: ")
    return LoginCredentials(mail, password)


def _parse_html(html: str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(html, "html.parser")


_LANGUAGE_TO_EXTENSIONS = {
    "cpp-gcc": ["cpp"],
    "python3": ["py"],
    "text": ["txt"],
    "awk": ["awk"],
    "bash": ["sh"],
    "bc": ["bc"],
    "c": ["c"],
    "csharp": ["cs"],
    "dart": ["dart"],
    "dc": ["dc"],
    "golang": ["go"],
    "haskell": ["hs"],
    "java11": ["java"],
    "javascript": ["js"],
    "kotlin": ["kt"],
    "perl": ["pl"],
    "php": ["php"],
    "pypy3": ["py"],
    "ruby3": ["rb"],
    "rust": ["rs"],
    "sed": ["sed"],
    "swift": ["swift"],
    "typescript": ["ts"],
}


def get_extension(language: str) -> str:
    return _LANGUAGE_TO_EXTENSIONS.get(language, [""])[0]
