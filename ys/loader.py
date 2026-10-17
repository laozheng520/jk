# -*- coding: utf-8 -*-
from base.spider import Spider
import json as _j

_q = ["a974149b", "963d21dd", "a4164bcd", "aebd5d8ce362dcb1", "fc434aad", "d1d378a2", "4b4b288c", "ac9c8a6d", "a81b5ebe24d9556d", "d3b56c4af64119e6", "f7d43198"]
_w = [76, 146, 205, 255, 154, 233, 13, 118, 20, 48, 105]
_m = [4, 7, 1, -1, 0, 5, 3, 2, -1, -1, 6]
_f = [0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0]
_v = ".py"

def _g():
    r = [None] * 8
    for a, b, c, d in zip(_q, _w, _m, _f):
        if c < 0:
            continue
        if d:
            r[c] = bytes((int(a[i:i + 2], 16) - b) & 0xFF for i in range(0, len(a), 2))
        else:
            r[c] = bytes(int(a[i:i + 2], 16) ^ b for i in range(0, len(a), 2))
    return b"".join(r)

def _h():
    s = 0
    for a, b, c, d in zip(_q, _w, _m, _f):
        if c >= 0:
            continue
        if d:
            s = (s + sum((int(a[i:i + 2], 16) - b) & 0xFF
                         for i in range(0, len(a), 2))) & 0xFFFF
        else:
            s = (s + sum(int(a[i:i + 2], 16) ^ b
                         for i in range(0, len(a), 2))) & 0xFFFF
    return s

class Spider(Spider):
    def init(self, extend=""):
        c = _j.loads(extend) if extend else {}
        self._site = c.get("site", "")
        self._base = c.get("base", "").rstrip("/")
        self._name = c.get("name", "")
        self._tag = _h()
        self._real = None

    def _load(self):
        if self._real is not None:
            return self._real
        import requests, base64
        from Crypto.Cipher import AES
        s = requests.Session()
        s.headers.update({"User-Agent": "okhttp/3.12.0"})
        r = s.get(self._base + "/" + self._site + _v, timeout=20)
        if r.status_code != 200:
            raise Exception("加载失败")
        d = base64.b64decode(r.content.strip())
        iv, ct = d[:16], d[16:]
        p = AES.new(_g(), AES.MODE_CBC, iv).decrypt(ct)
        code = p[:-p[-1]].decode("utf-8")
        ns = {}
        exec(compile(code, "<s>", "exec"), ns)
        real = ns["Spider"]()
        real.init("")
        self._real = real
        return real

    def getName(self):
        return self._name or self._load().getName()

    def destroy(self):
        if self._real is not None:
            try: self._real.destroy()
            except Exception: pass

    def homeContent(self, filter):
        return self._load().homeContent(filter)
    def homeVideoContent(self):
        return self._load().homeVideoContent()
    def categoryContent(self, tid, pg, filter, extend):
        return self._load().categoryContent(tid, pg, filter, extend)
    def detailContent(self, ids):
        return self._load().detailContent(ids)
    def searchContent(self, key, quick, pg="1"):
        return self._load().searchContent(key, quick, pg)
    def playerContent(self, flag, id, vipFlags):
        return self._load().playerContent(flag, id, vipFlags)
    def isVideoFormat(self, url):
        try: return self._load().isVideoFormat(url)
        except Exception: return False
    def manualVideoCheck(self):
        try: return self._load().manualVideoCheck()
        except Exception: return False
    def localProxy(self, param):
        try: return self._load().localProxy(param)
        except Exception: return None
