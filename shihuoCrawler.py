#coding=utf-8
import requests
import threading
import urllib
import time
import copy
from parsers import shihuoParser, smzdmParser
from datetime import datetime

class bargainCrawler():

    def __init__(self, site):
        self.site = site.lower()

        self.page_content = ""
        self.myParser = self.SetParser(self.site)
        
        self.storedItemList = []
        self.itemTimeRecorder = datetime.min

    def FetchCurrentItems(self, buyWhat, startPage=1, pagesNum=10, days=7):
            for i in range(startPage,startPage + pagesNum):
                self.CrawlOnePage(buyWhat, i)
                isOutdated = self.ParseOnePage(days)
                if isOutdated:
                    return isOutdated
            
            return isOutdated

        

    def CrawlOnePage(self, buyWhat, page=1 ):
        ##'''http://www.shihuo.cn/1?w=篮球鞋'''
        if page <= 0:
            page = 1
        #urllib.quote: translate Chinese characters into coded characters
        #pageurl = 'http://www.shihuo.cn'
        if self.site =='shihuo':
            self.pageurl = 'http://www.shihuo.cn/' + unicode(page) + '?w=' + urllib.quote(buyWhat)
        elif self.site == 'smzdm':
            self.pageurl = 'http://www.smzdm.com/' + unicode(page) + '?w=' + urllib.quote(buyWhat)
        else:
            self.pageurl = ""

        rh = requests.get(self.pageurl)

        if rh.status_code == requests.codes.ok:
            #替换HTML中的单引号字符（转移字符是&#039） 和双引号字符（&quot）, 避免在parse的时候出错
#            #TODO: improve these ugly lines below
            self.page_content = rh.content  ##返回raw的网页编码
#            self.page_content = rh.content.replace(r'&#039',"'") ##返回raw的网页编码
#            self.page_content = self.page_content.replace(r'&quot;','"') ##返回raw的网页编码
        #return rh.content  ##返回raw的网页编码
#            self.page_content = rh.text
#            return rh.text ##会对原始网页代码的编码进行猜测
    
    def SetParser(self, site):
        if site == "shihuo":
            return shihuoParser()
        else: 
            return smzdmParser() 
            
    def GetParser(self):
        return self.myParser
    
    #Parse the content of a crawled page.
    def ParseOnePage(self, limitDays = 7):
        self.myParser.feed(self.page_content)
        isItemRemoved = self.KeepItemRecent(limitDays)
#        self.PrintItemList(isSimplePrint = False)
        
        return isItemRemoved

    def PrintItemList(self,isSimplePrint = True):
        self.myParser.printItems(isSimplePrint)

    def UpdateStoredItemList(self):
        itemList = self.myParser.GetItemList()
        self.storedItemList = self.storedItemList + copy.deepcopy(itemList)
    
    def UpdateItemTimeRecorder(self):
        try:
            itemTime = datetime.strptime(self.myParser.GetItemList()[0][-3],'%m月%d日 %H:%M')
        except IndexError:
            return
        except:
            return False
        self.itemTimeRecorder = itemTime


    # TODO: IsItemCollected未引入“年”可能导致一种逻辑Bug：
    #      TimeRecorder日期是12月31日（2014年），newItem的日期是1月1日（2015），
    #      则原本是fresh的这个newItem不会被收录
    #
    #解决此问题：
    #1. 解决思路： 
    #   对收录到的item的时间项进行加“年”的修正
    #
    #2. itemList中的item遵守的时间准则:
    #   排在前边的item的收录时间一定晚于（或等于）排在后边的item的收录时间
    #    
    #3. 需要考虑的问题：
    #   a. 新年伊始，Crawl的第一个项目是去年的（如何记录？）
    #   b. 新年伊始，Crawl的中间某个项目或最后一个项目是去年的，之后的项目是今年的（）
    #
    #若已完成了这里，成员函数KeepRecentItemOnly中的itemDate变量的赋值一行也要修改
    #
    #IsItemUncollected: Return True if the newItem has not been collected
    def IsItemUncollected(self, newItemTime, timeRecorder):
        if newItemTime > timeRecorder:
            return True
        else:
            return False
            
    #由于商品具有时效性，因此只保留最近days天以来发布的商品
    #Return: True if some items in itemList should be removed. False if not.
    def KeepItemRecent(self, limitDays = 7):
        isRemoved = False
        nowDate = datetime.today()
        itemList = self.myParser.GetItemList()
        reverseItemIndexs = range(len(self.myParser.GetItemList()))[::-1]
        for i in reverseItemIndexs:
            item = itemList[i]
            #itemDate只有月和日的数据,需要修正itemDate的年数据
            itemDate = datetime.strptime(str(nowDate.year) + '年' + item[2], '%Y年%m月%d日 %H:%M')
            if (nowDate - itemDate).days > limitDays:
                del itemList[i] #??am I writting right?
                isRemoved = True
            else:
                return isRemoved

        return isRemoved
    
    
    #KeepItemUncollected: Only keep the uncollected items in the itemList.
    def KeepItemUncollected(self):
        itemList = self.myParser.GetItemList()
        reverseItemIndexs = range(len(self.myParser.GetItemList()))[::-1]
        for i in reverseItemIndexs:
            item = itemList[i]
            itemDate = datetime.strptime(item[2], '%m月%d日 %H:%M')
            if self.IsItemUncollected(itemDate, self.itemTimeRecorder):
                return
            else:
                del itemList[i]
            

    def DownloadItemPic(self, itemList):
        filedir = 'temppics'
        if not os.path.exists(filedir):
            os.mkdir(filedir)
        
        for item in itemList:
#输出itemList信息用于测试
            print 'item len:' + str(len(item))
            for i in item:
                print i
            pic_url = item[-1]
            filename = pic_url.split('/')[-1]
            temppath = filedir + '/'+ filename
            
            urllib.urlretrieve(pic_url, temppath)

#def RunCrawler():
#	pass

if __name__ == '__main__':
    crawlInterval = 5 
    buyWhat = '篮球鞋'
    my_shihuoCrawler = bargainCrawler("shihuo")

#    my_shihuoCrawler.CrawlOnePage(buyWhat, 4)
#    my_shihuoCrawler.ParseOnePage()
    my_shihuoCrawler.FetchCurrentItems(buyWhat, startPage=1, pagesNum=10, days=7)
    my_shihuoCrawler.UpdateStoredItemList()
    my_shihuoCrawler.UpdateItemTimeRecorder()
    my_shihuoCrawler.PrintItemList()
    my_shihuoCrawler.GetParser().CleanItemList()

    while True:
        my_shihuoCrawler.CrawlOnePage(buyWhat, 1)
        my_shihuoCrawler.ParseOnePage()
        my_shihuoCrawler.KeepItemUncollected()
        my_shihuoCrawler.UpdateStoredItemList()
        my_shihuoCrawler.UpdateItemTimeRecorder()
        my_shihuoCrawler.PrintItemList()
        my_shihuoCrawler.GetParser().CleanItemList()
	    #my_shihuoParser.DownloadItemPic()
        time.sleep(crawlInterval)
