import json
from random import choice, randint
import lorem

import pandas as pd
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def load_csv_with_pandas(file_path="./users.csv") -> DataFrame:
    return pd.read_csv(file_path)


options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)

data = load_csv_with_pandas()

failed_users = []

task = {}
with open("./task.json", "r", encoding="utf-8") as task_file:
    task = json.load(task_file)


base_link = task["base_link"]
login_url = f"{base_link}/u"
password = task["password"]

for username in data["Email Id"]:
    try:
        print(f"Using: {username}")
        # Open the login page
        driver.get(login_url)

        # Find the username and password input fields and login button by their IDs (you can use other locators as needed)
        username_field = driver.find_element(by=By.ID, value="user_id")
        password_field = driver.find_element(by=By.ID, value="password")
        login_button = driver.find_element(by=By.CLASS_NAME, value="loginBtn")

        # Input login credentials
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Submit the form
        login_button.click()
        driver.get(f"{base_link}/mlink/survey/{task['survey_id']}")

        driver.implicitly_wait(10)
        driver.find_element(
            By.CSS_SELECTOR, value=".actionbutton.actionblue.left-0"
        ).click()

        driver.implicitly_wait(10)

        for question in task["questions"]:
            question_type = question["question_type"]
            try:
                if question_type == "datapicker":
                    driver.find_element(
                        By.ID, f"{question['id']}-spa-textarea-date"
                    ).click()
                    driver.find_element(By.CLASS_NAME, "ui-datepicker-current").click()
                elif question_type == "mcq":
                    driver.find_element(
                        By.CSS_SELECTOR,
                        f"label[for='f{question['id']}-choice_{randint(1,question['option_count'])}']",
                    ).click()
                elif question_type == "moq":
                    option_count = question["option_count"]
                    for i in option_count:
                        click = choice([True, False])
                        if click:
                            driver.find_element(
                                By.CSS_SELECTOR,
                                f"label[for='f{question['id']}-choice_{i}']",
                            ).click()
                elif question_type == "likert":
                    for i in range(1, question["statement_count"]):
                        driver.find_element(
                            By.CSS_SELECTOR,
                            f"label[for='{question['id']}-statement_{i}-option_{randint(1,question['option_count'])}']",
                        ).click()
                elif question_type == "nps":
                    index = randint(0, 10)
                    driver.find_elements(
                        By.CSS_SELECTOR,
                        f".sr-nps-preview-container[data-id='{question['id']}'] #sr_nps",
                    )[index].click()
                elif question_type == "opinion_scale":
                    div_element = driver.find_element(By.CLASS_NAME, "input-range")
                    random_x = randint(0, 356)
                    actions = ActionChains(driver)
                    actions.move_to_element_with_offset(div_element, random_x, 2)
                    actions.click()
                    actions.perform()
                elif question_type == "ranking":
                    order_list_elements = driver.find_elements(
                        By.CSS_SELECTOR, ".fa-arrow-down, .far fa-arrow-up"
                    )
                    for element in order_list_elements:
                        click = choice([True, False])

                        if click:
                            try:
                                element.click()
                            except Exception:
                                pass
                elif question_type == "text":
                    driver.find_element(By.CLASS_NAME, "spa-textarea").send_keys(
                        lorem.paragraph()
                    )
                elif question_type == "star_rating":
                    index = randint(0, question["option_count"] - 1)
                    driver.find_elements(By.CSS_SELECTOR, "span.spa-star")[
                        index
                    ].click()
                elif question_type == "team" or question_type == "user":
                    teams_input = driver.find_element(
                        By.ID, f"token-input-spa-textarea-tl-{question['id']}"
                    )
                    teams_input.click()
                    driver.implicitly_wait(5)
                    teams = driver.find_elements(
                        By.CLASS_NAME, "token-input-dropdown-item-facebook"
                    )
                    teams[randint(0, len(teams) - 1)].click()
                elif question_type == "next":
                    driver.find_element(By.CSS_SELECTOR, ".sr-next").click()
            except Exception as err:
                pass

        driver.implicitly_wait(5)
        driver.find_element(By.CSS_SELECTOR, ".actionbutton.actionblue.ma-h5").click()
    except Exception as err:
        print(err)
        print(err.with_traceback(None))
        failed_users.append(username)
    finally:
        driver.get(f"{base_link}/ce/pulse/user/login/logout?external_param=true")
        driver.implicitly_wait(5)


driver.close()
print(f"Failed: {failed_users}")
