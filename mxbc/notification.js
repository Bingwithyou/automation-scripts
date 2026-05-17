const https = require('https');

const LOG_FILE = 'mxbc_log.txt';

function formatMarkdownLine(text) {
  const stripped = String(text || '').trim();
  if (!stripped) return '';
  if (stripped.startsWith('##') || stripped.startsWith('###')) return stripped;
  if (stripped.startsWith('```')) return stripped;
  if (stripped.startsWith('===') && stripped.endsWith('===')) {
    return `## ${stripped.replace(/^=+|=+$/g, '').trim()}`;
  }
  if (stripped.startsWith('- ')) return stripped;
  return `- ${stripped}`;
}

function addLog(text) {
  const fs = require('fs');
  const formatted = formatMarkdownLine(text);
  console.log(formatted);
  fs.appendFileSync(LOG_FILE, `${formatted}\n`, 'utf8');
}

function ensureEnv(keys) {
  const missing = keys.filter((key) => !process.env[key]);
  if (missing.length > 0) {
    console.log(`❌ 缺少必要环境变量: ${missing.join(', ')}`);
    process.exit(0);
  }
}

function sendServerChan(title, desp) {
  const sendKey = process.env.SERVER_CHAN_SEND_KEY;
  if (!sendKey) {
    console.log('⚠️ 未设置 SERVER_CHAN_SEND_KEY，跳过推送');
    return Promise.resolve();
  }

  const body = new URLSearchParams({ title, desp }).toString();

  return new Promise((resolve) => {
    const req = https.request(
      {
        hostname: 'sctapi.ftqq.com',
        port: 443,
        path: `/${sendKey}.send`,
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Content-Length': Buffer.byteLength(body),
        },
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          if (res.statusCode === 200) {
            console.log('✅ Server酱推送成功');
          } else {
            console.log(`❌ Server酱推送失败: ${res.statusCode}`);
          }
          resolve(data);
        });
      }
    );

    req.on('error', (error) => {
      console.log(`❌ Server酱请求异常: ${error.message}`);
      resolve();
    });

    req.write(body);
    req.end();
  });
}

module.exports = {
  LOG_FILE,
  addLog,
  ensureEnv,
  sendServerChan,
};
