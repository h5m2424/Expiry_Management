# 使用Python的官方镜像作为基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到容器的工作目录中
COPY . /app

# 安装依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 运行API
ENTRYPOINT ["bash", "entrypoint.sh"]
