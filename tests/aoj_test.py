import unittest

import selext.webdriver

import aoj


class Test(unittest.TestCase):
    def test(self) -> None:
        with selext.webdriver.create_chrome_driver(headless=True) as driver:
            submissions = []
            for submission in aoj.fetch_submissions(driver, "kagemeka"):
                print(submission)
                submissions.append(submission)


if __name__ == "__main__":
    unittest.main()
