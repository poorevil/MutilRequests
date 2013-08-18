#-*- coding:UTF-8 -*-
'''
Created on 2013-3-4

@author: poorevil
'''
import urllib
# -*- coding:utf-8 -*-
import lxml
from lxml import etree

import json
import re, htmlentitydefs


import requests, sys, urllib

reload(sys)
#sys.setdefaultencoding('utf-8')

url = 'http://s.click.taobao.com/t?e=zGU34CA7K%2BPkqB07S4%2FK0CFcRfH0G7DbPkiN9MBfHw5rr4aEFhUmg8hW5aRP3uoTWFcQgy9MKsYoKJD7aP%2F3DTjpPh81b9sB%2BITTUxSERBJ4Pnw5mrf0kCcvzZMwwaERUCXnp3IzMbLyMlIyj8gqNLDuBE5pUayE6da5ISstpHMr88Y3W7hul0U3xlBWn8Za&spm=2014.12283623.1.0'

def get_real_taobao(url):
    _refer = requests.get(url).url
    print _refer
    headers = {'Referer': _refer}
    return requests.get(urllib.unquote(_refer.split('tu=')[1]), headers=headers).url.split('&ali_trackid=')[0]

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
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

def getPicWaterFlow():
    content = urllib.urlopen('http://wantu.taobao.com/qinzi/new?spm=a1z0j.1000827.0.636.WWkD1Y&type=shopping&bySort=&cateId=5').read()
    
    page = etree.HTML(content, parser=None, base_url=None);

    script = page.xpath('//*[@id="pix-waterfall-data"]')

    for jsonStr in script:
        print jsonStr.text
        
        jsonDict = json.loads(jsonStr.text)
        print unescape(jsonDict['data']['waterfall'][8]['desc'])
        
    '''
    获取分页信息
    '''
    script = page.xpath('/html/body/div[3]/div[4]/a')

    for jsonStr in script:
        print jsonStr.get('href')#.text
        
def getPagenationUrlList():
    content = urllib.urlopen('http://wantu.taobao.com/fushi/new/tag-5403?spm=a1z0j.1000817.262580.9.bLjsxD&type=shopping').read()
    
    page = etree.HTML(content, parser=None, base_url=None);

    script = page.xpath('/html/body/div[3]/div[4]/a')

    for jsonStr in script:
        print jsonStr.get('href')#.text
        
#        jsonDict = json.loads(jsonStr.text)
#        print unescape(jsonDict['data']['waterfall'][8]['desc'])


if __name__ == '__main__':
    
#    rel = get_real_taobao(url)
#    print rel
    
#    getPicWaterFlow()
    getPagenationUrlList()

    
#描述
#http://wantu.taobao.com/ajax/PicDetailAjax.do?picId=59511427&userId=22186570&albumId=22162897&t=1363179453253&_method=read
#{"success":1,"data":{"length":18,"albumId":22162897,"currentPage":0,"pageSize":6,"models":[{"carrotNum":0,"collectNum":92,"commentNum":10,"croppedPath":"http://img01.taobaocdn.com/imgextra/i1/16570019748381534/T1MI0qXupaXXXXXXXX_!!22186570-0-pix.jpg","date":"2013-02-22 13:30","desc":"&#30475;&#19968;&#19979;&#23458;&#21381;&#30340;&#25972;&#20307;&#30340;&#26679;&#23376;&#21543;&#12290;&#34429;&#28982;&#19981;&#26159;&#24456;&#22823;&#65292;&#20294;&#26159;&#25402;&#23454;&#29992;&#30340;&#65292;&#31616;&#32422;&#22823;&#26041;&#30340;&#12290;","hasAuction":true,"height":446,"id":59511427,"imgFileId":16570019748377806,"isLike":false,"likeNum":51,"origin":{"title":"顽兔采集工具","url":"/about/tool"},"picPath":"http://img03.taobaocdn.com/imgextra/i3/16570019748377806/T1IiRqXuJbXXXXXXXX_!!22186570-0-pix.jpg","shitNum":0,"tags":[{"title":"&#23458;&#21381;","url":"http://wantu.taobao.com/search/picture?q=%BF%CD%CC%FC"},{"title":"&#23478;&#35013;","url":"http://wantu.taobao.com/search/picture?q=%BC%D2%D7%B0"},{"title":"&#31616;&#32422;","url":"http://wantu.taobao.com/search/picture?q=%BC%F2%D4%BC"}],"width":600},{"carrotNum":1,"collectNum":57,"commentNum":4,"croppedPath":"http://img02.taobaocdn.com/imgextra/i2/16570032861052152/T1RO0oXsxhXXXXXXXX_!!22186570-0-pix.jpg","date":"2013-02-22 13:29","desc":"&#22522;&#26412;&#30340;&#23458;&#21381;&#24212;&#24403;&#30340;&#21151;&#33021;&#37117;&#26159;&#26377;&#30340;&#65292;&#27801;&#21457;&#32972;&#26223;&#20570;&#20102;&#19968;&#20010;&#31616;&#32422;&#30340;&#25601;&#26495;&#65292;&#23454;&#29992;&#21448;&#26377;&#35013;&#39280;&#25928;&#26524;&#12290;","hasAuction":true,"height":446,"id":59507662,"imgFileId":16570019758144895,"isLike":false,"likeNum":18,"origin":{"title":"顽兔采集工具","url":"/about/tool"},"picPath":"http://img02.taobaocdn.com/imgextra/i2/16570019758144895/T1OO8pXpFfXXXXXXXX_!!22186570-0-pix.jpg","shitNum":1,"tags":[{"title":"&#23458;&#21381;","url":"http://wantu.taobao.com/search/picture?q=%BF%CD%CC%FC"},{"title":"&#23478;&#35013;","url":"http://wantu.taobao.com/search/picture?q=%BC%D2%D7%B0"},{"title":"&#31616;&#32422;","url":"http://wantu.taobao.com/search/picture?q=%BC%F2%D4%BC"}],"width":600},{"carrotNum":0,"collectNum":50,"commentNum":2,"croppedPath":"http://img03.taobaocdn.com/imgextra/i3/16570019755741395/T1pbRrXuFaXXXXXXXX_!!22186570-0-pix.jpg","date":"2013-02-22 13:29","desc":"&#23458;&#21381;&#37324;&#38754;&#30340;&#22681;&#65292;&#22522;&#26412;&#20197;&#35013;&#39280;&#20026;&#20027;&#65292;&#21152;&#19968;&#20010;&#23567;&#23567;&#30340;&#20070;&#26550;&#65292;&#20063;&#26159;&#24863;&#35273;&#25402;&#23454;&#29992;&#30340;&#12290;","hasAuction":true,"height":450,"id":59511424,"imgFileId":16570019760970805,"isLike":false,"likeNum":15,"origin":{"title":"顽兔采集工具","url":"/about/tool"},"picPath":"http://img04.taobaocdn.com/imgextra/i4/16570019760970805/T12UNcXwdiXXXXXXXX_!!22186570-0-pix.jpg","shitNum":0,"tags":[{"title":"&#23458;&#21381;","url":"http://wantu.taobao.com/search/picture?q=%BF%CD%CC%FC"},{"title":"&#23478;&#35013;","url":"http://wantu.taobao.com/search/picture?q=%BC%D2%D7%B0"},{"title":"&#31616;&#32422;","url":"http://wantu.taobao.com/search/picture?q=%BC%F2%D4%BC"}],"width":600},{"carrotNum":1,"collectNum":46,"commentNum":1,"croppedPath":"http://img03.taobaocdn.com/imgextra/i3/16570032860972180/T1CxhpXB4dXXXXXXXX_!!22186570-0-pix.jpg","date":"2013-02-22 13:29","desc":"&#20174;&#23458;&#21381;&#37324;&#38754;&#30475;&#23458;&#21381;&#30340;&#26679;&#23376;&#65292;&#23458;&#37324;&#24456;&#22810;&#22320;&#28783;&#30340;&#35013;&#39280;&#65292;&#26174;&#24471;&#38750;&#24120;&#30340;&#28201;&#39336;&#12290;","hasAuction":true,"height":600,"id":59507658,"imgFileId":16570032860980085,"isLike":false,"likeNum":10,"origin":{"title":"顽兔采集工具","url":"/about/tool"},"picPath":"http://img02.taobaocdn.com/imgextra/i2/16570032860980085/T1WYReXuxhXXXXXXXX_!!22186570-0-pix.jpg","shitNum":0,"tags":[{"title":"&#23478;&#35013;","url":"http://wantu.taobao.com/search/picture?q=%BC%D2%D7%B0"},{"title":"&#31616;&#32422;","url":"http://wantu.taobao.com/search/picture?q=%BC%F2%D4%BC"}],"width":450},{"carrotNum":0,"collectNum":22,"commentNum":1,"croppedPath":"http://img04.taobaocdn.com/imgextra/i4/16570032860932263/T1RMdpXrleXXXXXXXX_!!22186570-0-pix.jpg","date":"2013-02-22 13:28","desc":"&#23458;&#21381;&#30340;&#21478;&#19968;&#20010;&#38376;&#21475;&#65292;&#32431;&#33394;&#30340;&#38376;&#19978;&#35013;&#39280;&#20102;&#19968;&#20010;&#24456;&#26377;&#29305;&#33394;&#30340;&#33457;&#29615;&#65292;&#26174;&#24471;&#28201;&#39336;&#22823;&#26041;&#12290;","hasAuction":true,"height":600,"id":59511420,"imgFileId":16570032860916446,"isLike":false,"likeNum":4,"origin":{"title":"顽兔采集工具","url":"/about/tool"},"picPath":"http://img03.taobaocdn.com/imgextra/i3/16570032860916446/T1JWhqXChbXXXXXXXX_!!22186570-0-pix.jpg","shitNum":0,"tags":[{"title":"&#23458;&#21381;","url":"http://wantu.taobao.com/search/picture?q=%BF%CD%CC%FC"},{"title":"&#23478;&#35013;","url":"http://wantu.taobao.com/search/picture?q=%BC%D2%D7%B0"},{"title":"&#31616;&#32422;","url":"http://wantu.taobao.com/search/picture?q=%BC%F2%D4%BC"}],"width":450},{"carrotNum":0,"collectNum":48,"commentNum":0,"croppedPath":"http://img01.taobaocdn.com/imgextra/i1/16570019751002050/T12d0rXDRXXXXXXXXX_!!22186570-0-pix.jpg","date":"2013-02-22 13:28","desc":"&#23458;&#21381;&#30340;&#31383;&#25143;&#65292;&#34174;&#19997;&#30340;&#31383;&#32433;&#35753;&#25972;&#20307;&#30475;&#36215;&#26469;&#38750;&#24120;&#30340;&#28010;&#28459;&#65292;&#25670;&#28891;&#21488;&#33829;&#36896;&#20986;&#19968;&#20010;&#28010;&#28459;&#30340;&#23621;&#23478;&#31354;&#38388;&#12290;","hasAuction":true,"height":600,"id":59508057,"imgFileId":16570019751002047,"isLike":false,"likeNum":31,"origin":{"title":"顽兔采集工具","url":"/about/tool"},"picPath":"http://img02.taobaocdn.com/imgextra/i2/16570019751002047/T1W5trXpFXXXXXXXXX_!!22186570-0-pix.jpg","shitNum":0,"tags":[{"title":"&#23458;&#21381;","url":"http://wantu.taobao.com/search/picture?q=%BF%CD%CC%FC"},{"title":"&#23478;&#35013;","url":"http://wantu.taobao.com/search/picture?q=%BC%D2%D7%B0"},{"title":"&#31616;&#32422;","url":"http://wantu.taobao.com/search/picture?q=%BC%F2%D4%BC"}],"width":450}]}}

#价格
#http://wantu.taobao.com/ajax/PicDetailAjax.do?_method=get_auction&picId=59511427&userId=22186570&imgFileId=16570019748377806
#{"success":1,"data":{"id":13574492,"link":"http://s.click.taobao.com/t?e=zGU34CA7K%2BPkqB07S4%2FK0CFcRfH0G7DbPkiN9MBfHw5qwHI6darPmi8fmTPWFOV%2FkIbxq0MG39%2BmUCqlt6phECyqL9iK9%2F%2FSVcne9LFk1jCwEPnYHWSSknhexfFGzOzYF6yl5%2BPw9xcxedqVTtCY%2BxsupFdOzXbCMXZFByPbG5NjQtFfCg169g4RCdwn%2BW0I&spm=2014.12283623.1.0","price":"918.00","sellNum":0,"title":"特价韩式田园家具 时尚典雅简约实木 象牙白烤漆家居六斗柜"}}

#图集
#http://wantu.taobao.com/album/<22302694--图集id>?spm=a1z0j.1000655.5070283.1.6tSBu6&u=<277472507--用户id>
