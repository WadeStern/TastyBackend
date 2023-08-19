const puppeteer = require("puppeteer");
jest.setTimeout(60000);

const prodorstaging = process.env.prodorstaging;

test("Get Title", async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox']
  });
  const page = await browser.newPage()
  await page.goto('http://frontend.${prodorstaging}.wadestern.com/', {waitUntil: 'load', timeout: 20000})
  const title = await page.title()
  console.log(title)
  await browser.close()
});
test("Get Pythontest", async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox']
  });
  const page = await browser.newPage();
  await page.goto("http://frontend.${prodorstaging}.wadestern.com/pythontest/", {waitUntil: 'load', timeout: 20000});
  await page.waitForXPath('/html/body/div/div/div[2]');
  let [el] = await page.$x('/html/body/div/div/div[2]');
  const pythontest = await page.evaluate(name => name.innerText, el);
  console.log(pythontest);
  await browser.close();
});
test("Get 2nd title", async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox']
  });
  const page = await browser.newPage();
  await page.goto("http://frontend.${prodorstaging}.wadestern.com/", {waitUntil: 'load', timeout: 20000});
  await page.waitForXPath('/html/body/div/div/div[2]/div[2]/div[2]/div/h3');
  let [el] = await page.$x('/html/body/div/div/div[2]/div[2]/div[2]/div/h3');
  const names = await page.evaluate(name => name.innerText, el);
  console.log(names);
  await browser.close();
});
