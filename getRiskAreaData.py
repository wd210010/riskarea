import json
import requests
import time
import hashlib
import pandas as pd
import numpy as np
import sqlalchemy
import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir=r"/Users/gaopeng/lib/")

# cx_Oracle.init_oracle_client('C:\oracle\instantclient_21_6')

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
# post获取数据   注意时间戳不能超过180s
response = requests.post(url, headers=headers, json=params)
# 转换为字典
data_dict = json.loads(response.text)
# 获得风险表发布的日期和事件
public_time = data_dict['data']['end_update_time'].split()

# 保存risk_data 日期 时间.log
filepath = './data/risk_data' + ' ' + public_time[0] + ' ' + public_time[1] + '.log'
with open('./data/risk_data' + ' ' + public_time[0] + ' ' + public_time[1] + '.log', 'w', encoding='utf-8') as f:
    f.write(response.text)
    print("%s数据写入文件" % public_time[0] + public_time[1])


# 地址转换为经纬度函数,输出为字符串'117.23456789899,39.12167079728333'
def address_to_gd(address):
    url = "https://api.map.baidu.com/geocoding/v3/?"
    params = {'ak': 'B2GL0ohpoLwUGfSwEuyllsd3oEhAm4iX', 'output': 'json', 'address': address}
    result = requests.get(url, params)
    return str(result.json()['result']['location']['lng']) + ',' + str(result.json()['result']['location']['lat'])


# 地址列表转换为经纬度函数,gd记录成功转换的经纬度，err_addr记录失败的地址
def trans_gd(addr_list):
    gd = []
    err_addr = []
    for address in addr_list:
        try:
            gd.append(address_to_gd(address[0:60]))  # 百度地图查询最多60个字符
        except:
            err_addr.append(address)
    return gd, err_addr


# 从data_dict中分离数据形成df areas为data_dict字典，risk_grade为high/middle
def get_risk_area_info(areas, risk_grade):
    public_date = pd.to_datetime(areas['data']['end_update_time'].split()[0], format='%Y-%m-%d')
    public_time = int(areas['data']['end_update_time'].split()[1][0:-1])
    province = []
    city = []
    county = []
    area_name = []
    communitys = []
    # 新建空白df 包括8个字段
    df = pd.DataFrame(data=None,
                      columns=['public_date', 'risk_grade', 'province', 'city', 'county', 'area_name', 'community',
                               'public_time', 'location'])
    # 读取风险地区数据存为列表 highlist  middlelist
    for area in areas['data'][risk_grade + 'list']:
        for community in area['communitys']:
            province.append(area['province'])
            city.append(area['city'])
            county.append(area['county'])
            area_name.append(area['area_name'])
            communitys.append(community)
    df['community'] = communitys
    df['area_name'] = area_name
    df['county'] = county
    df['city'] = city
    df['province'] = province
    df['public_date'] = public_date
    df['public_time'] = public_time
    df['risk_grade'] = risk_grade
    # 获取经纬度时的地址：天津市天津市河东区向阳楼街道昕旺南苑1号楼、2号楼
    address_list = df['province'] + df['city'] + df['county'] + df['community']
    gd_list, err_list = trans_gd(address_list)
    if err_list:
        print('地址转换出错，具体为：')
        print(err_list)
    df['location'] = gd_list
    return df


# 得到两个df中高风险地区
df_high = get_risk_area_info(data_dict, 'high')
df_middle = get_risk_area_info(data_dict, 'middle')

# 中高风险经纬度写入各自的json文件["117.27401777740407,39.123992248811625", "117.26206061242185,39.14177694126339",...]
high_path = './data/high_risk_data ' + public_time[0] + ' ' + public_time[1] + '.json'
# 高风险地区经纬度写入json文件
with open(high_path, 'w') as f:
    # location由dataframe转化为list后才能json格式化
    json.dump(np.array(df_high['location']).tolist(), f)
    print('已写入%s文件' % high_path)
# 中风险地区经纬度写入json文件
middle_path = './data/middle_risk_data ' + public_time[0] + ' ' + public_time[1] + '.json'
with open(middle_path, 'w') as f:
    json.dump(np.array(df_middle['location']).tolist(), f)
    print('已写入%s文件。' % middle_path)


# 两个df写入oracle数据库
# df to_sql写入速度很慢.缺省情况下，Pandas + SQLAlchemy将所有object(字符串 df.info()查看)列保存为Oracle DB中的CLOB，这使插入速度非常慢，需要给每个字符串改变类别为varchar
def write_to_oracle(df):
    engine = sqlalchemy.create_engine("oracle+cx_oracle://c##riskarea:Ben800208@124.221.228.171:1524/ORCLCDB")
    # 将所有的字符串均设置为varchar 速度提升100倍
    type_list = {'public_time': sqlalchemy.Integer(), 'public_date': sqlalchemy.Date(),
                 'risk_grade': sqlalchemy.types.VARCHAR(10), 'province': sqlalchemy.types.VARCHAR(10),
                 'city': sqlalchemy.types.VARCHAR(20), 'county': sqlalchemy.types.VARCHAR(50),
                 'area_name': sqlalchemy.types.VARCHAR(100), 'community': sqlalchemy.types.VARCHAR(1000),
                 'location': sqlalchemy.types.VARCHAR(50)}
    df.to_sql('risk_area', engine, index=False, if_exists='append', dtype=type_list)
    print('写入oracle数据库完成，共%d条数据' % (len(df)))


write_to_oracle(df_high)
write_to_oracle(df_middle)
