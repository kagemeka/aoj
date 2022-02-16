import asyncio
import unittest

import selext.webdriver

import aoj


class Test(unittest.TestCase):
    def test(self) -> None:
        async def wrap() -> None:

            with selext.webdriver.create_chrome_driver(
                headless=True
            ) as driver:
                submissions = []
                async for submission in aoj.fetch_submissions(
                    driver, "kagemeka"
                ):
                    print(submission)
                    submissions.append(submission)

        asyncio.run(wrap())


if __name__ == "__main__":
    unittest.main()
