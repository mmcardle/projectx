module.exports = {
  beforeEach: function(browser, done) {
    browser.resizeWindow(1200, 768);
    done();
  },
};