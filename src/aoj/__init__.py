from __future__ import annotations

import asyncio
import dataclasses
import importlib.metadata
import typing

import aiohttp
import bs4
import selenium.webdriver

__version__ = importlib.metadata.version("aoj-api")

_SITE_URL = "https://onlinejudge.u-aizu.ac.jp"
_USERS_URL = f"{_SITE_URL}/status/users"
_REVIEW_URL = "https://judgeapi.u-aizu.ac.jp/reviews"
_WAIT_TIME = 1.0


def _parse_html(html: str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(html, "html.parser")


@dataclasses.dataclass
class Submission:
    id: int
    status: str
    problem_id: str
    language: str
    code: str | None = None


async def fetch_page_submissions(
    driver: selenium.webdriver.Chrome,
    user_id: str,
    page: int,
) -> typing.AsyncIterator[Submission]:
    url = f"{_USERS_URL}/{user_id}/submissions/{page}"
    driver.get(url)
    await asyncio.sleep(_WAIT_TIME)
    html = driver.page_source
    soup = _parse_html(html)
    table = soup.find_all("table")[1]
    rows = table.find_all("tr")
    for row in rows:
        infos = row.find_all("div")
        yield Submission(
            id=int(infos[0].text.strip()),
            status=infos[1].text.strip(),
            problem_id=infos[2].text.strip(),
            language=infos[4].text.strip(),
        )


@dataclasses.dataclass
class Pagination:
    current: int
    last: int


async def fetch_pagination(
    driver: selenium.webdriver.Chrome,
    user_id: str,
) -> Pagination:
    url = f"{_USERS_URL}/{user_id}/submissions/1"
    driver.get(url)
    await asyncio.sleep(_WAIT_TIME)
    html = driver.page_source
    soup = _parse_html(html)
    pagination = soup.find("div", class_="pagination")
    current = int(pagination.find(class_="active").text)
    last = int(pagination.find_all("li")[-1].text)
    return Pagination(current, last)


async def fetch_submissions(
    driver: selenium.webdriver.Chrome,
    user_id: str,
) -> typing.AsyncIterator[Submission]:
    pagination = await fetch_pagination(driver, user_id)
    for page in range(1, pagination.last + 1):
        async for submission in fetch_page_submissions(driver, user_id, page):
            yield submission


async def fetch_submission_code(
    session: aiohttp.ClientSession,
    submission_id: int,
) -> str:
    url = f"{_REVIEW_URL}/{submission_id}"
    async with session.get(url) as response:
        return typing.cast(str, (await response.json())["sourceCode"])


_LANGUAGE_TO_EXTENSION = {
    "C++": "cpp",
    "C": "c",
    "Java": "java",
    "C++11": "cpp",
    "C++14": "cpp",
    "C++17": "cpp",
    "C#": "cs",
    "D": "d",
    "Go": "go",
    "Ruby": "rb",
    "Rust": "rs",
    "Python": "py",
    "Python3": "py",
    "JavaScript": "js",
    "Scala": "scala",
    "Haskell": "hs",
    "OCaml": "ml",
    "PHP": "php",
    "Kotlin": "kt",
}


def get_extension(language: str) -> str:
    return _LANGUAGE_TO_EXTENSION[language]
