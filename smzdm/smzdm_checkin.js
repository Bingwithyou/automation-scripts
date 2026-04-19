/*
smzdm 签到脚本
项目地址: https://github.com/hex-ci/smzdm_script

cron: 10 8 * * *
*/

const Env = require('./env');
const { SmzdmBot, requestApi, removeTags, getEnvCookies, wait } = require('./bot');
const CryptoJS = require('crypto-js');

const $ = new Env('smzdm 签到');

class SmzdmCheckinBot extends SmzdmBot {
  constructor(cookie, sk) {
    super(cookie);

    this.sk = sk ? sk.trim() : '';
  }

  async run() {
    const { msg: msg1 } = await this.checkin();

    const { msg: msg2 } = await this.allReward();

    const { msg: msg3 } = await this.extraReward();

    return `${msg1}${msg2}${msg3}`;
  }

  async checkin() {
    const { isSuccess, data, response } = await requestApi('https://user-api.smzdm.com/checkin', {
      method: 'post',
      headers: this.getHeaders(),
      data: {
        touchstone_event: '',
        sk: this.sk || '1',
        token: this.token,
        captcha: ''
      }
    });

    if (isSuccess) {
      let msg = `⭐签到成功${data.data.daily_num}天
🏅金币: ${data.data.cgold}
🏅碎银: ${data.data.pre_re_silver}
🏅补签卡: ${data.data.cards}`;

      await wait(3, 10);

      const vip = await this.getVipInfo();

      if (vip) {
        msg += `\n🏅经验: ${vip.vip.exp_current}
🏅值会员等级: ${vip.vip.exp_level}
🏅值会员经验: ${vip.vip.exp_current_level}
🏅值会员有效期至: ${vip.vip.exp_level_expire}`;
      }

      $.log(`${msg}\n`);

      return {
        isSuccess,
        msg: `${msg}\n\n`
      };
    }
    else {
      $.log(`签到失败！${response}`);

      return {
        isSuccess,
        msg: '签到失败！'
      };
    }
  }

  async allReward() {
    const { isSuccess, data, response } = await requestApi('https://user-api.smzdm.com/checkin/all_reward', {
      method: 'post',
      headers: this.getHeaders(),
      debug: process.env.SMZDM_DEBUG
    });

    if (isSuccess) {
      const msg1 = `${data.data.normal_reward.reward_add.title}: ${data.data.normal_reward.reward_add.content}`;

      let msg2 = '';

      if (data.data.normal_reward.gift.title) {
        msg2 = `${data.data.normal_reward.gift.title}: ${data.data.normal_reward.gift.content_str}`;
      }
      else {
        msg2 = `${data.data.normal_reward.gift.sub_content}`;
      }

      $.log(`${msg1}\n${msg2}\n`);

      return {
        isSuccess,
        msg: `${msg1}\n${msg2}\n\n`
      };
    }
    else {
      if (data.error_code != '4') {
        $.log(`查询奖励失败！${response}`);
      }

      return {
        isSuccess,
        msg: ''
      };
    }
  }

  async extraReward() {
    const isContinue = await this.isContinueCheckin();

    if (!isContinue) {
      const msg = '今天没有额外奖励';

      $.log(`${msg}\n`);

      return {
        isSuccess: false,
        msg: `${msg}\n`
      };
    }

    await wait(5, 10);

    const { isSuccess, data, response } = await requestApi('https://user-api.smzdm.com/checkin/extra_reward', {
      method: 'post',
      headers: this.getHeaders()
    });

    if (isSuccess) {
      const msg = `${data.data.title}: ${removeTags(data.data.gift.content)}`;

      $.log(msg);

      return {
        isSuccess: true,
        msg: `${msg}\n`
      };
    }
    else {
      $.log(`领取额外奖励失败！${response}`);

      return {
        isSuccess: false,
        msg: ''
      };
    }
  }

  async isContinueCheckin() {
    const { isSuccess, data, response } = await requestApi('https://user-api.smzdm.com/checkin/show_view_v2', {
      method: 'post',
      headers: this.getHeaders()
    });

    if (isSuccess) {
      const result = data.data.rows.find(item => item.cell_type == '18001');

      return result.cell_data.checkin_continue.continue_checkin_reward_show;
    }
    else {
      $.log(`查询是否有额外奖励失败！${response}`);

      return false;
    }
  }

  async getVipInfo() {
    const { isSuccess, data, response } = await requestApi('https://user-api.smzdm.com/vip', {
      method: 'post',
      headers: this.getHeaders(),
      data: {
        token: this.token
      }
    });

    if (isSuccess) {
      return data.data;
    }
    else {
      $.log(`查询信息失败！${response}`);

      return false;
    }
  }
}

function random32() {
  const chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  let result = '';

  for (let i = 0; i < 32; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  return result;
}

function getSk(cookie) {
  const matchUserId = cookie.match(/smzdm_id=([^;]*)/);

  if (!matchUserId) {
    return ''
  }

  const userId = matchUserId[1];
  const deviceId = getDeviceId(cookie);
  const key = CryptoJS.enc.Utf8.parse('geZm53XAspb02exN');
  const cipherText = CryptoJS.DES.encrypt(userId + deviceId, key, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7
  });

  return cipherText.toString();
}

function getDeviceId(cookie) {
  const matchDeviceId = cookie.match(/device_id=([^;]*)/);

  if (matchDeviceId) {
    return matchDeviceId[1];
  }

  return random32();
}

!(async () => {
  $.checkSecrets(['SMZDM_COOKIE']);
  const cookies = getEnvCookies();

  if (cookies === false) {
    $.log('\n请先设置 SMZDM_COOKIE 环境变量');

    return;
  }

  let sks = [];

  if (process.env.SMZDM_SK) {
    if (process.env.SMZDM_SK.indexOf('&') > -1) {
      sks = process.env.SMZDM_SK.split('&');
    }
    else if (process.env.SMZDM_SK.indexOf('\n') > -1) {
      sks = process.env.SMZDM_SK.split('\n');
    }
    else {
      sks = [process.env.SMZDM_SK];
    }
  }

  let notifyContent = '';

  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i];

    if (!cookie) {
      continue;
    }

    let sk = sks[i];
    if (!sk) {
      sk = getSk(cookie)
    }

    if (i > 0) {
      await wait(10, 30);
    }

    const sep = `\n****** 账号${i + 1} ******\n`;

    $.log(sep);

    const bot = new SmzdmCheckinBot(cookie, sk);
    const msg = await bot.run();

    notifyContent += sep + msg + '\n';
  }

  $.log();
})().catch((e) => {
  $.log('', `❌ ${$.name}, 失败! 原因: ${e}!`, '')
}).finally(() => {
  $.done();
});
