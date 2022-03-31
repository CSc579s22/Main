from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

d = DesiredCapabilities.CHROME
d["loggingPrefs"] = {"browser": "ALL"}
driver = webdriver.Chrome(desired_capabilities=d)

url = "https://reference.dashif.org/dash.js/latest/samples/getting-started/logging.html"

driver.get(url)

# print messages
for entry in driver.get_log('browser'):
    print(entry)
