# 使用Nginx作为基础镜像
FROM nginx:1.25.1

# 将前端页面文件复制到Nginx的默认网站目录
COPY index.html /usr/share/nginx/html/

# 复制CSS和JS文件到Nginx的assets目录
COPY assets /usr/share/nginx/html/assets

# 暴露Nginx的默认HTTP端口
EXPOSE 80
