#!/bin/bash

# 等待数据库完全启动
sleep 60

# 启动 expiry_alert
python expiry_alert.py
