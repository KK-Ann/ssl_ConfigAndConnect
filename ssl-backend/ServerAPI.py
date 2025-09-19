import ssl
import socket
import threading
# import subprocess
import webview
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
import datetime
import json
class ServerAPI:
    def __init__(self):
        self.server_thread = None
        self.running = False
        self.log = []
        self.cert_file = ""
        self.key_file = ""
        self.port = 8443
        self._window =  None  # <- 私有属性，避免被 pywebview 的 introspection 访问
        self._clients = set()  # 用于跟踪长连接客户端 socket
        self._server_socket = None     # 监听 socket（未 wrap）
        self._wrapped_socket = None    # wrap 后的 ssl socket（用于中断 accept）
    # -------- 日志记录 ----------
    def _log(self, msg):
        print(msg)
        self.log.append(msg)
        # 返回给前端
        # 推送给前端（如果 window 可用）
        try:
            if self._window:
                # 调用前端全局函数 window.onNewLog(msg)
                js = f'window.onNewLog({json.dumps(msg)})'
                # evaluate_js 在不同平台行为有差异，捕获异常避免影响服务
                self._window.evaluate_js(js)
        except Exception:
            pass
        return msg
    def set_window(self, window):
        """从外部注入 webview window，或在 __main__ 中调用 api.set_window(window)"""
        self._window = window
    # -------- 获取日志 ----------
    def get_logs(self):
        return "\n".join(self.log)

    # -------- 生成证书和私钥 ----------
    def generate_certificate(self, options: dict):
        """
        生成自签名证书和私钥
        options = {
            "cert_type": "RSA" | "EC",
            "rsa_bits": 2048,
            "curve": "secp256r1",  # EC 曲线
            "hash_alg": "SHA256",  # SHA256 | SHA384 | SHA512
            "common_name": "localhost",
            "valid_days": 365
        }
        """
        cert_type = options.get("cert_type", "RSA")
        common_name = options.get("common_name", "localhost")
        valid_days = int(options.get("valid_days", 365))
        hash_alg = options.get("hash_alg", "SHA256")

        # ---- 选择哈希算法 ----
        hash_algo_map = {
            "SHA256": hashes.SHA256(),
            "SHA384": hashes.SHA384(),
            "SHA512": hashes.SHA512(),
        }
        hash_algo = hash_algo_map.get(hash_alg, hashes.SHA256())

        # ---- 生成密钥 ----
        if cert_type == "RSA":
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=int(options.get("rsa_bits", 2048))
            )
        elif cert_type == "EC":
            curve_name = options.get("curve", "secp256r1")
            curve_map = {
                "secp256r1": ec.SECP256R1(),
                "secp384r1": ec.SECP384R1(),
                "secp521r1": ec.SECP521R1(),
            }
            key = ec.generate_private_key(
                curve_map.get(curve_name, ec.SECP256R1())
            )
        else:
            raise ValueError("Unsupported cert_type")

        # ---- 构建证书 ----
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"CN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Shanghai"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Shanghai"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MyOrg"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=valid_days))
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName(common_name)]),
                critical=False,
            )
            .sign(private_key=key, algorithm=hash_algo)
        )

        # 在保存 PEM 前确保使用 options 中的路径并记录日志
        self.cert_file = options.get("cert_file", self.cert_file or "./server_cert.crt")
        self.key_file = options.get("key_file", self.key_file or "./server_key.key")

        self._log(f"[INFO] 将证书保存到: {self.cert_file}")
        self._log(f"[INFO] 将私钥保存到: {self.key_file}")

        with open(self.cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        with open(self.key_file, "wb") as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        self._log(f"[INFO] 证书生成完成: {self.cert_file}, {self.key_file}")

        return {
            "cert_file": self.cert_file,
            "key_file": self.key_file,
            "message": f"生成 {cert_type} 证书成功, 有效期 {valid_days} 天"
        }

    def get_available_options(self):
        """返回前端下拉菜单用的选项"""
        return {
            "cert_types": ["RSA", "EC"],
            "rsa_bits": [2048, 3072, 4096],
            "curves": ["secp256r1", "secp384r1", "secp521r1"],
            "hash_algs": ["SHA256", "SHA384", "SHA512"],
        }
    # -------- 启动服务端 ----------
    def start_server(self, port=8443, cert=None, key=None):
        if self.running:
            return self._log("[WARN] 服务端已在运行")

        self.port = port
        self.cert_file = cert or self.cert_file
        self.key_file = key or self.key_file

        if not self.cert_file or not self.key_file:
            return self._log("[ERROR] 请先生成或选择证书和私钥")

        def handle_client(conn, addr):
            """每个客户端的长连接处理器"""
            self._log(f"[INFO] 开始处理客户端长连接: {addr}")
            try:
                # 设置短超时以便能及时响应服务端关闭
                conn.settimeout(1.0)
                while self.running:
                    try:
                        data = conn.recv(4096)
                        if not data:
                            # 客户端关闭连接
                            break
                        try:
                            text = data.decode(errors="ignore")
                        except Exception:
                            text = repr(data)
                        self._log(f"[RECV] {addr} -> {text}")
                        # 简单回显或心跳响应
                        try:
                            conn.sendall(f"服务端收到: {text}".encode("utf-8"))
                        except Exception as e:
                            self._log(f"[ERROR] 发送到客户端失败 {addr}: {e}")
                            break
                    except socket.timeout:
                        # 超时循环，继续检查 self.running
                        continue
                    except OSError:
                        break
            finally:
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    conn.close()
                except Exception:
                    pass
                # 从跟踪集合移除
                try:
                    self._clients.discard(conn)
                except Exception:
                    pass
                self._log(f"[INFO] 客户端已断开: {addr}")

        def run_server():
            try:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.minimum_version = ssl.TLSVersion.TLSv1_3  # 强制 TLS1.3
                context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
                    # 保存原始监听 socket，便于外部 stop 时关闭
                    self._server_socket = sock
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(("0.0.0.0", self.port))
                    sock.listen(5)
                    self._log(f"[INFO] 服务端已启动，监听端口 {self.port} (TLS 1.3)")
                    self.running = True

                    while self.running:
                        try:
                            conn, addr = sock.accept()  # 普通 TCP 连接
                            self._log(f"[INFO] 客户端已连接: {addr}")

                            # 🔑 在这里 wrap 成 SSL socket
                            ssl_conn = context.wrap_socket(conn, server_side=True)

                            self._clients.add(ssl_conn)
                            t = threading.Thread(
                                target=handle_client, args=(ssl_conn, addr), daemon=True
                            )
                            t.start()
                        except socket.timeout:
                            continue
                        except OSError as e:
                            self._log(f"[ERROR] accept 出错: {e}")
                            break
                        except Exception as e:
                            self._log(f"[ERROR] accept 异常: {e}")
                            break
            except Exception as e:
                self._log(f"[ERROR] 服务端启动失败: {e}")
            finally:
                # 主循环退出后，关闭所有客户端连接
                self._log("[INFO] 开始关闭所有客户端连接...")
                for c in list(self._clients):
                    try:
                        c.shutdown(socket.SHUT_RDWR)
                    except Exception:
                        pass
                    try:
                        c.close()
                    except Exception:
                        pass
                self._clients.clear()
                # 清理并置空监听对象引用
                try:
                    if self._wrapped_socket:
                        self._wrapped_socket.close()
                except Exception:
                    pass
                try:
                    if self._server_socket:
                        self._server_socket.close()
                except Exception:
                    pass
                self._wrapped_socket = None
                self._server_socket = None
                self.running = False
                self._log("[INFO] 服务端已停止")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        return "[INFO] 启动命令已发送"
    # -------- 停止服务端 ----------
    def stop_server(self):
        """优雅停止服务：设置 running=False，关闭监听 socket 和所有客户端连接以中断 accept/recv"""
        if not self.running:
            return self._log("[WARN] 服务端未运行")
        # 标记停止，子线程会看到并退出循环
        self.running = False

        # 关闭 wrap 后的 ssl socket（可中断 accept）
        try:
            if self._wrapped_socket:
                try:
                    self._wrapped_socket.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self._wrapped_socket.close()
        except Exception:
            pass

        # 关闭原始监听 socket（备用）
        try:
            if self._server_socket:
                try:
                    self._server_socket.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self._server_socket.close()
        except Exception:
            pass

        # 关闭所有已连接客户端，立即中断它们的 recv 循环
        for c in list(self._clients):
            try:
                c.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                c.close()
            except Exception:
                pass
        self._clients.clear()

        return self._log("[INFO] 服务端正在关闭...")


if __name__ == "__main__":
    api = ServerAPI()
    window = webview.create_window("SSL Server Panel", url="http://localhost:5173", js_api=api)
    api.set_window(window)
    webview.start()
