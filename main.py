import argparse
import logging
import random
import time

import requests
from faker import Faker
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from emails import MAIL_GENERATION_WEIGHTS
from state_abbrev import abbrev_to_us_state

CLOUD_DESCRIPTION = 'Puts script in a \'cloud\' mode where the Chrome GUI is invisible'
CLOUD_DISABLED = False
CLOUD_ENABLED = True
MAILTM_DISABLED = False
MAILTM_ENABLED = True
EPILOG = ''
SCRIPT_DESCRIPTION = ''

url = 'https://www.jobcreatorsnetwork.com/is-student-loan-forgiveness-unfair/'

# Option parsing
parser = argparse.ArgumentParser(SCRIPT_DESCRIPTION, epilog=EPILOG)
parser.add_argument('--cloud', action='store_true', default=CLOUD_DISABLED,
                    required=False, help=CLOUD_DESCRIPTION, dest='cloud')
parser.add_argument('--mailtm', action='store_true', default=MAILTM_ENABLED,
                    required=False, dest='mailtm')
parser.add_argument('-g', '--google', required=False, default=False, action='store_true',
                    help="Uses google review instead of yelp review", dest='use_google')

parser.add_argument('-r', '--retry_amount', type=int, required=False, default=10,
                    help="Number of times to retry creating an account", dest='retry_amount')
args = parser.parse_args()

fake = Faker()


def get_random_user_agent() -> str:
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    # Get list of user agents.
    user_agents = user_agent_rotator.get_user_agents()

    # Get Random User Agent String.
    return user_agent_rotator.get_random_user_agent()


def start_driver(url):
    if (args.cloud == CLOUD_ENABLED):
        LOGGER.setLevel(logging.WARNING)
        # driver = geckodriver("./extensions/Tampermonkey.xpi")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        options.add_argument("window-size=1200x600")
        driver = webdriver.Chrome(
            'chromedriver', options=options)

    else:
        options = webdriver.ChromeOptions()
        options.add_argument(
            "--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument(  # Enable the WebGL Draft extension.
            '--enable-webgl-draft-extensions')
        options.add_argument('--disable-infobars')  # Disable popup
        options.add_argument('--disable-popup-blocking')  # and info bars.
        options.add_argument(f"user-agent={get_random_user_agent()}")  # Randomize user agent
        options.add_argument("headless")  # prevent browser from popping up
        # chrome_options.add_extension("./extensions/Tampermonkey.crx")
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)

    driver.get(url)

    return driver


def createFakeIdentity():
    fake_identity = dict()
    fake_identity['first_name'] = fake.first_name()
    fake_identity['last_name'] = fake.last_name()
    fake_identity['user'] = fake_identity['first_name'] + '' + \
                            fake_identity['last_name'] + str(random.randint(1, 999999))
    fake_identity['email'] = random_email(
        fake_identity['first_name'] + ' ' + fake_identity['last_name'] + str(random.randint(1, 999999)))
    fake_identity['password'] = fake.password()

    return fake_identity


def random_email(name=None):
    if name is None:
        name = fake.name()

    mailGens = [lambda fn, ln, *names: fn + ln,
                lambda fn, ln, *names: fn + "_" + ln,
                lambda fn, ln, *names: fn[0] + "_" + ln,
                lambda fn, ln, *names: fn + ln +
                                       str(int(1 / random.random() ** 3)),
                lambda fn, ln, *names: fn + "_" + ln +
                                       str(int(1 / random.random() ** 3)),
                lambda fn, ln, *names: fn[0] + "_" + ln + str(int(1 / random.random() ** 3)), ]

    return random.choices(mailGens, MAIL_GENERATION_WEIGHTS)[0](*name.split(" ")).lower() + "@" + requests.get(
        'https://api.mail.tm/domains').json().get('hydra:member')[0].get('domain')


def updateFormNumber():
    # send post request to the server with the data to track the number of reviews
    requests.post('http://datatracking-gz4c.com/studentloans')


def fill_out_form(fake_identity, driver):
    # Select Education Level
    education_levels = ['Current undergraduate student', 'Current graduate student',
                        'Former college student (did not graduate)', 'College graduate', 'Did not attend college',
                        'Other']

    student_debt = ['Currently have student loan debt',
                    'Did have student loan debt, but paid it off', 'Never took out student loans']

    # Wait for element to load
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.TAG_NAME, 'iframe')))

    driver.switch_to.frame(driver.find_element(
        by=By.TAG_NAME, value="iframe"))

    select = Select(driver.find_element(
        By.XPATH, "//*[contains(@name,'education_level_acquired')]"))
    select.select_by_value(random.choice(education_levels))

    select = Select(driver.find_element(
        By.XPATH, "//*[contains(@name,'student_debt')]"))
    select.select_by_value(random.choice(student_debt))

    # Randomly Select Question

    random.choice(driver.find_elements(
        By.XPATH, "//*[contains(@name,'income_over__125k')]")).click()

    driver.find_element(
        By.XPATH, "//*[contains(@name,'frustrations_with_biden')]").send_keys(generate_random_sentence())

    random.choice(driver.find_elements(
        By.XPATH, "//*[contains(@name,'received_pell_grant')]")).click()

    ST = random.choice(list(abbrev_to_us_state.keys()))

    driver.find_element(
        By.XPATH, "//*[contains(@name,'firstname')]").send_keys(fake_identity['first_name'])
    driver.find_element(
        By.XPATH, "//*[contains(@name,'lastname')]").send_keys(fake_identity['last_name'])
    driver.find_element(
        By.XPATH, "//*[contains(@name,'email')]").send_keys(fake_identity['email'])
    driver.find_element(
        By.XPATH, "//*[contains(@name,'state')]").send_keys(abbrev_to_us_state[ST])
    try:
        driver.find_element(
            By.XPATH, "//*[contains(@name,'zip')]").send_keys(fake.postcode_in_state(ST))
    except Exception as e:
        print("Error, skipping")
        return False

    time.sleep(3)
    random.choice(driver.find_elements(
        By.XPATH, "//*[contains(@type,'submit')]")).click()
    return True


def generate_random_sentence() -> str:
    # sometimes give empty sentence
    if random.randint(1, 10) <= 4:
        return ""
    WORDS = ["biden", "trump", "democrat", "republican", "liberal", "leftist", "left", "right", "conservative",
             "far-right", "far-left", "fox news", "CNN", "fake news", "media", "left-wing", "right-wing", "loans",
             "student", "debt", "forgive", "forgiveness", "college", "degree", "bachelor's degree", "master's degree",
             "PhD", "paid", "paid off", "president", "white house", "pell", "grant", "scholarship", "earned",
             "frustrated", "pell grant", "vote", "deserved", "undeserved", "education", "the", "if", "and", "or", "a",
             "an"]

    PUNCTUATIONS = [".", ",", "!", ":", ";", "&", "/", "\\"]
    word_choices = random.choices(WORDS, k=random.randint(5, 50))
    punctuation_choices = random.choices(PUNCTUATIONS, k=random.randint(0, 5))
    mix = word_choices + punctuation_choices
    random.shuffle(mix)
    return " ".join(mix)


if __name__ == "__main__":

    total_forms = 0

    while True:
        print('starting new form')
        driver = start_driver(
            url)

        driver.switch_to.window(driver.window_handles[0])
        fake_identity = createFakeIdentity()
        time.sleep(1)

        if fill_out_form(fake_identity, driver):
            print('Thank you: {} {} for filling out this form'.format(
                fake_identity['first_name'], fake_identity['last_name']))
            total_forms += 1
            print(f"Total Forms: {total_forms}")
            time.sleep(1)
            updateFormNumber()

        driver.close()
        time.sleep(1)
