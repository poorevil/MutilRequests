# -*- coding:utf-8 -*-
import requests

from time import sleep
from threading import Thread

#from lxml import etree

from Model import PicModel
from Dao.PicDetailDao_mysql import PicDetailDao

import json , re , htmlentitydefs , urllib , time
 
UPDATE_INTERVAL = 0.01

THREAD_START_DELAY = 1

#LOG_FILE_PATH = 'message-%d.log'%(time.time())


class URLThread(Thread):
    def __init__(self, url, cid,rootCid,timeout=10, allow_redirects=True):
        super(URLThread, self).__init__()
        self.url = url
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.response = None
        self.cid = cid
        self.rootCid = rootCid
 
    def getPicWaterFlow(self):
        '''
        抓取瀑布流列表
        返回最初的瀑布流图片加描述
        
        {
            "code": 0,
            "data": {
                "data": [
                    {
                        "type": 1,                        //type=1 : 有title   type=2 : 没有title
                        "rid": 6171006022,
                        "pid": 6171006022,
                        "oid": 6171006022,                        //图片id
                        "privacy": 0,
                        "uid": 536988617,
                        "originType": 9,
                        "userNick": "盈袖美人",                    //用户昵称
                        "favCount": 0,
                        "commentCount": 0,
                        "itemId": 19028675184,                        //num_iid
                        "favContTitle": "",                        //描述简介
                        "favContAction": "发布",
                        "fromOwnerId": 0,
                        "favContDate": "1天前",
                        "favContAlbum": "小西装@秋之...",            //图集名称
                        "favContAlbumId": 4500885096,                //图集id
                        "hasFavor": 0,
                        "imageUrl": "http://img01.taobaocdn.com/bao/uploaded/i1/10026024190925155/T1cWC5XBFfXXXXXXXX_!!0-item_pic.jpg",
                        "sellerId": 282830026,
                        "hasAuction": 0,
                        "price": "68",                            //价格
                        "bought": 0,
                        "actionType": 1,
                        "shopId": 0,
                        "title": "春装新款韩版女修身泡泡七分袖小西装潮流短款外套糖果色时尚女装",            //宝贝名称（type=2 : 没有title）
                        "commentAppId": 1100083,
                        "commentSubType": 2,
                        "width": 0,
                        "height": 0,
                        "linkUrl": "http://guang.taobao.com/detail/index.htm?uid=536988617&sid=6171006022",
                        "commentCont": []
                    },
                    ...
                ],
                "hasMore": 1,
                "isDaily": false,
                "isLogin": false,
                "totalPage": 25
            },
            "success": 1
        }
        
        
        {"code":1,"data":{"msg":"没有查到数据"},"success":0}
        '''
        try:
            self.response = requests.get(self.url, timeout = self.timeout, allow_redirects = self.allow_redirects)
        
            jsonResponse = json.loads(self.response.text)
            
            if jsonResponse['success'] == 1:
            
                script = jsonResponse['data']['data']
            
                dao = PicDetailDao()
                
                for dicttmp in script:
                    
                    if dicttmp['type'] != 1 and dicttmp['type'] != 2 :
                        continue
                    
                    try:
#                        self.setTaokeDetail(dicttmp)
                        
                        #专辑名称，有可能不存在
                        favContAlbum = ''
                        
                        if "favContAlbum" in dicttmp.keys():
                            favContAlbum = dicttmp['favContAlbum']
                        
                        titleStr = ''
                        if dicttmp['type'] == 1 :
                            titleStr = dicttmp['title']
                        
                        picModel = PicModel.PicModel(dicttmp['oid']
                                            ,dicttmp['imageUrl']
                                            ,dicttmp['height']
                                            ,dicttmp['width']
                                            ,dicttmp['favContTitle']
                                            ,self.cid
                                            ,self.rootCid
                                            ,favContAlbum
                                            ,dicttmp['favContAlbumId']
                                            ,dicttmp['userNick']
                                            ,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            ,dicttmp['itemId']
                                            ,dicttmp['price']
                                            ,titleStr)
                        
                        
                    
                        dao.insertPicDetail(picModel)
                    except Exception,what:
                        print '===========',what
                        
                        print '------- one pic detail error in url is : '+self.url
                        print 'The pic detail is : '+str(dicttmp)
                        
#                        with open(LOG_FILE_PATH,'a') as fp:
#                            fp.write('\n------- one pic detail error in url is : '+self.url)
#                            fp.write('\nThe pic detail is : '+str(dicttmp))
                                     
                        pass
        
        except Exception , what:
            
            print '*********** load pic detail error! url is : '+self.url
            print 'Error message is : '
            print what
            
#            with open(LOG_FILE_PATH,'a') as fp:
#                fp.write('\n*********** load pic detail error! url is : '+self.url)
            
            pass
 
    def run(self):
        print 'Thread is starting!!! url:'+self.url
        self.getPicWaterFlow()


##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    '''
    将html entities转换为中文
    '''
    if len(text) > 0:
    
        def fixup(m):
            text = m.group(0)
            if text[:2] == "&#":
                # character reference
                try:
                    if text[:3] == "&#x":
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity
                try:
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
                except KeyError:
                    pass
            return text # leave as is
        return re.sub("&#?\w+;", fixup, text)
    else:
        return text;

def multi_get(uris, categoaryId,rootCategoaryId, timeout=10,allow_redirects=True):
    '''
    uris uri列表
    timeout 访问url超时时间
    allow_redirects 是否url自动跳转
    '''
    def alive_count(lst):
        alive = map(lambda x : 1 if x.isAlive() else 0, lst)
        return reduce(lambda a,b : a + b, alive)
    
    threads = [ URLThread(uri, categoaryId,rootCategoaryId,timeout, allow_redirects) for uri in uris ]
    
    for thread in threads:
        
        thread.start()
        
        sleep(THREAD_START_DELAY)
        
    while alive_count(threads) > 0:
        sleep(UPDATE_INTERVAL)
        
    return [ (x.url, x.response) for x in threads ]
 
def loadPicDetailByFirestPageUrlAndNextPageNum(cate_id,socketTimeout,redirects,categoaryId,rootCategoaryId,nextAmount=0):
    '''
    cate_id                :淘宝网站上的类别id  cate_id
    socketTimeout          :超时事件
    redirects              :是否接受重定向  
    categoaryId            :抓取内容对应的目录id
    rootCategoaryId        :抓取内容对应的根目录id
    nextAmount             :向后抓取多少页
    '''
    try:
        
        waterflowUrls = []
        
        for idx in range(1,nextAmount+1):
            waterflowUrls.append('http://guang.taobao.com/square/ajax/get_index_source.json?cpage=%d&_input_charset=utf-8&cat_id=%s&tag_id=0&sort=1&type=0&sid=&uid=&t=1369641671186'%(idx,cate_id))
        
        r = multi_get(waterflowUrls,categoaryId,rootCategoaryId,socketTimeout,redirects)
        
    except:
        print u'网络链接失败，请检查网络！！！'
#        with open(LOG_FILE_PATH,'a') as fp:
#            fp.write(u'\n*********** 网络链接失败，请检查网络！！！')
    
#    with open(LOG_FILE_PATH,'a') as fp:
#        fp.write(u'\n================ Get pic detail is END here!!===========================')
#        fp.write(u'\n=================*************************==============================\n\n')
    
    return r

def loadPicDetailByPageUrls(urls,socketTimeout,redirects,categoaryId,rootCategoaryId):
    '''
    url                :必须是第一页
    
    categoaryId        :抓取内容对应的目录id
    rootCategoaryId    :抓取内容对应的根目录id
    '''
    
#    with open(LOG_FILE_PATH,'a') as fp:
#        fp.write(u'\n============================================================================')
#        fp.write(u'\n================ Get pic detail is now starting!!===========================')
#        fp.write(u'\nThe request params are :\nurls=%s\nsocketTimeout=%d\nredirects=%s\ncategoaryId=%d\nrootCategoaryId=%s'
#                 %(str(urls),socketTimeout,redirects,categoaryId,rootCategoaryId))
    
    
    try:
        
        ''' 第一页url与后面的分页url不同，需要获取后面分页的url '''
        waterflowUrls = urls
        
        r = multi_get(waterflowUrls,categoaryId,rootCategoaryId,socketTimeout,redirects)
        
    except:
        print u'网络链接失败，请检查网络！！！'
#        with open(LOG_FILE_PATH,'a') as fp:
#            fp.write(u'\n*********** 网络链接失败，请检查网络！！！')
    
#    with open(LOG_FILE_PATH,'a') as fp:
#        fp.write(u'\n================ Get pic detail is END here!!===========================')
#        fp.write(u'\n=================*************************==============================\n\n')
    
    return r
 
 
def generateDestJsonFile(pagesAmount=1,pageSize=20):
    dao = PicDetailDao()
    
    for idx in range(0,pagesAmount):
        results = dao.getPicDetailByAmount(pageSize,idx*pageSize)
        
        with open('page_'+str(idx),'w') as fp:
            fp.write(unescape(json.dumps(results, default=PicModel.PicModel.serialize)))
        
#    print unescape(json.dumps(results, default=PicModel.PicModel.serialize))
 
def generateDestJsonFileForAlbunmFiles(pageSize=20):
    '''
    生成图集中图片内容json
    对应二级页面---图集内容页面
    '''
    dao = PicDetailDao()
    
    rows = dao.getAlbunmIdByContentsMinAmount(5)
    
    for row in rows :
        pagesAmount = row['amount'] / pageSize
        
        if row['amount'] % pageSize > 0:
            pagesAmount = pagesAmount + 1
        
        for idx in range(0,pagesAmount):
            results = dao.getPicDetailByAlbunmId(row['albunm_id'],pageSize,idx*pageSize)
            
            with open('./generateFilesDir/albunmPage/albunmid_%s-page_%s'%(row['albunm_id'],str(idx)),'w') as fp:
                fp.write(unescape(json.dumps(results, default=PicModel.PicModel.serialize)))
 
def generateDestJsonFileForMainPage():
    '''
    生成首页json内容
    首页推荐图集列表
    http://img04.taobaocdn.com/imgextra/i4/18805020529766261/T1ApJvXqXiXXXXXXXX_!!472868805-0-pix.jpg_100x100.jpg
    '''
    dao = PicDetailDao()
    
    rows = dao.getAlbunmIdByContentsMinAmount(5)
    
    
    '''每页数量'''
    pageSize = 6
    '''总页数'''
    pagesAmount = len(rows) / pageSize
    if len(rows) % pageSize > 0:
        pagesAmount = pagesAmount + 1
            
    
#    for idx in range(0,pagesAmount):
    
    mainResultArray = []
    
    for idx,row in enumerate(rows) :
        
        result = {'albunmId':row['albunm_id'],'albunmName':row['albunm_name'],'pagesAmount':pagesAmount}
        
        picDetails = dao.getPicDetailByAlbunmId(row['albunm_id'],6,0)
        picPathArray = []
        
        for picModel in picDetails:
            picPathArray.append(picModel.picPath+'_200x200.jpg')
            
        result['picPaths'] = picPathArray
        
        mainResultArray.append(result)
        
        if (idx+1) % pageSize == 0 or idx == len(rows)-1:
            with open('./generateFilesDir/mainPage/albunm_page_%s'%(str(idx / pageSize)),'w') as fp:
                fp.write(unescape(json.dumps(mainResultArray)))
            
            mainResultArray = []
            
 
if __name__ == '__main__':
    '''亲子'''
    r = loadPicDetailByFirestPageUrlAndNextPageNum('9'
                                                  ,15,False,categoaryId = 9,rootCategoaryId = 0,nextAmount=40)
    
    '''服饰'''
    r = loadPicDetailByFirestPageUrlAndNextPageNum('1'
                                                  ,15,False,categoaryId = 1,rootCategoaryId = 0,nextAmount=40)

#    r = loadPicDetailByPageUrls(['http://wantu.taobao.com/qinzi/new?since=27248997&type=shopping&bySort=&cateId=5&p=9'
#                                ,'http://wantu.taobao.com/qinzi/new?since=27955204&type=shopping&bySort=&cateId=5&p=3']
#                                ,15,False,categoaryId = 9,rootCategoaryId = 0)
    
    
#    generateDestJsonFile(pagesAmount=10,pageSize=20)
#    generateDestJsonFileForAlbunmFiles()
#    generateDestJsonFileForMainPage()

#    dumpPicDetailSql();
    
    pass
    