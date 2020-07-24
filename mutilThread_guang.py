# -*- coding:utf-8 -*-
import requests

from time import sleep
from threading import Thread

from lxml import etree

from Model import PicModel
from Dao import PicDetailDao

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
 
    ''' 对于目前guang.taobao.com暂时不需要另外获取宝贝的num_iid '''
    def get_real_taobao(self,taobaokeUrl):
        '''
        将淘客加密链接转换为正常链接，目的是取num_iid!!
        
        返回结果类似：http://detail.tmall.com/item.htm?id=14999095831
        '''
        
        _refer = requests.get(taobaokeUrl).url

        headers = {'Referer': _refer}
        
        return requests.get(urllib.unquote(_refer.split('tu=')[1]), headers=headers).url.split('&ali_trackid=')[0]

    ''' 对于目前guang.taobao.com暂时不需要另外获取宝贝的num_iid '''
    def setTaokeDetail(self,picResultDict):
        
        '''
        根据详细信息获取淘宝宝贝num_iid
        
        价格链接
        http://wantu.taobao.com/ajax/PicDetailAjax.do?_method=get_auction&picId=59511427&userId=22186570&imgFileId=16570019748377806
        {
            "success": 1,
            "data": {
                "id": 13574492,
                "link": "http://s.click.taobao.com/t?e=zGU34CA7K%2BPkqB07S4%2FK0CFcRfH...4RCdwn%2BW0I&spm=2014.12283623.1.0",
                "price": "918.00",
                "sellNum": 0,
                "title": "特价韩式田园家具 时尚典雅简约实木 象牙白烤漆家居六斗柜"
            }
        }
        '''
        
        picId = picResultDict['id']
        userId = picResultDict['info']['userId']
#        albumId = picResultDict['info']['albumId']
        
        detailUrlPath = 'http://wantu.taobao.com/ajax/PicDetailAjax.do?_method=get_auction&picId=%s&userId=%s&imgFileId=16570019748377806'%(picId,userId)
        
        detailPaghResponse = requests.get(detailUrlPath, timeout = self.timeout, allow_redirects = self.allow_redirects)
        
        detailJsonDict = json.loads(detailPaghResponse.text)
        
        '''{"success":0,"msg":"请求的数据错误!"}'''
        
        if len(detailJsonDict) > 0 and detailJsonDict['success'] == 1 :
        
            taokeUrl = detailJsonDict['data']['link']
            
            if taokeUrl.find('s.click.taobao.com') >= 0:
                taokeUrl = self.get_real_taobao(detailJsonDict['data']['link'])
    
            num_iid = taokeUrl[taokeUrl.find('id=')+3:]
            
            picResultDict['num_iid'] = num_iid
    #        print 'num_iid-----:['+num_iid+']'
            picResultDict['price'] = detailJsonDict['data']['price']
            picResultDict['sellNum'] = detailJsonDict['data']['sellNum']
            picResultDict['title'] = detailJsonDict['data']['title']
        
        else:
            picResultDict['num_iid'] = ''
    #        print 'num_iid-----:['+num_iid+']'
            picResultDict['price'] = ''
            picResultDict['sellNum'] = ''
            picResultDict['title'] = ''
    
    def getPicWaterFlow(self):
        '''
        抓取瀑布流列表
        返回最初的瀑布流图片加描述
        
        {
            "code": 0,
            "data": {
                "data": [
                    {
                        "bought": 0,
                        "commentAppId": 1100083,
                        "commentCont": [],
                        "commentCount": 0,
                        "commentSubType": 2,
                        "favContAction": "发布",
                        "favContAlbum": "六一送神马!",                   //图集名称
                        "favContAlbumId": 3000151648,                   //图集id
                        "favContDate": "3天前",
                        "favContTitle": "六一热卖中。木马婴儿床铃只需要49.5即带回家，床铃作用：婴幼儿摇铃造型独特，设...",      //描述简介（部分）
                        "favCount": 4,
                        "fromOwnerId": 0,
                        "fromOwnerNick": "",
                        "hasAuction": 0,
                        "hasFavor": 0,
                        "height": 0,                                        //高度
                        "imageUrl": "http://img04.taobaocdn.com/bao/uploaded/i4/18108020333025166/T1gThGXDBcXXXXXXXX_!!0-item_pic.jpg",                                             //图片url
                        "itemId": 17516890064,                        //num_iid
                        "oid": 3003276006,                              //图片id
                        "originType": 0,
                        "pid": 3003276006,
                        "price": "48",                                      //价格
                        "rid": 3003276006,
                        "sellerId": 633938108,
                        "title": "包邮热卖床铃婴儿玩具床头铃木马音乐床铃3-4-5-6-7个月宝宝玩具",          //宝贝名称
                        "type": 1,
                        "uid": 13387716,
                        "userNick": "qy2007",                               //用户昵称
                        "width": 0                                          //宽度
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
            
                dao = PicDetailDao.PicDetailDao()
                
                for dicttmp in script:
                    
                    try:
#                        self.setTaokeDetail(dicttmp)
                        
                        #专辑名称，有可能不存在
                        favContAlbum = ''
                        
                        if "favContAlbum" in dicttmp.keys():
                            favContAlbum = dicttmp['favContAlbum']
    
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
                                            ,dicttmp['title'])
                        
                        
                    
                        dao.insertPicDetail(picModel)
                    except Exception,what:
                        print what
                        
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
    cate_id            :淘宝网站上的类别id  cate_id
    
    categoaryId        :抓取内容对应的目录id
    rootCategoaryId    :抓取内容对应的根目录id
    '''
    
    try:
        
#        ''' 第一页url与后面的分页url不同，需要获取后面分页的url '''
#        waterflowUrls = [url]
#        
#        if nextAmount > 0 :
#            
#            content = requests.get(url, timeout = socketTimeout, allow_redirects = redirects).text
#           
#            page = etree.HTML(content, parser=None, base_url=None);
#                
#            '''
#            获取分页信息
#            '''
#            script = page.xpath('/html/body/div[3]/div[3]/p/a')#('/html/body/div[4]/div[4]/a')
#                
#            paginationUrl = script[2].get('href')
#            
#            for idx in range(2,nextAmount+1):
#                
#                waterflowUrls.append(paginationUrl[:len(paginationUrl)-1]+str(idx))
        
        waterflowUrls = []
        
        for idx in range(1,nextAmount+1):
            waterflowUrls.append('http://guang.taobao.com/square/ajax/get_index_source.json?cpage=%d&_input_charset=utf-8&cat_id=%s&tag_id=0&sort=0&type=1&sid=&uid=&t=1369641671186'%(idx,cate_id))
        
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
    dao = PicDetailDao.PicDetailDao()
    
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
    dao = PicDetailDao.PicDetailDao()
    
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
    dao = PicDetailDao.PicDetailDao()
    
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
            
def dumpPicDetailSql():
    '''
    生成mysql导出文件
    '''
    
    dao = PicDetailDao.PicDetailDao()
    results = dao.getAllPicDetail()
    
    with open('./generateFilesDir/dumpSql/pic_detail.sql-1','w') as fp:
        fp.write('''-- MySQL dump 10.13  Distrib 5.5.30, for Linux (x86_64)
--
-- Host: localhost    Database: 
-- ------------------------------------------------------
-- Server version    (null)

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `lifepictorial`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `lifepictorial` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `lifepictorial`;

--
-- Table structure for table `advert`
--

DROP TABLE IF EXISTS `advert`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `advert` (
  `aid` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `pic_url` varchar(255) DEFAULT NULL,
  `ad_type` int(11) NOT NULL,
  `ad_identifier` varchar(255) DEFAULT NULL,
  `show_order` int(11) DEFAULT NULL,
  `app_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`aid`),
  UNIQUE KEY `aid_UNIQUE` (`aid`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `advert`
--

LOCK TABLES `advert` WRITE;
/*!40000 ALTER TABLE `advert` DISABLE KEYS */;
INSERT INTO `advert` VALUES (4,'广告名称2','2',2,'2',2,'2'),(9,'童装 女童春装2013 新款韩版运动休闲套装 中大儿童春秋款蝙蝠衫','http://img04.taobaocdn.com/imgextra/i4/1584587479/T2IAYIXgpXXXXXXXXX_!!1584587479.jpg_600x600.jpg',1,'http://detail.tmall.com/item.htm?id=17345661702&ali_trackid=2:mm_13983871_0_0:1366472585_3k3_1631249868',1,'4'),(10,'丝丝百合童装 女童 2013春装新款男童秋装天鹅绒韩版运动儿童套装','http://img01.taobaocdn.com/imgextra/i1/746279814/T2GNhlXdpOXXXXXXXX_!!746279814.jpg',1,'http://detail.tmall.com/item.htm?id=16548715600&ali_trackid=2:mm_13983871_0_0:1366472834_3k1_1645897648',2,'4'),(11,'秋柰仒童装 2013春装新款韩版女童连衣裙 儿童针织两件套公主裙子','http://img04.taobaocdn.com/imgextra/i4/651474559/T2MwjyXk0aXXXXXXXX_!!651474559.jpg',1,'http://detail.tmall.com/item.htm?id=22562596273&ali_trackid=2:mm_13983871_0_0:1366472988_310_313508864',0,'4'),(12,'EXSCV 男装 春款韩版衬衫男士修身长袖牛仔衬衫 新品休闲衬衣','http://img01.taobaocdn.com/imgextra/i1/730441733/T2tpKpXdXcXXXXXXXX_!!730441733.jpg',1,'http://s.click.taobao.com/t?e=zGU34CA7K%2BPkqB07S4%2FK0CFcRfH0GoT805sipKj0%2FbwrM8GhUBn7gmMVOS0m4nGclSKf6wLsigYQDM4IOIq0jetVMoHdhcE8KC5FdMtOZIuDog%3D%3D',3,'1'),(15,'比伦奴2013春款女装新款PU小外套皮夹克欧美机车修身小皮衣女短款','http://img02.taobaocdn.com/imgextra/i2/550987554/T2bO6EXgxaXXXXXXXX_!!550987554.jpg',1,'http://detail.tmall.com/item.htm?id=12641531213&ali_trackid=2:mm_13983871_0_0:1366531033_4k4_856224577',1,'1'),(17,'沙雅利新款桑蚕丝家居服 蕾丝边短袖性感真丝睡衣女 夏套装两件套','http://img01.taobaocdn.com/imgextra/i1/196682344/T23Qf0XaRXXXXXXXXX_!!196682344.jpg',1,'http://detail.tmall.com/item.htm?id=17797733426&ali_trackid=2:mm_13983871_0_0:1368071230_3k4_1323864233',0,'1');
/*!40000 ALTER TABLE `advert` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apps`
--

DROP TABLE IF EXISTS `apps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apps` (
  `app_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `detail` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`app_id`),
  UNIQUE KEY `app_id_UNIQUE` (`app_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apps`
--

LOCK TABLES `apps` WRITE;
/*!40000 ALTER TABLE `apps` DISABLE KEYS */;
INSERT INTO `apps` VALUES (1,'女装HD','潮流服饰指南'),(4,'宝贝画报HD','ipad客户端');
/*!40000 ALTER TABLE `apps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categoary`
--

DROP TABLE IF EXISTS `categoary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categoary` (
  `cid` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `parent_cid` varchar(255) NOT NULL DEFAULT '0',
  PRIMARY KEY (`cid`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoary`
--

LOCK TABLES `categoary` WRITE;
/*!40000 ALTER TABLE `categoary` DISABLE KEYS */;
INSERT INTO `categoary` VALUES (1,'女装','0'),(9,'亲子','0');
/*!40000 ALTER TABLE `categoary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pic_detail`
--

DROP TABLE IF EXISTS `pic_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pic_detail` (
  `pid` varchar(255) NOT NULL,
  `pic_path` varchar(255) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `width` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `cate_id` int(11) DEFAULT NULL,
  `root_cate_id` int(11) DEFAULT NULL,
  `albunm_name` varchar(255) DEFAULT NULL,
  `albunm_id` varchar(255) DEFAULT NULL,
  `user_id` varchar(255) DEFAULT NULL,
  `time` varchar(255) DEFAULT NULL,
  `taoke_num_iid` varchar(255) DEFAULT NULL,
  `taoke_title` varchar(255) DEFAULT NULL,
  `taoke_price` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`pid`),
  UNIQUE KEY `index_pid` (`pid`),
  KEY `index_albunm_id` (`albunm_id`),
  KEY `index_cate_id` (`cate_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pic_detail`
--

LOCK TABLES `pic_detail` WRITE;
/*!40000 ALTER TABLE `pic_detail` DISABLE KEYS */;
        ''')
    
    
        for row in results:
            fp.write('''
INSERT INTO pic_detail VALUES ("%s","%s",%d,%d,"%s",%d,%d,"%s","%s","%s","%s","%s","%s","%s");\n'''
                     %(row[0],
                       row[1],
                       row[2],
                       row[3],
                       unescape(row[4]).replace('\"','\\"'),
                       row[5],
                       row[6],
                       unescape(row[7]).replace('\"','\\"'),
                       row[8],
                       row[9],
                       row[10],
                       row[11],
                       row[12],
                       row[13],))
            
            
        fp.write('''
/*!40000 ALTER TABLE `pic_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `mysql`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `mysql` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `mysql`;

--
-- Table structure for table `general_log`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `general_log` (
  `event_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_host` mediumtext NOT NULL,
  `thread_id` int(11) NOT NULL,
  `server_id` int(10) unsigned NOT NULL,
  `command_type` varchar(64) NOT NULL,
  `argument` mediumtext NOT NULL
) ENGINE=CSV DEFAULT CHARSET=utf8 COMMENT='General log';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `slow_log`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `slow_log` (
  `start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_host` mediumtext NOT NULL,
  `query_time` time NOT NULL,
  `lock_time` time NOT NULL,
  `rows_sent` int(11) NOT NULL,
  `rows_examined` int(11) NOT NULL,
  `db` varchar(512) NOT NULL,
  `last_insert_id` int(11) NOT NULL,
  `insert_id` int(11) NOT NULL,
  `server_id` int(10) unsigned NOT NULL,
  `sql_text` mediumtext NOT NULL
) ENGINE=CSV DEFAULT CHARSET=utf8 COMMENT='Slow log';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `columns_priv`
--

DROP TABLE IF EXISTS `columns_priv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `columns_priv` (
  `Host` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Db` char(64) COLLATE utf8_bin NOT NULL DEFAULT '',
  `User` char(16) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Table_name` char(64) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Column_name` char(64) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Column_priv` set('Select','Insert','Update','References') CHARACTER SET utf8 NOT NULL DEFAULT '',
  PRIMARY KEY (`Host`,`Db`,`User`,`Table_name`,`Column_name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Column privileges';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `columns_priv`
--

LOCK TABLES `columns_priv` WRITE;
/*!40000 ALTER TABLE `columns_priv` DISABLE KEYS */;
/*!40000 ALTER TABLE `columns_priv` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `db`
--

DROP TABLE IF EXISTS `db`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `db` (
  `Host` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Db` char(64) COLLATE utf8_bin NOT NULL DEFAULT '',
  `User` char(16) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Select_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Insert_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Update_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Delete_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Drop_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Grant_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `References_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Index_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Alter_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_tmp_table_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Lock_tables_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_view_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Show_view_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_routine_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Alter_routine_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Execute_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Event_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Trigger_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  PRIMARY KEY (`Host`,`Db`,`User`),
  KEY `User` (`User`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Database privileges';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `db`
--

LOCK TABLES `db` WRITE;
/*!40000 ALTER TABLE `db` DISABLE KEYS */;
INSERT INTO `db` VALUES ('%','test','','Y','Y','Y','Y','Y','Y','N','Y','Y','Y','Y','Y','Y','Y','Y','N','N','Y','Y'),('%','test\\_%','','Y','Y','Y','Y','Y','Y','N','Y','Y','Y','Y','Y','Y','Y','Y','N','N','Y','Y');
/*!40000 ALTER TABLE `db` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `event` (
  `db` char(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '',
  `name` char(64) NOT NULL DEFAULT '',
  `body` longblob NOT NULL,
  `definer` char(77) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '',
  `execute_at` datetime DEFAULT NULL,
  `interval_value` int(11) DEFAULT NULL,
  `interval_field` enum('YEAR','QUARTER','MONTH','DAY','HOUR','MINUTE','WEEK','SECOND','MICROSECOND','YEAR_MONTH','DAY_HOUR','DAY_MINUTE','DAY_SECOND','HOUR_MINUTE','HOUR_SECOND','MINUTE_SECOND','DAY_MICROSECOND','HOUR_MICROSECOND','MINUTE_MICROSECOND','SECOND_MICROSECOND') DEFAULT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `modified` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `last_executed` datetime DEFAULT NULL,
  `starts` datetime DEFAULT NULL,
  `ends` datetime DEFAULT NULL,
  `status` enum('ENABLED','DISABLED','SLAVESIDE_DISABLED') NOT NULL DEFAULT 'ENABLED',
  `on_completion` enum('DROP','PRESERVE') NOT NULL DEFAULT 'DROP',
  `sql_mode` set('REAL_AS_FLOAT','PIPES_AS_CONCAT','ANSI_QUOTES','IGNORE_SPACE','NOT_USED','ONLY_FULL_GROUP_BY','NO_UNSIGNED_SUBTRACTION','NO_DIR_IN_CREATE','POSTGRESQL','ORACLE','MSSQL','DB2','MAXDB','NO_KEY_OPTIONS','NO_TABLE_OPTIONS','NO_FIELD_OPTIONS','MYSQL323','MYSQL40','ANSI','NO_AUTO_VALUE_ON_ZERO','NO_BACKSLASH_ESCAPES','STRICT_TRANS_TABLES','STRICT_ALL_TABLES','NO_ZERO_IN_DATE','NO_ZERO_DATE','INVALID_DATES','ERROR_FOR_DIVISION_BY_ZERO','TRADITIONAL','NO_AUTO_CREATE_USER','HIGH_NOT_PRECEDENCE','NO_ENGINE_SUBSTITUTION','PAD_CHAR_TO_FULL_LENGTH') NOT NULL DEFAULT '',
  `comment` char(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '',
  `originator` int(10) unsigned NOT NULL,
  `time_zone` char(64) CHARACTER SET latin1 NOT NULL DEFAULT 'SYSTEM',
  `character_set_client` char(32) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `collation_connection` char(32) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `db_collation` char(32) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `body_utf8` longblob,
  PRIMARY KEY (`db`,`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Events';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `func`
--

DROP TABLE IF EXISTS `func`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `func` (
  `name` char(64) COLLATE utf8_bin NOT NULL DEFAULT '',
  `ret` tinyint(1) NOT NULL DEFAULT '0',
  `dl` char(128) COLLATE utf8_bin NOT NULL DEFAULT '',
  `type` enum('function','aggregate') CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='User defined functions';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `func`
--

LOCK TABLES `func` WRITE;
/*!40000 ALTER TABLE `func` DISABLE KEYS */;
/*!40000 ALTER TABLE `func` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_category`
--

DROP TABLE IF EXISTS `help_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `help_category` (
  `help_category_id` smallint(5) unsigned NOT NULL,
  `name` char(64) NOT NULL,
  `parent_category_id` smallint(5) unsigned DEFAULT NULL,
  `url` char(128) NOT NULL,
  PRIMARY KEY (`help_category_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='help categories';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_category`
--

LOCK TABLES `help_category` WRITE;
/*!40000 ALTER TABLE `help_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `help_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_keyword`
--

DROP TABLE IF EXISTS `help_keyword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `help_keyword` (
  `help_keyword_id` int(10) unsigned NOT NULL,
  `name` char(64) NOT NULL,
  PRIMARY KEY (`help_keyword_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='help keywords';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_keyword`
--

LOCK TABLES `help_keyword` WRITE;
/*!40000 ALTER TABLE `help_keyword` DISABLE KEYS */;
/*!40000 ALTER TABLE `help_keyword` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_relation`
--

DROP TABLE IF EXISTS `help_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `help_relation` (
  `help_topic_id` int(10) unsigned NOT NULL,
  `help_keyword_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`help_keyword_id`,`help_topic_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='keyword-topic relation';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_relation`
--

LOCK TABLES `help_relation` WRITE;
/*!40000 ALTER TABLE `help_relation` DISABLE KEYS */;
/*!40000 ALTER TABLE `help_relation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_topic`
--

DROP TABLE IF EXISTS `help_topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `help_topic` (
  `help_topic_id` int(10) unsigned NOT NULL,
  `name` char(64) NOT NULL,
  `help_category_id` smallint(5) unsigned NOT NULL,
  `description` text NOT NULL,
  `example` text NOT NULL,
  `url` char(128) NOT NULL,
  PRIMARY KEY (`help_topic_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='help topics';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_topic`
--

LOCK TABLES `help_topic` WRITE;
/*!40000 ALTER TABLE `help_topic` DISABLE KEYS */;
/*!40000 ALTER TABLE `help_topic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `host`
--

DROP TABLE IF EXISTS `host`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host` (
  `Host` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Db` char(64) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Select_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Insert_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Update_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Delete_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Drop_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Grant_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `References_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Index_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Alter_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_tmp_table_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Lock_tables_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_view_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Show_view_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_routine_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Alter_routine_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Execute_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Trigger_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  PRIMARY KEY (`Host`,`Db`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Host privileges;  Merged with database privileges';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `host`
--

LOCK TABLES `host` WRITE;
/*!40000 ALTER TABLE `host` DISABLE KEYS */;
/*!40000 ALTER TABLE `host` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ndb_binlog_index`
--

DROP TABLE IF EXISTS `ndb_binlog_index`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ndb_binlog_index` (
  `Position` bigint(20) unsigned NOT NULL,
  `File` varchar(255) NOT NULL,
  `epoch` bigint(20) unsigned NOT NULL,
  `inserts` bigint(20) unsigned NOT NULL,
  `updates` bigint(20) unsigned NOT NULL,
  `deletes` bigint(20) unsigned NOT NULL,
  `schemaops` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`epoch`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ndb_binlog_index`
--

LOCK TABLES `ndb_binlog_index` WRITE;
/*!40000 ALTER TABLE `ndb_binlog_index` DISABLE KEYS */;
/*!40000 ALTER TABLE `ndb_binlog_index` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plugin`
--

DROP TABLE IF EXISTS `plugin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plugin` (
  `name` varchar(64) NOT NULL DEFAULT '',
  `dl` varchar(128) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='MySQL plugins';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plugin`
--

LOCK TABLES `plugin` WRITE;
/*!40000 ALTER TABLE `plugin` DISABLE KEYS */;
/*!40000 ALTER TABLE `plugin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proc`
--

DROP TABLE IF EXISTS `proc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `proc` (
  `db` char(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '',
  `name` char(64) NOT NULL DEFAULT '',
  `type` enum('FUNCTION','PROCEDURE') NOT NULL,
  `specific_name` char(64) NOT NULL DEFAULT '',
  `language` enum('SQL') NOT NULL DEFAULT 'SQL',
  `sql_data_access` enum('CONTAINS_SQL','NO_SQL','READS_SQL_DATA','MODIFIES_SQL_DATA') NOT NULL DEFAULT 'CONTAINS_SQL',
  `is_deterministic` enum('YES','NO') NOT NULL DEFAULT 'NO',
  `security_type` enum('INVOKER','DEFINER') NOT NULL DEFAULT 'DEFINER',
  `param_list` blob NOT NULL,
  `returns` longblob NOT NULL,
  `body` longblob NOT NULL,
  `definer` char(77) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '',
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `modified` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `sql_mode` set('REAL_AS_FLOAT','PIPES_AS_CONCAT','ANSI_QUOTES','IGNORE_SPACE','NOT_USED','ONLY_FULL_GROUP_BY','NO_UNSIGNED_SUBTRACTION','NO_DIR_IN_CREATE','POSTGRESQL','ORACLE','MSSQL','DB2','MAXDB','NO_KEY_OPTIONS','NO_TABLE_OPTIONS','NO_FIELD_OPTIONS','MYSQL323','MYSQL40','ANSI','NO_AUTO_VALUE_ON_ZERO','NO_BACKSLASH_ESCAPES','STRICT_TRANS_TABLES','STRICT_ALL_TABLES','NO_ZERO_IN_DATE','NO_ZERO_DATE','INVALID_DATES','ERROR_FOR_DIVISION_BY_ZERO','TRADITIONAL','NO_AUTO_CREATE_USER','HIGH_NOT_PRECEDENCE','NO_ENGINE_SUBSTITUTION','PAD_CHAR_TO_FULL_LENGTH') NOT NULL DEFAULT '',
  `comment` text CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `character_set_client` char(32) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `collation_connection` char(32) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `db_collation` char(32) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `body_utf8` longblob,
  PRIMARY KEY (`db`,`name`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Stored Procedures';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proc`
--

LOCK TABLES `proc` WRITE;
/*!40000 ALTER TABLE `proc` DISABLE KEYS */;
/*!40000 ALTER TABLE `proc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `procs_priv`
--

DROP TABLE IF EXISTS `procs_priv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `procs_priv` (
  `Host` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Db` char(64) COLLATE utf8_bin NOT NULL DEFAULT '',
  `User` char(16) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Routine_name` char(64) CHARACTER SET utf8 NOT NULL DEFAULT '',
  `Routine_type` enum('FUNCTION','PROCEDURE') COLLATE utf8_bin NOT NULL,
  `Grantor` char(77) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Proc_priv` set('Execute','Alter Routine','Grant') CHARACTER SET utf8 NOT NULL DEFAULT '',
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Host`,`Db`,`User`,`Routine_name`,`Routine_type`),
  KEY `Grantor` (`Grantor`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Procedure privileges';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `procs_priv`
--

LOCK TABLES `procs_priv` WRITE;
/*!40000 ALTER TABLE `procs_priv` DISABLE KEYS */;
/*!40000 ALTER TABLE `procs_priv` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proxies_priv`
--

DROP TABLE IF EXISTS `proxies_priv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `proxies_priv` (
  `Host` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `User` char(16) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Proxied_host` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Proxied_user` char(16) COLLATE utf8_bin NOT NULL DEFAULT '',
  `With_grant` tinyint(1) NOT NULL DEFAULT '0',
  `Grantor` char(77) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Host`,`User`,`Proxied_host`,`Proxied_user`),
  KEY `Grantor` (`Grantor`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='User proxy privileges';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proxies_priv`
--

LOCK TABLES `proxies_priv` WRITE;
/*!40000 ALTER TABLE `proxies_priv` DISABLE KEYS */;
INSERT INTO `proxies_priv` VALUES ('localhost','root','','',1,'','2013-03-24 05:23:44');
/*!40000 ALTER TABLE `proxies_priv` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servers`
--

DROP TABLE IF EXISTS `servers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `servers` (
  `Server_name` char(64) NOT NULL DEFAULT '',
  `Host` char(64) NOT NULL DEFAULT '',
  `Db` char(64) NOT NULL DEFAULT '',
  `Username` char(64) NOT NULL DEFAULT '',
  `Password` char(64) NOT NULL DEFAULT '',
  `Port` int(4) NOT NULL DEFAULT '0',
  `Socket` char(64) NOT NULL DEFAULT '',
  `Wrapper` char(64) NOT NULL DEFAULT '',
  `Owner` char(64) NOT NULL DEFAULT '',
  PRIMARY KEY (`Server_name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='MySQL Foreign Servers table';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servers`
--

LOCK TABLES `servers` WRITE;
/*!40000 ALTER TABLE `servers` DISABLE KEYS */;
/*!40000 ALTER TABLE `servers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tables_priv`
--

DROP TABLE IF EXISTS `tables_priv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tables_priv` (
  `Host` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Db` char(64) COLLATE utf8_bin NOT NULL DEFAULT '',
  `User` char(16) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Table_name` char(64) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Grantor` char(77) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Table_priv` set('Select','Insert','Update','Delete','Create','Drop','Grant','References','Index','Alter','Create View','Show view','Trigger') CHARACTER SET utf8 NOT NULL DEFAULT '',
  `Column_priv` set('Select','Insert','Update','References') CHARACTER SET utf8 NOT NULL DEFAULT '',
  PRIMARY KEY (`Host`,`Db`,`User`,`Table_name`),
  KEY `Grantor` (`Grantor`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Table privileges';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tables_priv`
--

LOCK TABLES `tables_priv` WRITE;
/*!40000 ALTER TABLE `tables_priv` DISABLE KEYS */;
/*!40000 ALTER TABLE `tables_priv` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `time_zone`
--

DROP TABLE IF EXISTS `time_zone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `time_zone` (
  `Time_zone_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Use_leap_seconds` enum('Y','N') NOT NULL DEFAULT 'N',
  PRIMARY KEY (`Time_zone_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Time zones';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `time_zone`
--

LOCK TABLES `time_zone` WRITE;
/*!40000 ALTER TABLE `time_zone` DISABLE KEYS */;
/*!40000 ALTER TABLE `time_zone` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `time_zone_leap_second`
--

DROP TABLE IF EXISTS `time_zone_leap_second`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `time_zone_leap_second` (
  `Transition_time` bigint(20) NOT NULL,
  `Correction` int(11) NOT NULL,
  PRIMARY KEY (`Transition_time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Leap seconds information for time zones';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `time_zone_leap_second`
--

LOCK TABLES `time_zone_leap_second` WRITE;
/*!40000 ALTER TABLE `time_zone_leap_second` DISABLE KEYS */;
/*!40000 ALTER TABLE `time_zone_leap_second` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `time_zone_name`
--

DROP TABLE IF EXISTS `time_zone_name`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `time_zone_name` (
  `Name` char(64) NOT NULL,
  `Time_zone_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`Name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Time zone names';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `time_zone_name`
--

LOCK TABLES `time_zone_name` WRITE;
/*!40000 ALTER TABLE `time_zone_name` DISABLE KEYS */;
/*!40000 ALTER TABLE `time_zone_name` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `time_zone_transition`
--

DROP TABLE IF EXISTS `time_zone_transition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `time_zone_transition` (
  `Time_zone_id` int(10) unsigned NOT NULL,
  `Transition_time` bigint(20) NOT NULL,
  `Transition_type_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`Time_zone_id`,`Transition_time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Time zone transitions';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `time_zone_transition`
--

LOCK TABLES `time_zone_transition` WRITE;
/*!40000 ALTER TABLE `time_zone_transition` DISABLE KEYS */;
/*!40000 ALTER TABLE `time_zone_transition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `time_zone_transition_type`
--

DROP TABLE IF EXISTS `time_zone_transition_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `time_zone_transition_type` (
  `Time_zone_id` int(10) unsigned NOT NULL,
  `Transition_type_id` int(10) unsigned NOT NULL,
  `Offset` int(11) NOT NULL DEFAULT '0',
  `Is_DST` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `Abbreviation` char(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`Time_zone_id`,`Transition_type_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Time zone transition types';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `time_zone_transition_type`
--

LOCK TABLES `time_zone_transition_type` WRITE;
/*!40000 ALTER TABLE `time_zone_transition_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `time_zone_transition_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `Host` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `User` char(16) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Password` char(41) CHARACTER SET latin1 COLLATE latin1_bin NOT NULL DEFAULT '',
  `Select_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Insert_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Update_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Delete_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Drop_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Reload_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Shutdown_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Process_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `File_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Grant_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `References_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Index_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Alter_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Show_db_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Super_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_tmp_table_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Lock_tables_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Execute_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Repl_subordinate_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Repl_client_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_view_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Show_view_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_routine_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Alter_routine_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_user_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Event_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Trigger_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_tablespace_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `ssl_type` enum('','ANY','X509','SPECIFIED') CHARACTER SET utf8 NOT NULL DEFAULT '',
  `ssl_cipher` blob NOT NULL,
  `x509_issuer` blob NOT NULL,
  `x509_subject` blob NOT NULL,
  `max_questions` int(11) unsigned NOT NULL DEFAULT '0',
  `max_updates` int(11) unsigned NOT NULL DEFAULT '0',
  `max_connections` int(11) unsigned NOT NULL DEFAULT '0',
  `max_user_connections` int(11) unsigned NOT NULL DEFAULT '0',
  `plugin` char(64) COLLATE utf8_bin DEFAULT '',
  `authentication_string` text COLLATE utf8_bin,
  PRIMARY KEY (`Host`,`User`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Users and global privileges';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('localhost','root','','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','','','','',0,0,0,0,'',''),('127.0.0.1','root','','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','','','','',0,0,0,0,'',''),('::1','root','','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','','','','',0,0,0,0,'',''),('localhost','','','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','','','','',0,0,0,0,'',NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Flush Grant Tables 
--

/*! FLUSH PRIVILEGES */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-05-15  1:19:03

''')
 
 
if __name__ == '__main__':
    '''亲子'''
#    r = loadPicDetailByFirestPageUrlAndNextPageNum('9'
#                                                  ,15,False,categoaryId = 9,rootCategoaryId = 0,nextAmount=40)
    
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
    
    
    
#    for url, data in r:
#        if data: print "received this data %s from this url %s" % (data.text, url)