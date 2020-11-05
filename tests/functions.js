
function login (browser, email, password) {

  browser.url(browser.launchUrl);

  // Login
  browser.waitForElementVisible('input[id=loginEmail]', 5000);
  browser.setValue("input[id=loginEmail]", email);
  browser.setValue("input[id=loginPassword]", password);
  browser.click('button[type=submit]');
}

module.exports = {
  login,
}