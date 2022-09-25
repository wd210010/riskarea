import sys
import json
import requests

# 读取log文件 得到dict字典
with open(sys.argv[1],'r',encoding='utf-8') as risk_file:
    areas = json.load(risk_file)

high_areas = []
middle_areas = []

# 读取高风险地区数据存为列表
for ha in areas['data']['highlist']:
    for high_area in ha['communitys']:
        high_areas.append(ha['area_name']+high_area)

# 读取中风险地区数据存为列表
for ma in areas['data']['middlelist']:
    for middle_area in ma['communitys']:
        middle_areas.append(ma['area_name']+middle_area)

# 地址转换为经纬度函数
def address_to_gd(address):
    url = "https://api.map.baidu.com/geocoding/v3/?"
    params = {'ak':'B2GL0ohpoLwUGfSwEuyllsd3oEhAm4iX', 'output': 'json', 'address': address}
    result = requests.get(url, params)
    return [result.json()['result']['location']['lng'],result.json()['result']['location']['lat']]

# 地址列表转换为经纬度函数
def trans_gd(addr_list):
    gd = []
    err_addr = []

    for address in addr_list:
        try:
            gd.append(address_to_gd(address[0:60]))
        except:
            err_addr.append(address)

    return gd, err_addr


if __name__=="__main__":
    high_gd, high_err = trans_gd(high_areas)
    middle_gd, middle_err = trans_gd(middle_areas)
    print('高风险地区%d个,获取经纬度出错%d个。'%(len(high_gd),len(high_err)))
    print('中风险地区%d个,获取经纬度出错%d个。'%(len(middle_gd),len(middle_err)))
    # 高风险地区经纬度写入json文件
    with open('./data/high_'+sys.argv[1][7:-3]+'json','w') as f:
        json.dump(high_gd,f)
    # 中风险地区经纬度写入json文件
    with open('./data/middle_'+sys.argv[1][7:-3] +'json','w') as f:
        json.dump(middle_gd,f)
    print('已写入json文件。')