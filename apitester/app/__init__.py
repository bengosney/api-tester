# First Party
from apitester.app.app import APITester


def run():
    APITester().run()


__all__ = ["APITester", "run"]
