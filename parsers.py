#coding=utf-8
import urllib
import os
from datetime import datetime
from sgmllib import SGMLParser

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

# It is useless to re-define feed again.
#    def feed(self, data):
#        SGMLParser.feed(self, data)

        
        
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
            
            if len(self.aItem) < 5:
                return
            elif len(self.aItem) > 5:
                itemTitle = ' '.join(self.aItem[:-4])
                self.aItem = [itemTitle] + self.aItem[-4:]
            
            self.itemList.append(self.aItem)
            self.aItem = []
            
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
#		print 'text is: ' + text ##有用的文本
    
    def printItems(self, isSimplePrint = True):
        for item in self.itemList:
                #only print title and date
                if isSimplePrint:
                        print item[0]
                        print item[1]
                else:
                        for i in item:
                                print i
    
    def GetItemList(self):
       return self.itemList
    
    def CleanItemList(self):
        del self.itemList[:]
    
 #TODO: smzdmParser <-- Will implement it
class smzdmParser(SGMLParser):
    pass
