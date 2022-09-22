import argparse
import csv
import random
import time
import requests
from state_abbrev import abbrev_to_us_state
from faker import Faker
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup
from emails import MAIL_GENERATION_WEIGHTS
from selenium import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select, WebDriverWait
import logging
from selenium.webdriver.remote.remote_connection import LOGGER


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


def start_driver(url):

    if (args.cloud == CLOUD_ENABLED):
        LOGGER.setLevel(logging.WARNING)
        #driver = geckodriver("./extensions/Tampermonkey.xpi")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        options.add_argument("window-size=1200x600")
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)

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
        # chrome_options.add_extension("./extensions/Tampermonkey.crx")
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)

    driver.get(url)

    return driver


def createFakeIdentity():
    fake_identity = {}
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


def updateFormNumber(fake_identity):
    # send post request to the server with the data to track the number of reviews
    requests.post('http://datatracking-gz4c.com/studentloans')


def fill_out_form(fake_identity, driver):

    # Select Education Level
    education_levels = ['Current undergraduate student', 'Current graduate student',
                        'Former college student (did not graduate)', 'College graduate', 'Did not attend college', 'Other']

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

    PROMPT = [
        "I think student loan forgiveness is unfair because it will hurt the economy.",
        "Student debt is bad because it has the impact on everyone but the top.",
        "Student loan forgiveness is unfair because it will hurt the economy.",
        "This can add negative value and negative costs in any case as consumers lose their savings to the consumer.",
        '''But a government retirement account doesn't work much better for consumers if there are no government-provided retirement accounts in place at the moment. In fact, the U.S. Treasury Department states there are two government retirement accounts that come into effect under the Affordable Care Act: the Treasury National Savings and Investment Fund and the National Retirement Savings and Trust Fund.''',
        'Student debt forgiveness is bad because it is a form of disarming.',
        'Debt forgiveness is basically having enough money, but the real solution is to forgive.',
        '''To be honest, I am not sure it is a good idea for tax reform. If you feel you have been ripped off like I am, don't take it. Take the good stuff.''',
        '''There are many other ways to forgive. One of its many drawbacks is that it takes money to pay off your debt. Another option is to use tax deductions to pay for medical emergencies or other expenses. You don't have to pay your debt back, but you will need more than you can afford.''',
        '''Student debt forgiveness is bad because people don't understand why it's good for them.''',
        ''' It's bad because their friends and families don't understand what it is and doesn't need it.''',
        '''It's bad because there isn't enough funding available to give everyone in this country a chance to earn the right to work toward their dreams.''',
        '''It's bad because it's not fair to the people who have to pay for it.''',
        '''We need to make sure that people who are in debt are able to pay it back.''',
        '''It'll make it harder for people to get jobs and it'll make it harder for people to get loans.''',
        '''It'll increase the cost of living for people who are already struggling.''',
        '''It will increase the cost of college for people who are already struggling.''',
        '''College will cost more''',
        '''I hate poor people''',
        '''Poor people are bad''',
        "poor people deserve to suffer",
        "poor people are lazy",
        "I'm mad at Biden for not giving me free money",
        "Just get a job freeloaders",
        "Nobody wants to work anymore. This is enabling.",
        "They will use their extra money for drugs",
        "Jesus would have loved people being in debt",
        "Just join the military LOLOLOL",
        "I served so I could pay of my debt, so should everyone else",
        "Just join the military",
        "We need MORE servicemen",
        "They would be able to pay off their debts if they didnt get a degree in gender studies",
        "They would be able to pay off their debts if they didnt get a degree in English",
        "They would be able to pay off their debts if they didnt get a degree in Wokism",
        "They would be able to pay off their debts if they didnt get a degree in basket weaving",
        "Just dont work at mcdonalds and you can pay off your loans",
        "Nobody wants to work anymore",
        "Lets go brandon",
        "Trump 2024",
        "This is all queen naija's fault",
        "Where is hunter biden's laptop??????",
        "Don Jr does coke",
        "Student Debt is actually good.",
        "Just get into crypto and there would be no debt",
        "I lost my house cause of crypto but im not crying about my 400k debt",
        "Biden Doesnt care about me",
        "Biden is racist",
        "Biden isn't racist enough",
        "trump 2020",
        "LOCK HER UP (hilary)",
        "I'm mad at Biden for not giving me free money GRRRRR",
        "Nobody is actually reading these lol",
        "Biden bad",
        "DESANTIS 2024 BABYYY",
        "I have no life.",
        "I hate school tbh",
        "I hate my parents",
        "I hate my siblings",
        "I hate my friends",
        "I hate my job",
        "I hate my boss",
        "I hate my coworkers",

    ]

    frustrations = driver.find_element(
        By.XPATH, "//*[contains(@name,'frustrations_with_biden')]").send_keys(random.choice(PROMPT))

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
            updateFormNumber(fake_identity)

        # print(fake_identity['email'],
        #       fake_identity['password'])

        driver.close()
        time.sleep(1)
