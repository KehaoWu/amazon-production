#!/bin/base

mkdir -p pg95
pushd pg95
wget https://ftp.postgresql.org/pub/source/v9.5.4/postgresql-9.5.4.tar.gz
tar -xzvf postgresql-9.5.4.tar.gz
pushd postgresql-9.5.4
./configure --prefix=$(dirname $PWD) --without-readline
make
make install
popd
$PWD/bin/initdb -D $PWD/data --auth-local trust --username $USER

echo "
port = 5563
wal_level = hot_standby  # 这个是设置主为wal的主机
max_wal_senders = 32 # 这个设置了可以最多有几个流复制连接，差不多有几个从，就设置几个
wal_keep_segments = 256 # 设置流复制保留的最多的xlog数目
wal_sender_timeout = 60s # 设置流复制主机发送数据的超时时间
max_connections = 100 # 这个设置要注意下，从库的max_connections必须要大于主库的
" >> $PWD/data/postgresql.conf

echo "
host    replication             $USER             121.43.97.117/0                 trust
" >> $PWD/data/pg_hba.conf
echo "
If you want to stop postgresql:
  pkill -f postgresql -9
"
