# Python 3

import re
import time
import logging
import requests
from pyquery import PyQuery as pyq

HEADERS = {
    'Pragma': 'no-cache' ,
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'no-cache',
    'Cookie': 'x-wl-uid=1G/Ua8LCVV7NMunFo0N84+SfQ0Dt7QUjlgQ+1RyvqmLqQU4lo+qn1mZiATac9BtdFhECuQk424Tr+UI3zLoEy2g==; gw-warning-displayed=displayed; session-token="LgFqvcvpAp4LCMBODKSyLHOW1tLBI7+kel7x5eKDedEfb8gz/Hhf4pAyrQSWqE7lUP/2TacWrJEysAxYd3xhanWtOd+8rUseY+ZLu/9CrkzDGl8HBMruT83rtPx7oW0aCVpoL0ZORd/v/mWcWYO8UHxHb2DhheYAErhuT+jPkphy+ZbT8LAeVLu4VHEeCDG0Gq9PtUJZ3hIZNXQU02lgpIqDeXJuW/q/uTI7qy0wjsk="; x-acbcn="ZO7wIIFH9JEW@FlVQVY4TfqeqoCwkMAN"; at-main=Atza|IwEBIK4TgxAng8QgP1Fl-lym5CoWqhUi3N2AIFsGGP_IS-PCYZqZ6ZHGcpqHsyk9TAxFPAEdMkqOEHVOHnlDDTKvD67J95qP5D240gov9yerWXzlxNAVTU1wDsEqWoMp0OL9NknSOL0zmgga18oDoBnet8gdPzcaIQqD3mB8JP2AfBAW9GhRItg3uHOCEvhaVq6jRcd-FwYaY9dXijqG3H06UA7oaxwezierMX8OZtoC8Dqlz1pNdOtJKQxAe_sKPId948WPGF1JQx4Z81oH2B_rbd8ZMhGqtvlKl4dm0mCwPFqOM50H9skqBD3VCBc8e_sNyjmW-NTLYFliL7GQ_5Z8RT5WGMneBlk2_LAynDdp0_mn5HZZjXDM_Z0L66KbJL7GWvANm0uV1ZkGl2apLesoO3br; __utma=164006624.1322084484.1457454873.1475288289.1475290368.74; __utmz=164006624.1475290368.74.19.utmccn=(referral)|utmcsr=amazon.cn|utmcct=/s/ref=nb_sb_noss_1|utmcmd=referral; __utmv=164006624.rzaixiancom-23; s_fid=043CC390B97FA108-3F9901D1E657F3DB; ubid-acbcn=479-7313174-1981907; session-id-time=2082729601l; session-id=454-8954288-6765618; csm-hit=S57PBDY214XX37KBTK3B+s-S57PBDY214XX37KBTK3B|1475377881458',
    'Connection': 'keep-alive'
}

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s: %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')

def getItem(element):
    element = pyq(element)
    asin = element.attr("data-asin")
    img = element.find("img").attr("src")
    title = element.find("h2").html()
    price = element.find('span.a-size-base.a-color-price.s-price.a-text-bold').html()
    return {
        "title": title,
        "asin": asin,
        "img": img,
        "price": price
    }

def getTotalPage(pq):
    total = pq('.pagnRA').prev().html()
    if total:
        try:
            total = int(total)
        except:
            total = 0
    else:
        total = 0
    return total

def getItems(url):
    logging.info("Begin to fetch {}".format(url))
    r = requests.get(url, headers=HEADERS)
    pq = pyq(r.text)
    items = pq("[id^=result_]").map(lambda index, value: getItem(value))
    total = getTotalPage(pq)
    time.sleep(3)
    logging.info("Finished fetching ({}) for {}".format(len(items), url))
    return items, total

def fetchByKeyword(keyword, conn=None):
    url = "https://www.amazon.cn/s/ref=nb_sb_noss_1?field-keywords={}"
    sql = """
        INSERT INTO items
        (title, asin, img, price, createtime, updatetime)
        VALUES
        (%(title)s, %(asin)s, %(img)s, %(price)s, now(), now())
        ON CONFLICT (asin)
        DO UPDATE SET
        updatetime = now(),
        title = EXCLUDED.title,
        img = EXCLUDED.img,
        price = EXCLUDED.price
    """
    items, total = getItems(url.format(keyword))
    if conn:
        print(conn)
        cursor = conn.cursor()
        sqlInit = """
            CREATE TABLE IF NOT EXISTS items (
                title text NOT NULL,
                asin varchar(10) NOT NULL,
                img text NULL,
                newimg text NULL,
                price text NOT NULL,
                createtime timestamp NOT NULL,
                updatetime timestamp NOT NULL,
                PRIMARY KEY (asin)
            )
        """
        cursor.execute(sqlInit)
        conn.commit()
        cursor.executemany(sql, tuple(items))
        conn.commit()
    if total > 1:
        for page in range(2, total+1):
            url = "https://www.amazon.cn/s/ref=nb_sb_noss_1?field-keywords={}&page={}"
            items, total = getItems(url.format(keyword, page))
            if conn:
                cursor.executemany(sql, tuple(items))
                conn.commit()
