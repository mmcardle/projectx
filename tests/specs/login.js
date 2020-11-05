
// For authoring Nightwatch tests, see
// https://nightwatchjs.org/guide

const constants = require("../constants.js")
const functions = require("../functions.js")

const PROJECT_EMAIL = constants.PROJECT_EMAIL;
const PROJECT_PASSWORD = constants.PROJECT_PASSWORD;

const login = functions.login;

module.exports = {

  //beforeEach: functions.reset,

  'Login': function (browser) {

    browser.url(browser.launchUrl)

    login(browser, PROJECT_EMAIL, PROJECT_PASSWORD)

    browser.waitForElementVisible('.main-content', 5000)
    
    browser.end()
  },
}
