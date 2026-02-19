from __future__ import annotations
import os
import io
import random
import logging
import hashlib
import datetime
import base64
from urllib.parse import urlencode

from .cooperation import muyangren907_shoot_time
from .Requests import Requests


def getAllItemsBySinglePageFunction(SinglePageFunc, max=-1):
    """
    Helper function to get all items using a single-page function.
    
    Args:
        SinglePageFunc: Function that takes cursor and returns dict with 'items', 'has_more', 'cursor'
        max: Maximum number of items to retrieve (-1 for all)
    
    Returns:
        List of all items
    """
    cursor = None
    r = []
    while True:
        page = SinglePageFunc(cursor=cursor)
        r += page["items"]
        if page["has_more"]:
            cursor = page["cursor"]
            if max > 0:
                if len(r) >= max:
                    break
        else:
            break
    if max <= 0:
        return r
    else:
        return r[:max]



















class General:
    def __init__(self, req:Requests):
        self.req = req

    @staticmethod
    def get_file_fullContent(filePath):
        with open(filePath, "rb") as f:
            binString = f.read()
            md5 = hashlib.md5(binString).hexdigest()

        return {
            "fileName": os.path.basename(filePath),
            "localFilePath": filePath,
            "size": os.path.getsize(filePath),
            "ctime": int(os.path.getctime(filePath)),
            "mtime": int(os.path.getmtime(filePath)),
            "md5": md5,
            "bin": binString,
            "media_info": muyangren907_shoot_time.getMediaInfo_interface(filePath),
        }

    def upload_step1_preCreate(self, fileFull):
        postdata = {
            "autoinit": "1",
            "block_list": '["{}"]'.format(fileFull["md5"]),
            "isdir": "0",
            "rtype": "1",
            "ctype": "11",  # required
            "path": "/" + fileFull["fileName"],  # required
            "size": fileFull["size"],  # required
            #   'slice-md5': '4fe8d73cf1ee838b...',
            "slice-md5": fileFull["md5"],
            "content-md5": fileFull["md5"],  # required
            "local_ctime": fileFull["ctime"],
            "local_mtime": fileFull["mtime"],
            # "shoot_time": fileFull["shoot_time"],
            # 'media_info': 'QD1xoOXfdIsFhss...' # 包含shoot_time
            "media_info": fileFull["media_info"],  # 包含shoot_time
        }
        params = {
            "clienttype": "70",
            #             'bdstoken': self.req.bdstoken, # requird
        }
        logging.debug("upload_step1,postData={}".format(postdata))
        data = self.req.postReqJson(
            url="https://photo.baidu.com/youai/file/v1/precreate",
            params=params,
            data=postdata,
        )
        # print('upload_step1_preCreate {}'.format(data))
        return data

    #         exist: {'data': {'fs_id': 9630...305088, 'size': 14...74, 'md5': '0379955f9bd...002f773217b', 'server_filename': 'Screen.png', 'path': '/youa/web/Screen.png', 'ctime': 16470..., 'mtime': 16470..., 'isdir': 0, 'category': 3, 'server_md5': '9af01bd...7bebeded', 'shoot_time': 1647...309}, 'return_type': 3, 'errno': 0, 'request_id': 48666...003049}
    #         New: {'return_type': 1, 'path': '/youa/web/Screen.png', 'uploadid': 'N1-MTAuNj...DA2MzY3OTQx', 'block_list': [0], 'errno': 0, 'request_id': 48669...67941}

    def upload_step2_superfile2(self, preCreateInfo, fileFull):
        params = dict(
            (
                ("method", "upload"),
                ("app_id", "16051585"),
                ("channel", "chunlei"),
                ("clienttype", "70"),
                ("web", "1"),
                #             ('logid', 'MTY.........'), # ? , changed every time
                ("path", "/" + fileFull["fileName"]),
                ("uploadid", preCreateInfo["uploadid"]),
                ("partseq", "0"),
            )
        )

        logging.debug("upload_step2,postParams={}".format(params))
        response = self.req.post(
            "https://c3.pcs.baidu.com/rest/2.0/pcs/superfile2",
            params=params,
            files={fileFull["fileName"]: io.BytesIO(fileFull["bin"])},
        )
        return response.json()

    def upload_step3_create(self, preCreateInfo, fileFull):
        params = dict(
            (
                ("clienttype", "70"),
                #             ('bdstoken', self.req.bdstoken),
            )
        )

        data = {
            "path": "/" + fileFull["fileName"],
            "size": fileFull["size"],
            "uploadid": preCreateInfo["uploadid"],
            "block_list": '["{}"]'.format(fileFull["md5"]),
            "isdir": "0",
            "rtype": "1",
            "content-md5": fileFull["md5"],
            "ctype": "11",
            "media_info": fileFull["media_info"]
            #           'media_info': 'QD1xoOX.....'
        }
        logging.debug("upload_step3,postData={}".format(data))
        return self.req.post(
            "https://photo.baidu.com/youai/file/v1/create", params=params, data=data
        ).json()

    def upload_1file(self, filePath):
        # get_file_fullContent,fileName,localFilePath,size,ctime,mtime,md5,bin
        fobj = self.get_file_fullContent(filePath)
        preC = self.upload_step1_preCreate(fobj)
        if preC.get("uploadid", None) is not None:
            reqJson1 = self.upload_step2_superfile2(preCreateInfo=preC, fileFull=fobj)
            reqJson2 = self.upload_step3_create(preCreateInfo=preC, fileFull=fobj)
            return preC, reqJson1, reqJson2
        else:
            pass
            # file exsis online, 確認網頁操作時也沒有重新上傳
            return preC, None, None

    def createNewAlbum(self, Name, tid=None):
        url = "https://photo.baidu.com/youai/album/v1/create"
        if tid is None:
            tid = str(random.randint(100000000000000000, 999999999999999999))
        params = {
            "title": Name,  #
            "source": "0",
            "tid": tid,  # tid 用来唯一标识，title相同的相册可以同时存在 exam=316511988232386428
        }
        res = self.req.getReqJson(url=url, params=params)
        return res

    @staticmethod
    def funcS(j, r):
        a = []
        p = []
        o = ""
        v = len(j)
        for q in range(256):
            a.append(ord(j[q % v]))
            p.append(q)
            q += 1
        u = 0
        for q in range(256):
            u = (u + p[q] + a[q]) % 256
            t = p[q]
            p[q] = p[u]
            p[u] = t
            q += 1
        i = u = q = 0
        for q in range(len(r)):
            i = (i + 1) % 256
            u = (u + p[i]) % 256
            t = p[i]
            p[i] = p[u]
            p[u] = t
            k = p[((p[i] + p[u]) % 256)]
            o += chr(ord(r[q]) ^ k)
            q += 1
        return o

    @classmethod
    def get_sign_by_sign1sign2sign3(cls, sign1, sign2, sign3):
        funcS = (
            cls.funcS
        )  # fun_s = js2py.eval_js(sign2); notice to import js2py and in requirements
        sign = base64.encodebytes(funcS(sign3, sign1).encode("latin1")).decode()
        return sign

    def batchDonwload_precondition(self):
        # bacth download 之前，此requrest能够得到几条信息（其中还有一个js函数），
        # 需要通过该函数返回的信息计算处sign用于真正的batchdownload，现在还不知道是如何转换的
        url = "https://photo.baidu.com/youai/file/v1/batchdownloadvariable"
        params = {"fields": '["sign1","sign2","sign3","timestamp"]', "clienttype": "70"}
        rdata = self.req.getReqJson(url=url, params=params)
        sign = self.get_sign_by_sign1sign2sign3(
            rdata["sign1"], rdata["sign2"], rdata["sign3"]
        )
        return {"sign": sign, "timestamp": rdata["timestamp"]}

    def getdlLink_batchDonwload(self, items, zipname=None):
        preData = self.batchDonwload_precondition()
        base_url = "https://photo.baidu.com/youai/file/v1/batchdownload"
        fsid_list = [str(i.get_fsid()) for i in items]
        if zipname is None:
            now = datetime.datetime.now()
            zipname = now.strftime("【一刻相册】%H时%M分-批量下载 {} 项.zip").format(len(fsid_list))
        
        # 限制每批最多 1000 张
        if len(fsid_list) > 1000:
            logging.warning(f"文件数量超过限制 {len(fsid_list)} > 1000，将只下载前 1000 张")
            fsid_list = fsid_list[:1000]
        
        # 输出调试信息
        logging.info(f"=== 批量下载 URL 生成逻辑 ===")
        logging.info(f"文件数量: {len(fsid_list)}")
        logging.info(f"ZIP 文件名: {zipname}")
        logging.info(f"前 5 个 fsid: {fsid_list[:5]}")
        logging.info(f"签名长度: {len(preData['sign'])}")
        logging.info(f"时间戳: {preData['timestamp']}")
        
        # 构造参数
        params = {
            "clienttype": "70",
            "fsid_list": "[{}]".format(",".join(fsid_list)),
            "zipname": zipname,
            "sign": preData["sign"],
            "timestamp": preData["timestamp"],
        }
        
        # 计算参数长度
        fsid_list_str = params["fsid_list"]
        params_str = urlencode(params)
        full_url = f"{base_url}?{params_str}"
        
        logging.info(f"fsid_list 参数长度: {len(fsid_list_str)} 字符")
        logging.info(f"完整 URL 长度: {len(full_url)} 字符")
        logging.info(f"完整 URL: {full_url}")
        
        resJson = self.req.getReqJson(url=base_url, params=params)
        
        # 检查返回结果
        if resJson.get("errno") != 0:
            logging.error(f"批量下载失败: errno={resJson.get('errno')}, msg={resJson}")
            raise Exception(f"批量下载失败: {resJson}")
        
        return resJson["dlink"]

    def getDownloadZip(self, items, dirPath, zipname=None):
        from .contribution import downLoader

        dl = downLoader(req=self.req)
        url = self.getdlLink_batchDonwload(items=items, zipname=zipname)
        dl.getDownloadZip(url=url, dirPath=dirPath, fileName=zipname)