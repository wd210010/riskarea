import flask, json
import sqlalchemy
import pandas as pd
import numpy as np
import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir=r"/Users/gaopeng/lib/")

# 实例化api，把当前这个python文件当作一个服务，__name__代表当前这个python文件
api = flask.Flask(__name__)

# 'index'是接口路径，methods不写，默认get请求
@api.route('/index', methods=['get'])
# get方式访问
def index():
    ren = {'msg': '成功访问首页', 'msg_code': 200}
    # json.dumps 序列化时对中文默认使用的ascii编码.想输出中文需要指定ensure_ascii=False
    return json.dumps(ren, ensure_ascii=False)

@api.route('/getdata',methods=['post'])
def getdata():
    # url?date=2022-09-22&id=igao
    date = flask.request.args.get('date')
    id = flask.request.args.get('id')
    engine = sqlalchemy.create_engine("oracle+cx_oracle://c##riskarea:Ben800208@124.221.228.171:1524/ORCLCDB")
    sql_str = "select location from risk_area where public_date=to_date('%s','YYYY-MM-DD')"%date
    df = pd.read_sql_query(sql_str, engine)
    locations = np.array(df['location']).tolist()
    if id =='igao':
        ren = {'msg':locations, 'msg_code':200 }
    else:
        ren = {'msg':'error','msg_code':400}
    return json.dumps(ren, ensure_ascii=False)

if __name__ == '__main__':
    api.run(port=8800, debug=True, host='127.0.0.1')  # 启动服务
    # debug=True,改了代码后，不用重启，它会自动重启
    # 'host='127.0.0.1'别IP访问地址