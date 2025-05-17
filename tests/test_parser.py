import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from reviewscraper.parser import parse_reviews, scroll_reviews

class DummyDriver:
    def __init__(self, html_cards):
        self.html_cards = html_cards
        self.find_elements_called = False

    def find_elements(self, by, value):
        self.find_elements_called = True
        class Card:
            def __init__(self, stars, text):
                self._stars = stars
                self._text = text
            def find_element(self, by, selector):
                class Elem:
                    def __init__(self, text):
                        self.text = text
                    def get_attribute(self, name):
                        return f"{self.text} stars"
                if 'aria-label' in selector or 'stars' in selector:
                    return Elem(str(self._stars))
                return Elem(self._text)
        return [Card(4, 'Great place'), Card(2, 'Not clean')]

    def execute_script(self, script, element):
        return None

    def find_element(self, by, value):
        return None  # not used here

    def implicitly_wait(self, seconds):
        pass

    def quit(self):
        pass

@pytest.fixture
def driver():
    return DummyDriver(html_cards=None)

def test_parse_reviews_filter_none(driver):
    reviews = parse_reviews(driver, star_filter=None)
    assert len(reviews) == 2

def test_parse_reviews_filter_specific(driver):
    reviews = parse_reviews(driver, star_filter=[4])
    assert len(reviews) == 1
    assert reviews[0]['stars'] == 4

def test_scroll_reviews(driver):
    # scroll_reviews should not error
    scroll_reviews(driver, pause=0, max_iters=1)
    assert driver.find_elements_called == False
