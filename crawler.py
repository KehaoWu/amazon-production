import psycopg2
from libs.amazon import fetchByKeyword
from libs.config import config

conn = psycopg2.connect(
    database = config.get("database", "database"),
    user = config.get("database", "user"),
    password = config.get("database", "password"),
    host = config.get("database", "host"),
    port = config.get("database", "port")
    )


with open('keywords.txt') as fp:
    words = fp.readlines()

for word in words:
    word = word.strip()
    fetchByKeyword(keyword = word, conn = conn)
