# -*- coding:utf-8 -*-

'''
Created on 2013-3-15

@author: poorevil
'''

from json import JSONEncoder

class PicModel(JSONEncoder):
    '''
    图片Model
    '''
    def __init__(self,pId=None,picPath=None,height=0,width=0,desc=None,cateId=0,rootCateId=0
                 ,albunmName=None,albunmId=None,userId=None,time=None
                 ,taokeNumIID=None,price=None,title=None):
        self.pId = pId                              #图片id
        self.picPath = picPath                      #图片地址
#        self.detailLink = detailLink                #详细页面地址
        self.height = height                        #高
        self.width = width                          #宽
        self.desc = desc                            #图片描述
        self.cateId = cateId                        #所属目录id
        self.rootCateId = rootCateId                #所属根目录id
        self.albunmName = albunmName                #所属图集名称
        self.albunmId = albunmId                    #所属图集id
        self.userId = userId                        #上传用户id
        self.time = time                            #上传时间
        self.taokeNumIID = taokeNumIID              #淘宝宝贝id
        self.price = price                          #价格
        self.title = title                          #淘宝宝贝名称
    
    
    def initPropertyByCur(self,cur):
        
        self.pId = cur['pId']
        self.picPath = cur['pic_path']                      #图片地址
        self.height = cur['height']                         #高
        self.width = cur['width']                           #宽
        self.desc = cur['desc']                             #图片描述
        self.cateId = cur['cate_id']                         #所属目录id
        self.rootCateId = cur['root_cate_id']                 #所属根目录id
        self.albunmName = cur['albunm_name']                 #所属图集名称
        self.albunmId = cur['albunm_id']                     #所属图集id
        self.userId = cur['user_id']                         #上传用户id
        self.time = cur['time']                             #上传时间
        self.taokeNumIID = cur['taoke_num_iid']               #淘宝宝贝id
        self.price = cur['taoke_price']                           #价格
        self.title = cur['taoke_title']                           #淘宝宝贝名称
    
     
    @staticmethod
    def serialize(obj):
        return {
            "pId":   obj.pId,
            "picPath": obj.picPath,
            "height": obj.height,
            "width": obj.width,
            "desc": obj.desc,
            "cateId": obj.cateId,
            "rootCateId": obj.rootCateId,
            "albunmName": obj.albunmName,
            "albunmId": obj.albunmId,
            "userId": obj.userId,
            "time": obj.time,
            "taokeNumIID": obj.taokeNumIID,
            "price": obj.price,
            "title": obj.title
        }