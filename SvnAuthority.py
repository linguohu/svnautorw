#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import sys
import base64

# python2 和 python3的兼容代码
try:
    # python2 中
    import cookielib

    print("user cookielib in python2.")
except:
    # python3 中
    import http.cookiejar as cookielib

    print("user cookielib in python3.")

# session代表某一次连接
svnSession = requests.session()
# 因为原始的session.cookies 没有save()方法，所以需要用到cookielib中的方法LWPCookieJar，这个类实例化的cookie对象，就可以直接调用save方法。
svnSession.cookies = cookielib.LWPCookieJar(filename="svnCookies.txt")

userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
header = {
    "Referer": "http://svn.com:8080/esvn/login.jsp",
    'User-Agent': userAgent,
}
pjauthDataRW = ({
                    "act": "save",
                    "check": "pojo",
                    "grs": "aa",
                    "newres": "[ECM_DEV:/aa/Trunk]",
                    "path": "/aa/Trunk",
                    "pj": "ECM_DEV",
                    "res": "[ECM_DEV:/]",
                    "rw": "rw"
                },
                {
                    "act": "save",
                    "check": "pojo",
                    "grs": "bb",
                    "newres": "[ECM_DEV:/ec-fc/Trunk]",
                    "path": "/ec-fc/Trunk",
                    "pj": "ECM_DEV",
                    "res": "[ECM_DEV:/]",
                    "rw": "rw"
                },
                
)
pjauthDataDel = ({
                     "act": "del",
                     "gr": "aa",
                     "pj": "ECM_DEV",
                     "delres": "[ECM_DEV:/aa/Trunk]",
                     "path": "/aa/Trunk",
                     "res": "[ECM_DEV:/]",
                     "usr": "+"
                 },
                 {
                     "act": "del",
                     "gr": "bb",
                     "pj": "ECM_DEV",
                     "delres": "[ECM_DEV:/ec-fc/Trunk]",
                     "path": "/ec-fc/Trunk",
                     "res": "[ECM_DEV:/]",
                     "usr": "+"
                 },
                 
)


# svn 登录
def svnLogin(account, password):
    print("开始登录svn")
    postUrl = "http://svn.com:8080/esvn/login"
    postData = {
        "usr": account,
        "psw": password,
    }
    # 使用session直接post请求
    responseRes = svnSession.post(postUrl, data=postData, headers=header)
    # 无论是否登录成功，状态码一般都是 statusCode = 200
    print("statusCode = %s" % (responseRes.status_code))
    print(responseRes.text)
    # 登录成功之后，将cookie保存在本地文件中，好处是，就不需要再走svnLogin的流程了，因为已经从文件中拿到cookie了
    svnSession.cookies.save()


# 
def rwSvn(postDate):
    routeUrl = "http://svn.com:8080/esvn/pjauth"
    header = {
        "Referer": "http://svn.com:8080/esvn/pjauth",
        'User-Agent': userAgent,
    }

    responseRes = svnSession.post(routeUrl, data=postDate, headers=header)
    print("statusCode = {responseRes.status_code}")

    if responseRes.status_code != 200:
        return False
    else:
        return True


def delSvn(postData):
    routeUrl = "http://svn.com:8080/esvn/pjauth"
    header = {
        "Referer": "http://svn.com:8080/esvn/pjauth",
        'User-Agent': userAgent,
    }
    responseRes = svnSession.post(routeUrl, data=postData, headers=header)
    print("statusCode = {responseRes.status_code}")
    if responseRes.status_code != 200:
        return False
    else:
        return True
if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("请传入rw(读写权限)或者remove(删除授权)参数")
        exit(1)
      #  第一步：登录，密码加密
    svnLogin("user", "pw")
    svnSession.cookies.load()
    if sys.argv[1] == "rw":
        for line in open("item.txt"):
            for saveItem in pjauthDataRW:
                #读取的行需要去除换行符后再比较
                if line.strip('\n') == saveItem['path'].split('/')[1]:
                    isSave = rwSvn(saveItem)
                    print("%s is save  = {isSave}" % (saveItem['grs']))
                    if isSave == False:
                        print("%s 保存失败..." % (saveItem['grs']))
    elif sys.argv[1] == "remove":

        for delItem in pjauthDataDel:
            isDelSvn = delSvn(delItem)
            print("%s is del svn = {isDelSvn}" % (delItem['gr']))
            if isDelSvn == False:
                print("%s 删除失败..." % (delItem['gr']))
