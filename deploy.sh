#!/bin/bash  
echo "拉取最新代码..." 
git pull  
echo "重新构建并启动服务..." 
nerdctl compose up -d --build  
echo "部署完成"

