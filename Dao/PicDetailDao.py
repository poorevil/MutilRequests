# -*- coding:utf-8 -*-
'''
Created on 2013-3-17

@author: poorevil
'''

import sqlite3

from Model import PicModel

class PicDetailDao(object):
    '''
    PicDetail dao
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.con = sqlite3.connect('pic_detail_db.db3')
        self.con.row_factory = sqlite3.Row              # sqlite3.Row
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
            cur.execute('''INSERT INTO pic_detail ("pid","pic_path","height","width","desc","cate_id","root_cate_id","albunm_name","albunm_id","user_id","time","taoke_num_iid","taoke_title","taoke_price") 
                            VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')'''%(picDetailModel.pId
                                                                                    ,picDetailModel.picPath
                                                                                    ,picDetailModel.height
                                                                                    ,picDetailModel.width
                                                                                    ,picDetailModel.desc
                                                                                    ,picDetailModel.cateId
                                                                                    ,picDetailModel.rootCateId
                                                                                    ,picDetailModel.albunmName
                                                                                    ,picDetailModel.albunmId
                                                                                    ,picDetailModel.userId
                                                                                    ,picDetailModel.time
                                                                                    ,picDetailModel.taokeNumIID
                                                                                    ,picDetailModel.title
                                                                                    ,picDetailModel.price))
        
            self.con.commit()
        except:
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
        
    