# _*_coding:utf-8_*_


import re
import logging
from .dbtools import DatabaseAgent
from job.models.industrial import Industrial


MSG_MAP = {
    200: 'success',
    401: '未提供认证信息',
    402: '认证信息过期，请重新登录',
    403: '错误的认证信息',
    404: '请求内容不存在',
    405: '不允许的操作',
    410: '用户名已存在',
    421: '用户名或密码错误',
    422: '请求缺少必要参数',
    500: '请求错误，请联系管理员',
    501: 'JSON格式错误',
    10000: '目录名已存在',
    10001: '文件传输错误'
}


#信息是否已经存在
def is_exits(title,url):
    db_agent = DatabaseAgent()
    url_exits = db_agent.get(
        orm_model=Industrial,
        filter_kwargs={"url": url}
    )
    if url_exits:
        logging.info("-----------already exits------------")
        return False
    title_exits = db_agent.get(
        orm_model=Industrial,
        filter_kwargs={"title": title}
    )
    if title_exits:
        logging.info("-----------already exits------------")
        return False
    return True


# 过滤html标签
def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    # s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)#替换实体
    return s


##替换常用HTML字符实体.
# 使用正常的字符替换HTML中特殊的字符实体.
# 你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
# @param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                     'lt': '<', '60': '<',
                     'gt': '>', '62': '>',
                     'amp': '&', '38': '&',
                     'quot': '"', '34': '"', }

    re_charEntity = re.compile(r'&#?(?P<name>\w+);')
    sz = re_charEntity.search(htmlstr)
    while sz:
        entity = sz.group()  # entity全称，如&gt;
        key = sz.group('name')  # 去除&;后entity,如&gt;为gt
        try:
            htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
            sz = re_charEntity.search(htmlstr)
        except KeyError:
            # 以空串代替
            htmlstr = re_charEntity.sub('', htmlstr, 1)
            sz = re_charEntity.search(htmlstr)
    return htmlstr



# 最大数
def Get_Max(list):
    return max(list)


# 最小数
def Get_Min(list):
    return min(list)


# 极差
def Get_Range(list):
    return max(list) - min(list)


# 中位数
def Get_Median(data):
    data = sorted(data)
    size = len(data)
    if size % 2 == 0:  # 判断列表长度为偶数
        median = (data[size // 2] + data[size // 2 - 1]) / 2
    if size % 2 == 1:  # 判断列表长度为奇数
        median = data[(size - 1) // 2]
    return median


# 众数(返回多个众数的平均值)
def Get_Most(list):
    most = []
    item_num = dict((item, list.count(item)) for item in list)
    for k, v in item_num.items():
        if v == max(item_num.values()):
            most.append(k)
    return sum(most) / len(most)


# 获取平均数
def Get_Average(list):
    sum = 0
    for item in list:
        sum += item
    return sum / len(list)


# 获取方差
def Get_Variance(list):
    sum = 0
    average = Get_Average(list)
    for item in list:
        sum += (item - average) ** 2
    return sum / len(list)


# 验证请求是否完整
def params_inact(post_data, *args):
    if not isinstance(post_data, dict):
        return False
    for arg in args:
        if arg not in post_data.keys():
            print("miss {} filed ".format(arg))
            return False
    return True


# 统一格式返回
def to_json(code, data=None):
    return jsonify({
        "code": code,
        "msg": MSG_MAP[code],
        "data": data
    })

