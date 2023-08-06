import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support.wait import WebDriverWait


def guardar_captura(driver: webdriver.Remote, captura_error):
    try:
        if driver is not None:
            driver.save_screenshot(captura_error)
    except Exception:
        pass


def close_driver(driver: webdriver.Remote):
    try:
        if driver is not None:
            driver.quit()
    except Exception:
        pass


def login_sap(driver: webdriver.Remote, user, password):
    WebDriverWait(driver, 30).until(visibility_of_element_located((By.ID, 'USERNAME_FIELD-inner')))
    driver.find_element(By.ID, 'USERNAME_FIELD-inner').send_keys(user)
    time.sleep(0.5)

    WebDriverWait(driver, 30).until(visibility_of_element_located((By.ID, 'PASSWORD_FIELD-inner')))
    driver.find_element(By.ID, 'PASSWORD_FIELD-inner').send_keys(password)
    time.sleep(0.5)

    WebDriverWait(driver, 30).until(visibility_of_element_located((By.ID, 'LANGUAGE_SELECT')))
    driver.find_element(By.ID, 'LANGUAGE_SELECT').click()
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, 'option[value="ES"]').click()
    time.sleep(0.5)

    driver.find_element(By.ID, 'LOGIN_LINK').click()
    time.sleep(3)


def login_sharepoint(driver: webdriver.Remote, user, password):
    # Usuario
    # Si falla la búsqueda del campo por ID, se busca por nombre del input
    try:
        WebDriverWait(driver, 20).until(visibility_of_element_located((By.ID, 'i0116')))\
            .send_keys(user, Keys.ENTER)
    except TimeoutException:
        WebDriverWait(driver, 20).until(visibility_of_element_located((By.NAME, 'loginfmt')))\
            .send_keys(user, Keys.ENTER)

    # Contraseña
    # Si falla la búsqueda del campo por ID, se busca por nombre del input
    try:
        WebDriverWait(driver, 10).until(visibility_of_element_located((By.ID, 'i0118')))\
            .send_keys(password, Keys.ENTER)
    except TimeoutException:
        WebDriverWait(driver, 10).until(visibility_of_element_located((By.NAME, 'passwd')))\
            .send_keys(password, Keys.ENTER)

    time.sleep(1)
    WebDriverWait(driver, 10).until(visibility_of_element_located((By.ID, 'idBtn_Back'))).click()
