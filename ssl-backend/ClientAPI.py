import ssl
import socket
import threading
import json
import webview
from cryptography import x509
from cryptography.hazmat.backends import default_backend


class ClientAPI:
    def __init__(self):
        self.log = []
        self.sock = None
        self.ssl_sock = None

        self._window = None
        self.connected = False
        self.recv_thread = None
        self.recv_callback = None
    def _log(self, msg):
        print(msg)
        self.log.append(msg)
        # 返回给前端
        # 推送给前端（如果 window 可用）
        try:
            if self._window:
                # 调用前端全局函数 window.onNewLog(msg)
                js = f'window.onNewLog2({json.dumps(msg)})'
                # evaluate_js 在不同平台行为有差异，捕获异常避免影响服务
                self._window.evaluate_js(js)
        except Exception:
            pass
        return msg
    def get_logs(self):
        return "\n".join(self.log)
    def set_window(self, window):
        """从外部注入 webview window，或在 __main__ 中调用 api.set_window(window)"""
        self._window = window
    def client_connect(self, config):
        """
        建立 TLS 连接并返回服务端证书信息
        config: {"host": "127.0.0.1", "port": "8443"}
        """
        host = config["host"]
        port = int(config["port"])

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            # context = ssl.create_default_context()# 默认严格验证（使用系统受信任 CA）
            raw_sock = socket.create_connection((host, port))
            self.ssl_sock = context.wrap_socket(raw_sock, server_hostname=host)

            # 获取服务端证书
            cert_bin = self.ssl_sock.getpeercert(True)
            cert = x509.load_der_x509_certificate(cert_bin, default_backend())

            # 使用带时区的 UTC 属性，避免 CryptographyDeprecationWarning
            not_before = getattr(cert, "not_valid_before_utc", cert.not_valid_before)
            not_after = getattr(cert, "not_valid_after_utc", cert.not_valid_after)
            cert_info = {
                "validity": f"{not_before.isoformat()} - {not_after.isoformat()}",
                "publicKeyAlgo": cert.public_key().__class__.__name__,
               "signatureAlgo": getattr(cert.signature_algorithm_oid, "_name", str(cert.signature_algorithm_oid)),
            }
            self.connected = True

    
            self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
            self.recv_thread.start()

            return cert_info
        except Exception as e:
            self._log(f"连接失败: {e}")
            raise Exception(f"连接失败: {e}")

    def client_disconnect(self):
        """断开连接"""
        try:
            if self.ssl_sock:
                self.ssl_sock.close()
            self.connected = False
            return True
        except Exception as e:
            self._log(f"断开失败: {e}")
            raise Exception(f"断开失败: {e}")

    def client_send(self, message: str):
        """发送消息并返回服务端响应"""
        if not self.connected or not self.ssl_sock:
            raise Exception("未连接服务器")

        try:
            self.ssl_sock.sendall(message.encode("utf-8"))
            self._log(f"[发送] {message}")
            # data = self.ssl_sock.recv(4096).decode("utf-8")
            # return data
        except Exception as e:
            raise Exception(f"发送失败: {e}")

    def _recv_loop(self):
        """后台监听接收消息（可扩展推送到前端）"""
        while self.connected and self.ssl_sock:
            try:
                addr = self.ssl_sock.getpeername()  # 返回 (ip, port) 元组
                data = self.ssl_sock.recv(4096)
                if not data:
                    break
                msg = data.decode("utf-8")
                self._log(f"[收到消息from{addr}]{msg}")

            except Exception:
                break


if __name__ == "__main__":
    api = ClientAPI()
    window = webview.create_window("TLS Client", url="http://localhost:5173", js_api=api)  # 这里是前端地址
    webview.start()
