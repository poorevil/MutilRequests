# -*- coding:utf-8 -*-
'''
Created on 2013-3-17

@author: poorevil
'''

import MySQLdb

import utils

from Model import PicModel

class PicDetailDao(object):
    '''
    PicDetail dao
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.con = MySQLdb.connect(host='127.0.0.1', user='root', passwd='',db='lifepictorial',port=3306, charset="utf8")  
        pass
    
    def getPicDetailByAmount(self,limit,offset):
        '''
        根据需要获取的数量，按时间倒叙查询
        '''
        cur = self.con.cursor()
        cur.execute('''select pid,pic_path,height,width,desc,cate_id,root_cate_id,
                        albunm_name,albunm_id,user_id,time,taoke_num_iid,taoke_title,taoke_price from pic_detail 
                        order by time desc limit %d offset %d'''%(limit,offset))
        
        results = []
        
        for row in cur:            
            picModel = PicModel.PicModel()
            picModel.initPropertyByCur(row)
            
            results.append(picModel)
            
        cur.close()
        
        return results
        
    def insertPicDetail(self,picDetailModel):
        
        cur = self.con.cursor()
        try:
            
            sql = '''INSERT INTO admin_picdetail 
            (`pid`, `pic_path`, `height`, `width`, `pic_desc`, `categoary_id`, `albunm_name`, `albunm_id`, `user_id`, 
            `time`, `taoke_num_iid`, `taoke_title`, `taoke_price`) 
            VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')'''%(picDetailModel.pId
            ,picDetailModel.picPath
            ,picDetailModel.height
            ,picDetailModel.width
            ,picDetailModel.desc
            ,picDetailModel.cateId
            ,picDetailModel.albunmName
            ,picDetailModel.albunmId
            ,picDetailModel.userId
            ,picDetailModel.time
            ,picDetailModel.taokeNumIID
            ,picDetailModel.title
            ,picDetailModel.price)
            
            sql = utils.unescape(sql).encode('utf-8')
            
            cur.execute(sql)

            self.con.commit()
        except Exception,what:
            print '========-------=======',what
#            print sql
            pass
        
        cur.close()
        
        
    def getAlbunmIdByContentsMinAmount(self,minAmount):
        '''
        根据图集中内容的多少倒叙排列查询图集id
        minAmount:图集中图片数量不得少于minAmount的数量
        '''
        cur = self.con.cursor()
        
        cur.execute('''SELECT albunm_id ,albunm_name, count(*) as amount FROM pic_detail group by albunm_id having count(*) > %d 
                        order by count(*) desc'''%minAmount)
        
        result = cur.fetchall()

        cur.close()
        
        return result
    
    def getPicDetailByAlbunmId(self,albunmId,limit,offset):
        '''
        根据albunmId、需要获取的数量，按时间倒叙查询
        '''
        cur = self.con.cursor()
        cur.execute('''select pid,pic_path,height,width,desc,cate_id,root_cate_id,
                        albunm_name,albunm_id,user_id,time,taoke_num_iid,taoke_title,taoke_price from pic_detail 
                        where albunm_id = '%s' 
                        order by time desc limit %d offset %d'''%(albunmId,limit,offset))
        
        results = []
        
        for row in cur:            
            picModel = PicModel.PicModel()
            picModel.initPropertyByCur(row)
            
            results.append(picModel)
            
        cur.close()
        
        return results
    
    def getAllPicDetail(self):
        '''
        获取所有数据，用于dump
        '''
        cur = self.con.cursor()
        cur.execute('''select pid,pic_path,height,width,desc,cate_id,root_cate_id,
                        albunm_name,albunm_id,user_id,time,taoke_num_iid,taoke_title,taoke_price from pic_detail ''')
        
        results = cur.fetchall()
        
        return results
        
    def __del__(self):
        self.con.close()
        
    