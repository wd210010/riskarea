import sys
import json
import requests
import numpy as np
import pandas as pd
import sqlalchemy
import cx_Oracle

cx_Oracle.init_oracle_client('C:\oracle\instantclient_21_6')

# 读取log文件 得到dict字典
with open('./data/risk_data 2022-09-27 16时.log', 'r', encoding='utf-8') as risk_file:
    areas = json.load(risk_file)

# high_arears = []
middle_areas = []


# # 读取高风险地区数据存为列表
# for ha in areas['data']['highlist']:
#     for high_area in ha['communitys']:
#         high_areas.append(ha['area_name']+high_area)

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
    return df


df = get_risk_area_info(areas, 'middle')

# 去掉community长度超过1000的部分，写入数据库不得超过1000
def len_control(str):
    return str[0:1000]


df['community'] = df['community'].map(len_control)

with open('./data/middle_risk_data 2022-09-27 16时.json', 'r', encoding='utf-8') as risk_file:
    gd = json.load(risk_file)

df['location'] = gd

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

write_to_oracle(df)

# 读取中风险地区数据存为列表
# for ma in areas['data']['middlelist']:
#     for middle_area in ma['communitys']:
#         middle_areas.append(ma['area_name'] + middle_area)
#
#
# # 地址转换为经纬度函数
# def address_to_gd(address):
#     url = "https://api.map.baidu.com/geocoding/v3/?"
#     params = {'ak': 'B2GL0ohpoLwUGfSwEuyllsd3oEhAm4iX', 'output': 'json', 'address': address}
#     result = requests.get(url, params)
#     return [result.json()['result']['location']['lng'], result.json()['result']['location']['lat']]
#
#
# # 地址列表转换为经纬度函数
# def trans_gd(addr_list):
#     gd = []
#     err_addr = []
#
#     for address in addr_list:
#         try:
#             gd.append(address_to_gd(address[0:60]))
#         except:
#             err_addr.append(address)
#
#     return gd, err_addr


# if __name__ == "__main__":
#     high_gd, high_err = trans_gd(high_areas)
#     middle_gd, middle_err = trans_gd(middle_areas)
#     print('高风险地区%d个,获取经纬度出错%d个。' % (len(high_gd), len(high_err)))
#     print('中风险地区%d个,获取经纬度出错%d个。' % (len(middle_gd), len(middle_err)))
#     # 高风险地区经纬度写入json文件
#     with open('./data/high_' + sys.argv[1][7:-3] + 'json', 'w') as f:
#         json.dump(high_gd, f)
#     # 中风险地区经纬度写入json文件
#     with open('./data/middle_' + sys.argv[1][7:-3] + 'json', 'w') as f:
#         json.dump(middle_gd, f)
#     print('已写入json文件。')
