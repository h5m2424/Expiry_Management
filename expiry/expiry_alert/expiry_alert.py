import configparser
import pymysql
import logging
import datetime
import smtplib
import time
from email.mime.text import MIMEText

# 加载配置文件
config = configparser.ConfigParser()
config.read('config/config.ini')

# 配置日志
log_path = config['logging']['log_path']
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 获取当前日期和时间
current_datetime = datetime.datetime.now()

# 连接数据库
db_config = {
    'host': config['database']['host'],
    'user': config['database']['user'],
    'password': config['database']['password'],
    'database': config['database']['database']
}
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

# 查询证件表
query = "SELECT name, expiry FROM document"
cursor.execute(query)
certificates = cursor.fetchall()

# 发送邮件
def send_email(subject, body):
    smtp_host = config['email']['smtp_host']
    smtp_port = config['email']['smtp_port']
    smtp_username = config['email']['smtp_username']
    smtp_password = config['email']['smtp_password']
    sender = config['email']['sender']
    recipients = config['email']['recipients'].split(',')

    msg = MIMEText(body)
    msg['Subject'] = f"{subject} - {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(msg)

# 记录上一次发送告警的时间和已发送告警列表
last_alert_time = None
sent_alerts = []

while True:
    # 获取当前日期和时间
    current_datetime = datetime.datetime.now()

    # 发送告警
    for certificate in certificates:
        name = certificate[0]
        expiry = certificate[1]

        # 判断是否超过有效期当天
        if expiry <= current_datetime.date():
            # 判断是否在告警时间范围内
            for alert_time in config['alert_times']:
                if current_datetime.time() >= datetime.datetime.strptime(config['alert_times'][alert_time], '%H:%M').time():
                    # 判断是否已经发送过告警
                    if (alert_time, name) not in sent_alerts:
                        # 发送告警邮件
                        subject = f"证件 {name} 已过期！"
                        body = f"证件 {name} 已过期，请及时处理！"
                        send_email(subject, body)
                        # 更新上一次发送告警的时间和已发送告警列表
                        last_alert_time = current_datetime
                        sent_alerts.append((alert_time, name))
                        logging.info(f"Sent expiration alert for certificate {name}")

        # 判断是否需要发送告警
        for alert_day in config['alert_days']:
            alert_date = expiry - datetime.timedelta(days=int(config['alert_days'][alert_day]))
            if alert_date == current_datetime.date():
                # 判断是否在告警时间范围内
                for alert_time in config['alert_times']:
                    if current_datetime.time() >= datetime.datetime.strptime(config['alert_times'][alert_time], '%H:%M').time():
                        # 判断是否已经发送过告警
                        if (alert_time, name) not in sent_alerts:
                            # 发送告警邮件
                            subject = f"证件 {name} 即将过期！"
                            body = f"证件 {name} 即将在 {config['alert_days'][alert_day]} 天后过期，请注意！"
                            send_email(subject, body)
                            # 更新上一次发送告警的时间和已发送告警列表
                            last_alert_time = current_datetime
                            sent_alerts.append((alert_time, name))
                            logging.info(f"Sent expiration alert for certificate {name}")

    # 检查是否到达下一个告警时间点，并清空已发送告警列表
    if last_alert_time is not None:
        next_alert_time = last_alert_time + datetime.timedelta(hours=1)
        if current_datetime >= next_alert_time:
            sent_alerts = []
            logging.info("Cleared sent alerts")

    time.sleep(10)

