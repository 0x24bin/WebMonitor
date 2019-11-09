# WebMonitor
网站监控


主要作用：
定时对rule.json文件内对网站进行轮询访问
对需要访问对网站主页保存html 并将访问页面截图保存
将网站内容与历史记录进行比对，将比对结果邮件发送发送邮箱

各个脚本主要功能

config.ini     配置文件
config.py     读取配置文件
log.py         日志记录
Notification.py   邮件通知
read_DB.py      写sqlite db程序
RequestsHeader.py   设置请求header
rule.json          需要监控对网站主页列表
webmonitor.py  主入口程序
WebpageShot.py  网页截图
