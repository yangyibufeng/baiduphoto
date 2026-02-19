import requests
import logging


"""

Requests 是python requests的一个简单包装，主要是用于统一cookies和请求参数的作用。
req.get() 相当于 requests.get()
req.getReqJson() 相当于 requests.get().json()
...


"""


class Requests:
    def __init__(self, cookies, proxies=None):
        self.cookies = cookies

        self.headers = {
            "Connection": "keep-alive",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
            "sec-ch-ua-platform": '"macOS"',
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://photo.baidu.com/photo/web/home",
            "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7",
        }

        self.proxies = proxies
        #
        self.bdstoken = None

    def get_proxies(self):
        if self.proxies is None:
            r = {}
        else:
            r = dict(self.proxies)
        # print(type(r),r)
        return r

    def get_bdstoken(self):
        url = "https://photo.baidu.com/photo/web/home"
        response = requests.get(
            url, proxies=self.get_proxies(), cookies=self.cookies, headers=self.headers
        )
        d = None
        for l in response.text.split("\n"):
            if "templateData" in l:
                d = l
                break
        if d is None:
            logging.error("can not get bdstoken")
            return
        return (
            l.split("=")[1]
            .split(";")[0]
            .split(",")[0]
            .split(":")[1]
            .replace("'", "")
            .strip()
        )

    def get_bdstoken_Cache(self):
        if self.bdstoken is None:
            self.bdstoken = self.get_bdstoken()
        return self.bdstoken

    def get(self, url, **kwargs):
        if "params" in kwargs:
            kwargs["params"]["bdstoken"] = self.get_bdstoken_Cache()
        else:
            kwargs["params"] = {"bdstoken": self.get_bdstoken_Cache()}
        req = requests.get(
            url=url,
            proxies=self.get_proxies(),
            cookies=self.cookies,
            headers=self.headers,
            **kwargs
        )
        return req

    def post(self, url, **kwargs):
        if "params" in kwargs:
            kwargs["params"]["bdstoken"] = self.get_bdstoken_Cache()
        else:
            kwargs["params"] = {"bdstoken": self.get_bdstoken_Cache()}
        req = requests.post(
            url=url,
            proxies=self.get_proxies(),
            cookies=self.cookies,
            headers=self.headers,
            **kwargs
        )
        return req

    def getReqJson(self, url, **kwargs):
        response = self.get(url, **kwargs)
        try:
            data = response.json()
        except Exception as e:
            logging.error(f"JSON 解析失败: {e}")
            logging.error(f"响应状态码: {response.status_code}")
            logging.error(f"响应内容: {response.text[:500]}")
            raise Exception(f"API 返回的不是有效的 JSON 格式: {response.text[:200]}")
        
        if data["errno"] == 0:
            return data
        else:
            logging.error("request return error, return = {}".format(data))
            return data

    def postReqJson(self, url, **kwargs):
        response = self.post(url, **kwargs)
        try:
            data = response.json()
        except Exception as e:
            logging.error(f"JSON 解析失败: {e}")
            logging.error(f"响应状态码: {response.status_code}")
            logging.error(f"响应内容: {response.text[:500]}")
            raise Exception(f"API 返回的不是有效的 JSON 格式: {response.text[:200]}")
        
        if data["errno"] == 0:
            return data
        else:
            logging.error("request return error, return = {}".format(data))
            return data