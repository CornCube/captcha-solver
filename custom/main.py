import time
from random import randint

from PIL import Image
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from solve import Solve

# Initialize selenium, model, class list
solve = Solve()
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("window-size=800,800")

options.add_argument("user-agent=Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 "
                     "Edge/12.10166")

driver = webdriver.Chrome(options=options)
driver.delete_all_cookies()

items = dict([("cars", "car"),
              ("taxis", "car"),
              ("vehicle", "car"),
              ("vehicles", "car"),
              ("bridges", "bridge"),
              ("chimneys", "chimney"),
              ("crosswalks", "crosswalk"),
              ("palm trees", "palm"),
              ("stairs", "stair"),
              ("hydrants", "hydrant"),
              ("a fire hydrant", "hydrant"),
              ("fire hydrants", "hydrant"),
              ("bicycles", "bicycle"),
              ("traffic lights", "traffic light"),
              ("motorcycles", "motorcycle"),
              ("parking meters", "parking meter"),
              ("buses", "bus"),
              ("bus", "bus")])


def check_exists_by_xpath(xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


driver.get("https://www.google.com/recaptcha/api2/demo")


def main():
    # switch to recaptcha frame
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    driver.switch_to.frame(frames[0])

    time.sleep(2)

    # click on checkbox to activate recaptcha
    check_box = WebDriverWait(driver, 60).until(ec.element_to_be_clickable((By.ID, "recaptcha-anchor")))
    check_box.click()

    # check if challenge has to be completed
    driver.switch_to.parent_frame()
    time.sleep(randint(5, 10))
    WebDriverWait(driver, 60).until(ec.frame_to_be_available_and_switch_to_it((By.TAG_NAME, 'iframe')))
    if check_exists_by_xpath('//span[@aria-checked="true"]'):
        driver.switch_to.parent_frame()
        pass
    else:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='recaptcha challenge "
                                                                 "expires in two minutes']"))

            # 4 types of captcha may occur
            instructions = driver.find_element(By.CLASS_NAME, 'rc-imageselect-instructions').text
            print(instructions)

            captcha_type = ''
            if 'Select all squares with' in instructions:
                captcha_type = 'type 1'
                if 'If there are none, click skip' in instructions:
                    captcha_type = 'type 2'
            elif 'Select all images with' in instructions:
                captcha_type = 'type 3'
                if 'Click verify once there are none left' in instructions:
                    captcha_type = 'type 4'

            print(captcha_type)

            item = driver.find_element(By.XPATH, '//strong').text

            # make sure that item is included in the COCO dataset
            if item in items:
                item = items[item]
                print(item)
            else:
                print('item is not in COCO, please refresh and try again.')
                raise Exception

            driver.find_element(By.TAG_NAME, "table").screenshot("web_screenshot.png")
            img = Image.open("web_screenshot.png")
            size = len(
                driver.find_elements(By.XPATH, "//div[@class='rc-imageselect-challenge']//div//table//tbody//tr"))
            correct_tiles = solve.inference(img, size, item)
            tiles = driver.find_elements(By.XPATH, "//td[@class='rc-imageselect-tile']")

            def solve_captcha(results):
                # find all tiles
                # iterate through em while incrementing r and c
                # check if tile rc matches a correct tile
                # if it does, select it and increment. if it doesn't, ignore and increment
                col = 0
                row = 1  # start top left (c, r) = (1, 1). increment by one = (2, 1). (3, 1). ()

                for tile in tiles:
                    col += 1
                    if col > size:
                        row += 1
                        col = 1
                    for result in results:
                        if (col == result['tile_col']) and (row == result['tile_row']):
                            tile.click()
                            print(str(col) + ' ' + str(row) + ' clicked!')
                            time.sleep(2)
                            break

            if captcha_type == 'type 1':
                # simply select the appropriate squares
                solve_captcha(correct_tiles)
                driver.find_element(By.XPATH, "//button[@id='recaptcha-verify-button']").click()
                print(captcha_type)

            elif captcha_type == 'type 2':
                # select appropriate squares, if none then press skip and retry
                while len(correct_tiles) == 0:
                    driver.find_element(By.XPATH, "//button[@id='recaptcha-verify-button']").click()
                    time.sleep(5)
                    driver.find_element(By.TAG_NAME, "table").screenshot("web_screenshot.png")
                    img = Image.open("web_screenshot.png")

                    item = driver.find_element(By.XPATH, '//strong').text

                    # make sure that item is included in the COCO dataset
                    if item in items:
                        item = items[item]
                        print(item)
                    else:
                        print('item is not in COCO, please refresh and try again.')
                        raise Exception
                    
                    correct_tiles = solve.inference(img, size, item)

                solve_captcha(correct_tiles)
                driver.find_element(By.XPATH, "//button[@id='recaptcha-verify-button']").click()
                print(captcha_type)

            elif captcha_type == 'type 3':
                # individual images, just need to select the squares
                solve_captcha(correct_tiles)
                driver.find_element(By.XPATH, "//button[@id='recaptcha-verify-button']").click()
                print(captcha_type)

            elif captcha_type == 'type 4':
                # individual images, but need to keep retrying as long as stuff is detected
                # solve. everything has been pressed! now, rerun. everything has been pressed! until there are no corre
                while len(correct_tiles) != 0:
                    solve_captcha(correct_tiles)
                    time.sleep(5)
                    driver.find_element(By.TAG_NAME, "table").screenshot("web_screenshot.png")
                    img = Image.open("web_screenshot.png")
                    correct_tiles = solve.inference(img, size, item)

                driver.find_element(By.XPATH, "//button[@id='recaptcha-verify-button']").click()
                print(captcha_type)

            time.sleep(10)
            driver.quit()

        except Exception as e:
            print('failed, refreshing page')
            driver.refresh()
            print(e)
            main()


main()

# types 3 and 4 work pretty well, 1 and 2 are inconsistent
