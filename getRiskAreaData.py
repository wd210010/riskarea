import json
import requests
import time
import hashlib

# 时间戳  1663384497
timestamp = str(int((time.time())))
# 其他参数
token = '23y0ufFl5YxIyGrI8hWRUZmKkvtSjLQA'
nonce = '123456789abcdefg'
passid = 'zdww'
key = "3C502C97ABDA40D0A60FBEE50FAAD1DA"

# zdww签名
# 加入编码1663384589fTN2pfuisxTavbTuYVSsNJHetwq5bJvCQkjjtiLM2dCratiA1663384589
zdwwsign = timestamp + 'fTN2pfuisxTavbTuYVSsNJHetwq5bJvC' + 'QkjjtiLM2dCratiA' + timestamp
# 哈希值运算  42BA04239CFBD501AEB8D9839F04E68E32D1A9F5DEFA7FF49F1FF36A02B38DBA
hsobj = hashlib.sha256()
hsobj.update(zdwwsign.encode('utf-8'))
zdwwsignature = hsobj.hexdigest().upper()

# 得到header签名 EC1AE9461C53BF398C0616ABEADAC5AF047DD36C19EAD7E51FC2606770842847
has256 = hashlib.sha256()
sigh_header = timestamp + token + nonce + timestamp
has256.update(sigh_header.encode('utf-8'))
signatureHeader = has256.hexdigest().upper()

url = 'https://bmfw.www.gov.cn/bjww/interface/interfaceJson'
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    # "Content-Length": "235",
    "Content-Type": "application/json; charset=UTF-8",
    "Host": "bmfw.www.gov.cn",
    "Origin": "http://bmfw.www.gov.cn",
    "Referer": "http://bmfw.www.gov.cn/yqfxdjcx/risk.html",
    # "Sec-Fetch-Dest": "empty",
    # "Sec-Fetch-Mode": "cors",
    # "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0",
    "x-wif-nonce": "QkjjtiLM2dCratiA",
    "x-wif-paasid": "smt-application",
    "x-wif-signature": zdwwsignature,
    "x-wif-timestamp": timestamp
}
params = {
    'appId': "NcApplication",
    'paasHeader': "zdww",
    'timestampHeader': timestamp,
    'nonceHeader': "123456789abcdefg",
    'signatureHeader': signatureHeader,
    'key': "3C502C97ABDA40D0A60FBEE50FAAD1DA"
}
#post获取数据   注意时间戳不能超过180s
response = requests.post(url, headers=headers, json=params)
# 转换为字典
data_dict = json.loads(response.text)
#获得风险表发布的日期和事件
public_time = data_dict['data']['end_update_time'].split()

# 保存risk_data 日期 时间.log
with open('./data/risk_data' + ' ' + public_time[0] + ' ' + public_time[1] + '.log', 'w', encoding='utf-8') as f:
    f.write(response.text)