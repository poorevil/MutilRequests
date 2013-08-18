# -*- coding:utf-8 -*-

'''
Created on 2013-8-3

@author: poorevil
'''
import re, htmlentitydefs

##
# copy from http://effbot.org/zone/re-sub.htm#unescape-html
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




if __name__ == '__main__':
    
    str = '''
    {
                "type": 1,
                "rid": 6171006022,
                "pid": 6171006022,
                "oid": 6171006022,
                "privacy": 0,
                "uid": 536988617,
                "originType": 9,
                "userNick": "盈袖美人",
                "favCount": 0,
                "commentCount": 0,
                "itemId": 19028675184,
                "favContTitle": "",
                "favContAction": "发布",
                "fromOwnerId": 0,
                "favContDate": "1天前",
                "favContAlbum": "&#23567;&#35199;&#35013;@&#31179;&#20043;...",
                "favContAlbumId": 4500885096,
                "hasFavor": 0,
                "imageUrl": "http://img01.taobaocdn.com/bao/uploaded/i1/10026024190925155/T1cWC5XBFfXXXXXXXX_!!0-item_pic.jpg",
                "sellerId": 282830026,
                "hasAuction": 0,
                "price": "68",
                "bought": 0,
                "actionType": 1,
                "shopId": 0,
                "title": "春装新款韩版女修身泡泡七分袖小西装潮流短款外套糖果色时尚女装",
                "commentAppId": 1100083,
                "commentSubType": 2,
                "width": 0,
                "height": 0,
                "linkUrl": "http://guang.taobao.com/detail/index.htm?uid=536988617&sid=6171006022",
                "commentCont": []
            },
    '''
    
    print unescape(str)
    
    pass