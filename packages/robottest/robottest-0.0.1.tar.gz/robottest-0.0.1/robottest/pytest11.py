import pytest
import allure

from .lib.cli import Cli

class RobotFixture(object):
    def __init__(self):
        pass

    @property
    def cli(self):
        return Cli()

@pytest.fixture(scope="session")
def robot_fix():
    return RobotFixture()
