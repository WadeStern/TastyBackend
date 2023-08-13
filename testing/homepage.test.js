const puppeteer = require("puppeteer");

test("Get Title", async () => {
  const browser = await puppeteer.launch()
  const page = await browser.newPage()
  await page.goto('http://frontend.staging.wadestern.com/')
  const title = await page.title()
  console.log(title)
  await browser.close()
});
test("Get Pythontest", async () => {
  const browser = await puppeteer.launch({});
  const page = await browser.newPage();
  await page.goto("http://frontend.staging.wadestern.com/pythontest/");
  await page.waitForXPath('/html/body/div/div/div[2]');
  let [el] = await page.$x('/html/body/div/div/div[2]');
  const pythontest = await page.evaluate(name => name.innerText, el);
  console.log(pythontest);
  await browser.close();
});
test("Get 2nd title", async () => {
  const browser = await puppeteer.launch({});
  const page = await browser.newPage();
  await page.goto("http://frontend.staging.wadestern.com/");
  await page.waitForXPath('/html/body/div/div/div[2]/div[2]/div[2]/div/h3');
  let [el] = await page.$x('/html/body/div/div/div[2]/div[2]/div[2]/div/h3');
  const names = await page.evaluate(name => name.innerText, el);
  console.log(names);
  await browser.close();
});
