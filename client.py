import requests
from bs4 import BeautifulSoup
import time
import sys
import traceback

# def Beijing_time():
#     r=requests.get('https://www.baidu.com')
#     t=time.strptime(r.headers['date'],'%a, %d %b %Y %H:%M:%S GMT')
#     return time.mktime(t)+28800

# if(Beijing_time()-1680500272>=86400*2):
#     input("测试期已过，请联系作者。")
#     sys.exit()

headers='''
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: no-cache
Connection: keep-alive
Cookie: %s
Host: 172.26.57.60
Pragma: no-cache
Referer: http://172.26.57.60/rsdagl/rsdagl/stdagl/action/StdaglAction.do?method=dackCx
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Core/1.94.197.400 QQBrowser/11.6.5265.400
'''
#headers转换
def trans(s):
    d = dict()
    s = s.split("\n")
    for i in s:
        if(i == ''):
            continue
        if(i[0] == ":"):
            i = i[1:]
        d[i.split(': ')[0]] = i.split(': ')[1]
    return d


url="http://172.26.57.60/rsdagl/rsdagl/stdagl/action/StdaglAction.do?method=dackCx"
if __name__ == "__main__":
    cookie=input("输入cookie:")
    headers=trans(headers%cookie)
    while(1):
        time.sleep(5)
        try:
            r=requests.get(url,headers=headers)
            soup = BeautifulSoup(r.text, 'lxml')
            # with open("StdaglAction.html",'r',encoding="utf-8") as f:
            #     r=f.read()
            # soup = BeautifulSoup(r, 'lxml')
            all_tr=soup.select('table')[-2].select('tr')[1:-2]
            tr_list=list()
        except:
            print("获取数据失败")
            traceback.print_exc()
            continue
        fileidList=list()
        for tr in all_tr:
            d=dict()
            d['name']=tr.select('td')[2].text
            d["fileid"]=tr.select('td')[3].text
            if(d["fileid"] in fileidList):
                continue
            d["time"]=tr.select('td')[8].text
            d["operator"]=tr.select('td')[9].text
            d["status"]=tr.select('td')[10].text
            tr_list.append(d)
            fileidList.append(d["fileid"])
        print(tr_list)
        try:
            r=requests.post("http://doctor10th.cn:1024/postList",json=tr_list)
        except:
            print("连接服务器失败")
            traceback.print_exc()
        