import unittest

import selext.webdriver

import algomethod


class Test(unittest.TestCase):
    def test(self) -> None:
        task_ids = algomethod.fetch_task_ids()
        print(task_ids)
        with selext.webdriver.create_chrome_driver(headless=True) as driver:
            submissions = algomethod.fetch_submissions(driver, 209, "kagemeka")
            print(submissions)
            for submission in submissions:
                submission.code = algomethod.fetch_submission_code(
                    driver,
                    submission.id,
                )
                print(submission.code)
                print(algomethod.get_extension(submission.language))


if __name__ == "__main__":
    unittest.main()
