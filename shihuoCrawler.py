#coding=utf-8
import requests
from sgmllib import SGMLParser
import urllib
import os

def CrawlOnePage(page, buyWhat):
    ##'''http://www.shihuo.cn/1?w=篮球鞋'''
    if page <= 0:
        page = 1
    #urllib.quote: translate Chinese characters into coded characters
    #pageurl = 'http://www.shihuo.cn'
    pageurl = 'http://www.shihuo.cn/' + unicode(page) + '?w=' + urllib.quote(buyWhat)
#    print pageurl

    rh = requests.get(pageurl)

    if rh.status_code == requests.codes.ok:
        return rh.content  ##返回raw的网页编码
        ##rh.text ##会对原始网页代码的编码进行猜测

class shihuoParser(SGMLParser):
    def reset(self):
            #itemList: 
            self.itemList = []
            self.aItem = []
            self.in_body_flag = False
            self.index_item_flag = False
            self.item_hd_flag = False
            self.in_h2_flag = False
            self.in_a_flag = False
            self.shihuo_buy_link_flag = False
            self.in_p_pic_flag = False
            self.in_p_pic_a_flag = False
            self.in_img_flag = False
            self.getdata = False
            self.verbatim = 0
            self.sub_div = 0
            SGMLParser.reset(self)
                                
#    def start_body(self, attrs):
#        if self.in_body_flag == True:
#                self.verbatim +=1 ##进入子层body了，层数加1
#            return
#        self.in_body_flag = True
#        return
#
#    def end_body(self):##遇到</div>
#        if self.verbatim == 0:
#            self.in_body_flag = False
#            return
#        if self.in_body_flag == True:
#            self.verbatim -=1
#            return

    def start_div(self, attrs):

        for k,v in attrs:##遍历div的所有属性以及其值
            if k == 'class' and 'shihuo-index-item' in v and v!="shihuo-index-item-text" :
                ##确定进入了<div class='shiuho-index-item  '>, 注意值最后的2个空格
                self.index_item_flag = True
                #print 'into div class="shihuo-index-item "'
                return
            
            if self.index_item_flag == True and k == 'class' and v == 'item-hd':
                self.item_hd_flag = True
                return
            
            if self.index_item_flag == True and k == 'class' and v == 'shihuo-buy-link':
                self.shihuo_buy_link_flag = True
                return
            
        if self.index_item_flag == True:
            self.sub_div += 1
            return

            #if k == 'class' and v == ''
    
    def end_div(self):
        #There is no <div>s embeded in this flag, so just assign it with false
        if self.item_hd_flag == True:
            self.item_hd_flag = False
            return
        
        #There is no <div>s embeded in this flag, so just assign it with false
        if self.shihuo_buy_link_flag == True:
            self.shihuo_buy_link_flag = False
            return
                        
        if self.sub_div ==0 and self.item_hd_flag == False:
            self.index_item_flag = False
#            print 'out from div class="shihuo-index-item "'

            """
            now we are out from div class="shihuo-index-item "
            so now we add the complete item to itemList
            """
            
            #do not append it if there is no item.
            if len(self.aItem) == 0:
                return
            
            self.itemList.append(self.aItem)
            #now we reset the aItem for the next one.
            self.aItem = []
            return
            
        if self.index_item_flag == True:
            self.sub_div -=1
            return
            
    def start_h2(self,attrs):
        if self.item_hd_flag == False:
            return
        self.in_h2_flag = True
    def end_h2(self):
        if self.in_h2_flag:
            self.in_h2_flag = False
            
#    def start_a(self, attrs):
#        if self.in_h2_flag:
#            self.in_h2_a_flag = True
#        elif self.in_p_pic_flag:
#            self.in_p_pic_a_flag = True
#            for k, v in attrs:
#                if k == 'href':
#                    #here v is the buy link!!!
#                    print v
#        else: return
#        
#    def end_a(self):
#        if self.in_a_flag:
#            self.in_a_flag = False
#        elif self.in_p_pic_a_flag:
#            self.in_p_pic_a_flag = False

    def start_p(self, attrs):
        ##make sure we are in shihuo-buy-link ( of shihuo-index-item )
        if self.shihuo_buy_link_flag == False:
            return
        
        for k,v in attrs:##遍历p的所有属性以及其值
            if k == 'class' and v == 'pic' :
                ##确定进入了<p class='pic'>
                self.in_p_pic_flag = True
                #print 'into div class="shihuo-index-item "'
                return
    
    def end_p(self):
        if self.in_p_pic_flag:
            self.in_p_pic_flag = False
    
    ##注意上面也有一个start_a函数
    def start_a(self, attrs):
        if self.in_p_pic_flag == False:
            return
        self.in_p_pic_a_flag = True
        for k, v in attrs:
            if k == 'href':
                #here v is the buy link!!!
                self.aItem.append(v)
                #print v
    
    def end_a(self):
        if self.in_p_pic_a_flag:
            self.in_p_pic_a_flag = False
    
    def start_img(self, attrs):
        if self.in_p_pic_a_flag == False:
            return
        self.in_img_flag = True
        for k, v in attrs:
            if k == 'src':
                #here v is the item's picture                
                self.aItem.append(v)
                #print v
                #This is the last element in a item
    
    def end_img(self):
        if self.in_img_flag:
            self.in_img_flag = False
    
    def handle_data(self, text):##处理文本
#        if self.in_a_flag:
        if self.in_h2_flag:
            if not text.strip() == '':
                self.aItem.append(text)
#                print text ##有用的文本
    
    def printID(self):
        for i in self.itemList:
            print i
    
    def DownloadItemPic(self):
        filedir = 'temppics'
        if not os.path.exists(filedir):
            os.mkdir(filedir)
        
        for item in self.itemList:
##输出itemList信息用于测试
#            print 'item len:' + str(len(item))
#            for i in item:
#                print i
            pic_url = item[-1]
            filename = pic_url.split('/')[-1]
            temppath = filedir + '/'+ filename
            
            urllib.urlretrieve(pic_url, temppath)
            

if __name__ == '__main__':
    page_content = CrawlOnePage(1,'篮球鞋')
    #print page_content
    my_shihuoParser = shihuoParser()
    my_shihuoParser.feed(page_content)
#    my_shihuoParser.printID()
    my_shihuoParser.DownloadItemPic()
