import configparser
import logging
import pymysql
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

# 连接数据库
logger = logging.getLogger(__name__)
logger.info('连接数据库')

db_config = {
    'host': config['database']['host'],
    'user': config['database']['user'],
    'password': config['database']['password'],
    'database': config['database']['database']
}
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

# 发送邮件
def send_email(subject, body):
    logger.info('发送邮件')
    smtp_host = config['email']['smtp_host']
    smtp_port = config['email']['smtp_port']
    smtp_username = config['email']['smtp_username']
    smtp_password = config['email']['smtp_password']
    sender = config['email']['sender']
    recipients = config['email']['recipients'].split(',')

    msg = MIMEText(body)
    msg['Subject'] = f"{subject} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(msg)

# 初始化已发送的告警集合
sent_alerts = set()

# 发送告警
while True:
    # 查询证件表
    query = "SELECT name, expiry FROM document"
    logger.info('执行数据库查询')
    cursor.execute(query)
    certificates = cursor.fetchall()

    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime('%H:%M')
    target_time = '00:00'

    # 检查是否到达新的一天，并清空已发送告警集合
    if current_time == target_time:
        sent_alerts = set()
        logger.info('初始化已发送的告警集合')

    for certificate in certificates:
        name = certificate[0]
        expiry = certificate[1]

        # 判断是否超过有效期当天
        if expiry <= current_datetime.date():
            # 判断是否在告警时间范围内
            for alert_time in config['alert_times']:
                if current_time == datetime.datetime.strptime(config['alert_times'][alert_time], '%H:%M').strftime('%H:%M'):
                    # 判断是否已经发送过告警
                    if (alert_time, name) not in sent_alerts:
                        # 发送告警邮件
                        subject = f"证件 {name} 已过期！"
                        body = f"证件 {name} 已过期，请及时处理！"
                        send_email(subject, body)
                        # 添加到已发送告警集合
                        sent_alerts.add((alert_time, name))
                        logging.info(f"已发送证书过期警报：{name}")

        # 判断是否需要发送告警
        for alert_day in config['alert_days']:
            alert_date = expiry - datetime.timedelta(days=int(config['alert_days'][alert_day]))
            if alert_date == current_datetime.date():
                # 判断是否在告警时间范围内
                for alert_time in config['alert_times']:
                    if current_time == datetime.datetime.strptime(config['alert_times'][alert_time], '%H:%M').strftime('%H:%M'):
                        # 判断是否已经发送过告警
                        if (alert_time, name) not in sent_alerts:
                            # 发送告警邮件
                            subject = f"证件 {name} 即将过期！"
                            body = f"证件 {name} 即将在 {config['alert_days'][alert_day]} 天后过期，请注意！"
                            send_email(subject, body)
                            # 添加到已发送告警集合
                            sent_alerts.add((alert_time, name))
                            logging.info(f"已发送证书过期警报：{name}")

    time.sleep(20)
