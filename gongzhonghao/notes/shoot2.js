// 用 playwright-core + 系统 Chrome 对 9 张卡片精确截 1080x1440
const { chromium } = require('C:/Users/22129/AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright-core');
const path = require('path');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true
  });
  const page = await browser.newPage({ viewport: { width: 1200, height: 1600 } });
  const fileUrl = 'file:///' + path.resolve(__dirname, 'notes.html').replace(/\\/g, '/');
  const outDir = path.join(__dirname, 'img');
  fs.mkdirSync(outDir, { recursive: true });

  const names = [
    '01-封面', '02-什么是七宗罪七美德', '03-七宗罪', '04-七美德',
    '05-怎么玩', '06-报告长什么样', '07-适合谁', '08-商品卡', '09-结尾'
  ];

  for (let i = 0; i < 9; i++) {
    await page.goto(fileUrl + '?s=' + i, { waitUntil: 'load' });
    await page.waitForTimeout(300);
    const stage = page.locator('#s' + i);
    await stage.screenshot({ path: path.join(outDir, names[i] + '.png') });
    const size = fs.statSync(path.join(outDir, names[i] + '.png')).size;
    console.log(names[i] + ' -> ' + size + ' bytes');
  }

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error(e); process.exit(1); });
