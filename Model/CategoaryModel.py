'''
Created on 2013-3-15

@author: poorevil
'''

class CategoaryModel(object):
    
    '''
    目录model
    '''
    
    def __init__(self,cId,title,parentCId=0):
        self.cId = cId                              #目录id
        self.title = title                          #标题
        self.parentCId = parentCId                  #父类目id