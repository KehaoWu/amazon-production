import json
import psycopg2
from flask import Flask, request
from flask_cors import CORS
from libs.config import config

app = Flask('Amazon')

conn = psycopg2.connect(
    database = config.get("database", "database"),
    user = config.get("database", "user"),
    password = config.get("database", "password"),
    host = config.get("database", "host"),
    port = config.get("database", "port")
    )


@app.route('/getitem', methods=['POST', 'GET'])
def process():
    url = "https://www.amazon.cn/gp/product/{0}/ref=as_li_qf_sp_asin_tl?ie=UTF8&camp=536&creative=3200&creativeASIN={0}&linkCode=as2&tag=rzaixiancom-23"
    sql = """
        SELECT title,asin,img,price FROM items ORDER BY RANDOM() LIMIT 1;
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    r = cursor.fetchone()
    if r:
        final_result = {
            "success": True,
            "data": {
                "title": r[0],
                "url": url.format(r[1]),
                "img": r[2],
                "price": r[3]
            }
        }
    else:
        final_result = {
            "success": False
        }

    final_result = json.dumps(final_result, indent=4, ensure_ascii=False)
    return app.make_response((final_result, 200, {'Content-Type': 'application/json;charset=utf-8'}))


if __name__ == '__main__':
    from libs.config import config
    port = int(config.get("server", "port"))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
