# -*- coding: utf-8 -*-
"""正弘城设备注册 + 请求签名 (小程序 v354 新版安全机制)

流程:
  1. GET  securities/rsa/pubkey      获取服务端 RSA 公钥 (无需签名)
  2. 本地生成 1024 位 RSA 密钥对, clientPublicKey = base64(X.509 SPKI DER)
  3. 用服务端公钥 PKCS1v1.5 分块(117B)加密注册体, base64 后 POST securities/devices/register
  4. 响应用客户端私钥 PKCS1v1.5 分块(128B)解密, 得到 accessToken/workKey 等会话数据
  5. 请求签名: SHA256(排序参数串 + 密钥)
     - useNewAlgorithm=false: 密钥 = WAP_KEYS[timestamp % 10]
     - useNewAlgorithm=true:  密钥 = signKey, 且路径参与签名
"""
import base64
import hashlib
import json
import os
import random
import string
import time

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

API_BASE = "https://m.zhcommerce.com/api/v3"
APP_KEY = "OW5OGNWC"
SESSION_FILE = os.path.expanduser("~/.zhcommerce/session.json")

WAP_KEYS = [
    "N94QKAZD289GQARELPOJQGZM8",
    "GFNCV79W9U1CYFEXQ904OI6BB",
    "C1BOEMXCP1A5KUBVQIXKGBH51",
    "0RU2DV7E67T7ZMPQXWAVD99MY",
    "EPOJKLVKIQQMGG9XWT9C28F5C",
    "8GTBBWEADC6RG237EUEC7KZFU",
    "1XP3TLH0BZMZS7TT3TF7JD500",
    "TNFVOH7WHTC4NCD6SI9QZ3W5N",
    "ZZNEL2ULF9TPAC9NU3493GL7I",
    "8SABWT2MB1JOHOM02QVN36TGI",
]


def random_mixed(length):
    alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
    return "".join(random.choice(alphabet) for _ in range(length))


# --- 会话持久化 ---

def load_session():
    try:
        with open(SESSION_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_session(data):
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.chmod(SESSION_FILE, 0o600)


def session_valid(sess):
    register_time = int(sess.get("registerTime") or 0)
    validity = int(sess.get("sessionValiditySeconds") or 0)
    if not register_time or not validity:
        return False
    return time.time() < register_time + validity - 300


# --- 设备注册 ---

def _import_pubkey(pubkey):
    try:
        return RSA.import_key(pubkey)
    except ValueError:
        return RSA.import_key(base64.b64decode(pubkey))


def get_pubkey(device_id):
    params = {"appKey": APP_KEY, "deviceId": device_id, "rnd": random_mixed(20)}
    resp = requests.get(f"{API_BASE}/securities/rsa/pubkey", params=params,
                        headers={"Content-Type": "application/json"}, timeout=(10, 30))
    data = resp.json()
    if data.get("errorCode") != "PUB-00000" or not (data.get("body") or {}).get("publicKey"):
        raise RuntimeError(f"获取RSA公钥失败: {json.dumps(data, ensure_ascii=False)[:500]}")
    return data["body"]["publicKey"]


def rsa_pkcs1_encrypt_chunks(public_key_pem, plaintext: bytes, chunk=117):
    cipher = PKCS1_v1_5.new(_import_pubkey(public_key_pem))
    out = b""
    for i in range(0, len(plaintext), chunk):
        out += cipher.encrypt(plaintext[i:i + chunk])
    return out


def rsa_pkcs1_decrypt_chunks(private_key, ciphertext: bytes, chunk=128):
    cipher = PKCS1_v1_5.new(private_key)
    out = b""
    for i in range(0, len(ciphertext), chunk):
        out += cipher.decrypt(ciphertext[i:i + chunk], sentinel=b"")
    return out


def register_device(device_id):
    """设备注册, 返回会话 dict (accessToken/workKey/useNewAlgorithm 等)"""
    public_key_pem = get_pubkey(device_id)
    client_key = RSA.generate(1024, e=65537)
    client_public_b64 = base64.b64encode(
        client_key.publickey().export_key(format="DER")).decode()
    payload = json.dumps(
        {"clientPublicKey": client_public_b64, "keySeed": random_mixed(30)},
        separators=(",", ":"), ensure_ascii=False)
    enc = rsa_pkcs1_encrypt_chunks(public_key_pem, payload.encode("utf-8"))
    req_body = base64.b64encode(enc).decode()
    params = {"appKey": APP_KEY, "deviceId": device_id, "rnd": random_mixed(20)}
    resp = requests.post(f"{API_BASE}/securities/devices/register", params=params,
                         data=json.dumps({"reqBody": req_body}),
                         headers={"Content-Type": "application/json", "EncryptRsa": "true"},
                         timeout=(10, 30))
    data = resp.json()
    if data.get("errorCode") != "PUB-00000" or not data.get("body"):
        raise RuntimeError(f"设备注册失败: {json.dumps(data, ensure_ascii=False)[:500]}")
    body = data["body"]
    if isinstance(body, str):
        ct = base64.b64decode(body)
        plain = rsa_pkcs1_decrypt_chunks(client_key, ct)
        body = json.loads(plain.decode("utf-8"))
    body["devicesRegisterCheck"] = True if body.get("useNewAlgorithm") else False
    body["signWithPath"] = True if body.get("signWithPath") else False
    return body


def ensure_session(device_id):
    """读会话缓存; 过期或无效则重新注册"""
    sess = load_session()
    if sess and session_valid(sess) and sess.get("accessToken"):
        return sess
    sess = register_device(device_id)
    save_session(sess)
    return sess


# --- 签名 ---

def build_sign(params, path, timestamp, sess, variant=0):
    """与小程序 v354 一致的签名构造

    variant=0: 忠实还原 JS 实现 (路径直接拼接参数串, 末尾去一个 &, 追加密钥)
    variant=1: 路径后补 & 再拼参数
    """
    joined = "".join(
        f"{k}={params[k]}&" for k in sorted(params) if params[k] not in ("", None))
    joined = joined[:-1] if joined else ""
    if sess.get("devicesRegisterCheck"):
        key = sess["signKey"]
        path_part = path if sess.get("signWithPath") else ""
        src = path_part + joined if variant == 0 else path_part + "&" + joined
    else:
        key = WAP_KEYS[timestamp % 10]
        src = joined
    return hashlib.sha256((src + key).encode("utf-8")).hexdigest()
