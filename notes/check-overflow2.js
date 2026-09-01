// 精确检查 .center 内容是否溢出（scrollHeight vs clientHeight）
const { chromium } = require('C:/Users/22129/AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright-core');
const path = require('path');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true
  });
  const page = await browser.newPage({ viewport: { width: 1200, height: 1600 } });
  const fileUrl = 'file:///' + path.resolve(__dirname, 'notes.html').replace(/\\/g, '/');

  for (let i = 0; i < 9; i++) {
    await page.goto(fileUrl + '?s=' + i, { waitUntil: 'load' });
    await page.waitForTimeout(200);
    const info = await page.evaluate(() => {
      const stage = document.querySelector('.stage:not(.hidden)');
      const center = stage.querySelector('.center');
      const cs = getComputedStyle(center);
      return {
        scrollH: center.scrollHeight,
        clientH: center.clientHeight,
        padTop: cs.paddingTop,
        padBottom: cs.paddingBottom,
        stageH: stage.getBoundingClientRect().height,
        clipped: center.scrollHeight > center.clientHeight + 4,
        // 找出具体溢出元素
        overflowing: Array.from(center.children).map(ch => ({
          tag: ch.tagName, cls: (ch.className||'').toString().slice(0,25),
          scrollH: ch.scrollHeight, clientH: ch.clientHeight
        })).filter(x => x.scrollH > x.clientH + 4)
      };
    });
    console.log(`s${i}: clipped=${info.clipped} center ${info.scrollH}px content vs ${info.clientH}px visible (padding ${info.padTop}/${info.padBottom})`);
    info.overflowing.forEach(x => console.log('   overflow: ' + x.tag + '.' + x.cls + ' ' + x.scrollH + '>' + x.clientH));
  }

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error(e); process.exit(1); });
