import contextlib
import sys
import threading
import time

import pytest
from selenium import webdriver
import uvicorn

sys.path.insert(0, "./tests")  # Add the tests directory to the path


class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


config = uvicorn.Config("app:app", host="127.0.0.1", port=5000, log_level="info")


@pytest.fixture(scope="session")
def server():
    with Server(config=config).run_in_thread():
        yield


@pytest.fixture
def browser_driver():
    """Create browser driver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()
