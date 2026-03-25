const fs = require('fs');
const path = require('path');
const { sendServerChan } = require('./notification');

const LOG_FILE = path.resolve(process.cwd(), 'smzdm_log.txt');

async function sendSummary() {
  if (!fs.existsSync(LOG_FILE)) {
    console.log('⚠️ 日志文件不存在，跳过推送');
    return;
  }

  const content = fs.readFileSync(LOG_FILE, 'utf-8');
  if (!content.trim()) {
    console.log('⚠️ 日志内容为空，跳过推送');
    return;
  }

  console.log('🚀 开始推送 SMZDM 任务汇总...');
  await sendServerChan('什么值得买任务汇总', content);

  // 发送后删除日志文件
  try {
    fs.unlinkSync(LOG_FILE);
    console.log('✅ 已清理本地日志文件');
  } catch (err) {
    console.error(`❌ 清理日志文件失败: ${err.message}`);
  }
}

sendSummary().catch(err => {
  console.error(`❌ 推送汇总失败: ${err.message}`);
});
