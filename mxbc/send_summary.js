const fs = require('fs');
const path = require('path');
const { LOG_FILE, sendServerChan } = require('./notification');

async function sendSummary() {
  if (process.env.COMBINED_SUMMARY_MODE === 'yes') {
    console.log('已启用统一汇总模式，跳过单独蜜雪冰城通知。');
    return;
  }

  const logPath = path.resolve(process.cwd(), LOG_FILE);
  if (!fs.existsSync(logPath)) {
    console.log('⚠️ 日志文件不存在，跳过推送');
    return;
  }

  const content = fs.readFileSync(logPath, 'utf-8').trim();
  if (!content) {
    console.log('⚠️ 日志内容为空，跳过推送');
    return;
  }

  await sendServerChan('蜜雪冰城每日汇总', content);
}

sendSummary().catch((error) => {
  console.error(`❌ 发送汇总失败: ${error.message}`);
});
