// 将 notes.html 中 9 张卡片逐张截图为 1080x1440 PNG
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1440 } });
  const fileUrl = 'file:///' + path.resolve(__dirname, 'notes.html').replace(/\\/g, '/');
  const outDir = path.join(__dirname, 'img');
  fs.mkdirSync(outDir, { recursive: true });

  const names = [
    '01-封面',
    '02-什么是七宗罪七美德',
    '03-七宗罪',
    '04-七美德',
    '05-怎么玩',
    '06-报告长什么样',
    '07-适合谁',
    '08-商品卡',
    '09-结尾'
  ];

  for (let i = 0; i < 9; i++) {
    await page.goto(fileUrl + '?s=' + i, { waitUntil: 'load' });
    // 去掉 body 边距，让 stage 顶格显示
    await page.addStyleTag({ content: 'html,body{margin:0!important;padding:0!important;background:#000}' });
    const file = path.join(outDir, names[i] + '.png');
    await page.screenshot({ path: file });
    const size = fs.statSync(file).size;
    console.log(names[i] + ' -> ' + size + ' bytes');
  }

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error(e); process.exit(1); });
