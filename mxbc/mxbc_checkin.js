const crypto = require('crypto');
const https = require('https');
const fs = require('fs');

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

const PRIVATE_KEY = `-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCtypUdHZJKlQ9L
L6lIJSphnhqjke7HclgWuWDRWvzov30du235cCm13mqJ3zziqLCwstdQkuXo9sOP
Ih94t6nzBHTuqYA1whrUnQrKfv9X4/h3QVkzwT+xWflE+KubJZoe+daLKkDeZjVW
nUku8ov0E5vwADACfntEhAwiSZUALX9UgNDTPbj5ESeII+VztZ/KOFsRHMTfDb1G
IR/dAc1mL5uYbh0h2Fa/fxRPgf7eJOeWGiygesl3CWj0Ue13qwX9PcG7klJXfToI
576MY+A7027a0aZ49QhKnysMGhTdtFCksYG0lwPz3bIR16NvlxNLKanc2h+ILTFQ
bMW/Y3DRAgMBAAECggEBAJGTfX6rE6zX2bzASsu9HhgxKN1VU6/L70/xrtEPp4SL
SpHKO9/S/Y1zpsigr86pQYBx/nxm4KFZewx9p+El7/06AX0djOD7HCB2/+AJq3iC
5NF4cvEwclrsJCqLJqxKPiSuYPGnzji9YvaPwArMb0Ff36KVdaHRMw58kfFys5Y2
HvDqh4x+sgMUS7kSEQT4YDzCDPlAoEFgF9rlXnh0UVS6pZtvq3cR7pR4A9hvDgX9
wU6zn1dGdy4MEXIpckuZkhwbqDLmfoHHeJc5RIjRP7WIRh2CodjetgPFE+SV7Sdj
ECmvYJbet4YLg+Qil0OKR9s9S1BbObgcbC9WxUcrTgECgYEA/Yj8BDfxcsPK5ebE
9N2teBFUJuDcHEuM1xp4/tFisoFH90JZJMkVbO19rddAMmdYLTGivWTyPVsM1+9s
tq/NwsFJWHRUiMK7dttGiXuZry+xvq/SAZoitgI8tXdDXMw7368vatr0g6m73cBK
jZWxSHjK9/KVquVr7BoXFm+YxaECgYEAr3sgVNbr5ovx17YriTqe1FLTLMD5gPrz
ugJj7nypDYY59hLlkrA/TtWbfzE+vfrN3oRIz5OMi9iFk3KXFVJMjGg+M5eO9Y8m
14e791/q1jUuuUH4mc6HttNRNh7TdLg/OGKivE+56LEyFPir45zw/dqwQM3jiwIz
yPz/+bzmfTECgYATxrOhwJtc0FjrReznDMOTMgbWYYPJ0TrTLIVzmvGP6vWqG8rI
S8cYEA5VmQyw4c7G97AyBcW/c3K1BT/9oAj0wA7wj2JoqIfm5YPDBZkfSSEcNqqy
5Ur/13zUytC+VE/3SrrwItQf0QWLn6wxDxQdCw8J+CokgnDAoehbH6lTAQKBgQCE
67T/zpR9279i8CBmIDszBVHkcoALzQtU+H6NpWvATM4WsRWoWUx7AJ56Z+joqtPK
G1WztkYdn/L+TyxWADLvn/6Nwd2N79MyKyScKtGNVFeCCJCwoJp4R/UaE5uErBNn
OH+gOJvPwHj5HavGC5kYENC1Jb+YCiEDu3CB0S6d4QKBgQDGYGEFMZYWqO6+LrfQ
ZNDBLCI2G4+UFP+8ZEuBKy5NkDVqXQhHRbqr9S/OkFu+kEjHLuYSpQsclh6XSDks
5x/hQJNQszLPJoxvGECvz5TN2lJhuyCupS50aGKGqTxKYtiPHpWa8jZyjmanMKnE
dOGyw/X4SFyodv8AEloqd81yGg==
-----END PRIVATE KEY-----`;

const APP_ID = 'd82be6bbc1da11eb9dd000163e122ecb';
const BASE_URL = 'https://mxsa.mxbc.net';
const VERSION = '2.8.21';
const USER_AGENT =
  'Mozilla/5.0 (iPhone; CPU iPhone OS 26_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.70(0x1800463a) NetType/WIFI Language/zh_CN';
const REFERER = 'https://servicewechat.com/wx7696c66d2245d107/225/page-frame.html';
const DB_REDIRECT = 'https://76177-activity.dexfu.cn/chw/visual-editor/skins?id=216593&orderType=1';

function createSign(params) {
  const signSource = Object.keys(params)
    .sort()
    .filter((key) => params[key] !== undefined && params[key] !== null && params[key] !== '')
    .map((key) => {
      const value = params[key];
      return `${key}=${typeof value === 'object' ? JSON.stringify(value) : String(value)}`;
    })
    .join('&');

  const signer = crypto.createSign('RSA-SHA256');
  signer.update(signSource);
  const signature = signer.sign(PRIVATE_KEY, 'base64');
  return signature.replace(/\//g, '_').replace(/\+/g, '-');
}

function requestJson({ method, path, headers, body }) {
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname: 'mxsa.mxbc.net',
        port: 443,
        path,
        method,
        headers,
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          try {
            const parsed = data ? JSON.parse(data) : {};
            resolve({ statusCode: res.statusCode, body: parsed, raw: data });
          } catch (error) {
            reject(new Error(`接口返回非 JSON: status=${res.statusCode}, body=${data.slice(0, 300)}`));
          }
        });
      }
    );

    req.on('error', reject);
    req.setTimeout(30000, () => {
      req.destroy(new Error('请求超时'));
    });

    if (body) {
      req.write(body);
    }
    req.end();
  });
}

function buildCommonHeaders() {
  return {
    'Access-Token': process.env.MXBC_ACCESS_TOKEN,
    'x-ssos-cid': process.env.MXBC_SSOS_CID,
    'traceNo': '',
    'content-type': 'application/json',
    version: VERSION,
    'Accept-Encoding': 'identity',
    'User-Agent': USER_AGENT,
    Referer: REFERER,
    Connection: 'keep-alive',
    Host: 'mxsa.mxbc.net',
  };
}

async function getLoginUrl() {
  const t = Date.now();
  const params = {
    appId: APP_ID,
    dbredirect: DB_REDIRECT,
    t,
  };
  const sign = createSign(params);
  const path = `/api/v1/duiba/getLoginUrl?dbredirect=${encodeURIComponent(DB_REDIRECT)}&t=${t}&appId=${APP_ID}&sign=${encodeURIComponent(sign)}`;

  return requestJson({
    method: 'GET',
    path,
    headers: buildCommonHeaders(),
  });
}

async function getCustomerInfo() {
  const t = Date.now();
  const params = {
    appId: APP_ID,
    t,
  };
  const sign = createSign(params);
  const path = `/api/v1/customer/info?t=${t}&appId=${APP_ID}&sign=${encodeURIComponent(sign)}`;

  return requestJson({
    method: 'GET',
    path,
    headers: buildCommonHeaders(),
  });
}

async function main() {
  ensureEnv(['MXBC_ACCESS_TOKEN', 'MXBC_SSOS_CID']);

  addLog('=== 蜜雪冰城每日签到 ===');

  const loginResult = await getLoginUrl();
  addLog(`getLoginUrl HTTP 状态: ${loginResult.statusCode}`);

  if (loginResult.statusCode !== 200 || loginResult.body.code !== 0) {
    addLog('```json');
    addLog(JSON.stringify(loginResult.body, null, 2));
    addLog('```');
    throw new Error('getLoginUrl 请求失败');
  }

  const loginUrl = loginResult.body?.data?.loginUrl || loginResult.body?.data || '';
  addLog('✅ getLoginUrl 请求成功，视为今日签到已完成');
  if (loginUrl) {
    addLog(`登录链接已返回: ${String(loginUrl).slice(0, 120)}...`);
  }

  const infoResult = await getCustomerInfo();
  addLog(`customer/info HTTP 状态: ${infoResult.statusCode}`);

  if (infoResult.statusCode !== 200 || infoResult.body.code !== 0) {
    addLog('```json');
    addLog(JSON.stringify(infoResult.body, null, 2));
    addLog('```');
    throw new Error('customer/info 请求失败');
  }

  const customerPoint = infoResult.body?.data?.customerPoint;
  if (customerPoint !== undefined) {
    addLog(`当前雪王币: ${customerPoint}`);
  } else {
    addLog('⚠️ 未获取到当前雪王币');
  }
}

main().catch((error) => {
  addLog(`❌ 蜜雪冰城任务异常: ${error.message}`);
  process.exitCode = 1;
});
