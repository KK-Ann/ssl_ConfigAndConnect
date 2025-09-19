
### 核心功能

选择是作为ssl的服务端或者客户端

- **服务端部分**
    
    - 选择证书 (`.crt`) 和私钥 (`.key`) 文件。
        
    - 输入监听端口（如 8443）。
        
    - 启动/停止 SSL 服务端。
        
    - 显示连接日志（谁连上了，收到了什么数据）。

        
- **客户端部分**
    
    - 输入服务端 IP 和端口。
        
    - 选择证书（如果需要验证）。
        
    - 建立 SSL 连接。
        
    - 发送消息、接收消息。
    

## 技术栈

vue+pywebview
界面借鉴：https://github.com/typsusan/flow-system
## 安装部署


### 必需组件
下载npcap: https://npcap.com/#download

### 运行方式
1. 直接运行: 双击ids.exe
2. 源码运行:   
   - 安装依赖: 
```bash
pip install \-r requirements.txt
# 激活虚拟环境: 
venv\\Scripts\\activate

3. 运行: 
```bash
   
   python statrt.py # (桌面模式)
```
4. 打包:
```bash
pyinstaller main.spec
```

