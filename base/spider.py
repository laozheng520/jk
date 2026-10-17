class Spider:
    def init(self, extend=""):
        pass
    def destroy(self):
        pass
    def homeContent(self, filter):
        return {}
    def homeVideoContent(self):
        return {}
    def categoryContent(self, tid, pg, filter, extend):
        return {}
    def detailContent(self, ids):
        return {}
    def searchContent(self, key, quick, pg="1"):
        return {}
    def playerContent(self, flag, id, vipFlags):
        return {}
    def isVideoFormat(self, url):
        pass
    def manualVideoCheck(self):
        pass
    def localProxy(self, params):
        return None
