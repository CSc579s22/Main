let assert = require('assert'),
  webdriver = require('selenium-webdriver'),
  By = webdriver.By,
  until = webdriver.until,
  chrome = require('selenium-webdriver/chrome')

let path = require('chromedriver').path;
let driver = chrome.Driver.createSession(new chrome.Options(), new chrome.ServiceBuilder(path).build());

driver.get('https://reference.dashif.org/dash.js/latest/samples/getting-started/logging.html');
driver.manage().logs().get(webdriver.logging.Type.BROWSER)
  .then(function (entries) {
    entries.forEach(function (entry) {
      console.log('[%s] %s', entry.level.name, entry.message);
    });
  });
