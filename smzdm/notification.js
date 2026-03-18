const got = require('got');

async function sendServerChan(title, desp) {
  const sendKey = process.env.SERVER_CHAN_SEND_KEY;
  if (!sendKey) {
    console.log('⚠️ 未设置 SERVER_CHAN_SEND_KEY，跳过推送');
    return;
  }

  const url = `https://sctapi.ftqq.com/${sendKey}.send`;
  
  try {
    const response = await got.post(url, {
      form: {
        title,
        desp
      },
      responseType: 'json'
    });

    if (response.body.code === 0) {
      console.log('✅ Server酱推送成功');
    } else {
      console.log(`❌ Server酱推送失败: ${response.body.message}`);
    }
  } catch (error) {
    console.log(`❌ Server酱请求异常: ${error.message}`);
  }
}

module.exports = { sendServerChan };
