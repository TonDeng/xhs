// 检查每张卡片是否有元素溢出 1080x1440 边界
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
    const problems = await page.evaluate(() => {
      const stage = document.getElementById('s' + document.querySelector('.stage:not(.hidden)')?.id?.slice(1) || '0');
      const sr = stage.getBoundingClientRect();
      const issues = [];
      stage.querySelectorAll('*').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 && r.height === 0) return;
        const pad = 2;
        if (r.left < sr.left - pad || r.right > sr.right + pad || r.top < sr.top - pad || r.bottom > sr.bottom + pad) {
          const cls = el.className && typeof el.className === 'string' ? el.className.slice(0, 30) : el.tagName;
          const txt = (el.textContent || '').trim().slice(0, 20);
          issues.push(`${el.tagName}.${cls} [${txt}] L${Math.round(r.left)} T${Math.round(r.top)} R${Math.round(r.right)} B${Math.round(r.bottom)}`);
        }
      });
      // 计算实际内容高度（stage 内所有元素的最大 bottom）
      let maxBottom = 0;
      stage.querySelectorAll('*').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.height > 0 && r.bottom > maxBottom) maxBottom = r.bottom;
      });
      return { issues: issues.slice(0, 12), maxBottom: Math.round(maxBottom), stageBottom: Math.round(sr.bottom), overflow: maxBottom > sr.bottom + 2 };
    });
    console.log(`s${i}: overflow=${problems.overflow} maxBottom=${problems.maxBottom}/${problems.stageBottom} issues=${problems.issues.length}`);
    problems.issues.slice(0, 6).forEach(x => console.log('   ' + x));
  }

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error(e); process.exit(1); });
