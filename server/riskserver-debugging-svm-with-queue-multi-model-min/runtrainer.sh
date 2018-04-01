# 更新数据库重启worker
export PATH=$PWD/bin:$PATH
python manage.py rqworker trainer


