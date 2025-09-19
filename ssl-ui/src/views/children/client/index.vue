<template>
  <div class="client-panel">
    <!-- <h2>作为客户端进行连接</h2> -->
    <!-- 两列布局 -->
    <el-row >
      <el-col :span="12">
        <el-form  label-width="100px" class="client-form">
          <!-- 服务端 IP -->
          <el-form-item label="服务端 IP">
            <el-input v-model="clientConfig.host" placeholder="请输入服务端 IP" />
          </el-form-item>

          <!-- 服务端端口 -->
          <el-form-item label="端口">
            <el-input v-model="clientConfig.port" placeholder="请输入端口" />
          </el-form-item>

          <!-- 建立/断开连接 -->
          <el-form-item>
            <el-button type="primary" @click="connectServer" :disabled="isConnected">建立连接</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="danger" @click="disconnectServer" :disabled="!isConnected">断开连接</el-button>
          </el-form-item>
        </el-form>
      </el-col>
      <!-- 证书信息 -->
      <el-col :span="12">        
        <el-card class="cert-info" shadow="hover">
          <h3>服务端证书信息</h3>
          <el-descriptions border :column="1">
            
            <el-descriptions-item label="有效期">{{ certInfo.validity || '--' }}</el-descriptions-item>
            <el-descriptions-item label="公钥算法">{{ certInfo.publicKeyAlgo || '--' }}</el-descriptions-item>
            <el-descriptions-item label="签名算法">{{ certInfo.signatureAlgo || '--' }}</el-descriptions-item>
            
          </el-descriptions>
        </el-card>
      </el-col>
      
    </el-row>
      <!-- 消息收发 -->
      <el-card class="msg-box" shadow="hover">
        <h3>消息通信</h3>
        
            <el-input
              v-model="sendMsg"
              placeholder="请输入要发送的消息"
              type="textarea"
              :rows="3"
            />
            <div style="margin-top: 10px;">
              <el-button type="success" @click="sendMessage" :disabled="!isConnected">发送</el-button>
            </div>       
          
        
      </el-card>
      
      
    <!-- 日志显示 -->
    <div class="log-container">
      <h3>连接日志</h3>
      
        <el-input
        type="textarea"
        :rows="9"
        v-model="logs"
        readonly
      />      
    </div>
  </div>
</template>

<script>
import { ref,onMounted } from "vue"
import { onActivated, onDeactivated } from "vue";
export default {
  name: "ClientView",
  setup() {
    const clientConfig = ref({
      host: "127.0.0.1",
      port: "8443"
    })

    const isConnected = ref(false)
    const sendMsg = ref("")
    const recvMsg = ref("")
    const logs = ref([])
    const certInfo = ref({
      validity: '',
      publicKeyAlgo: '',
      signatureAlgo: '',
    })

    const connectServer = async () => {
      try {
        const res = await window.pywebview.api.client_connect(clientConfig.value)
        logs.value.push(`[连接成功] ${clientConfig.value.host}:${clientConfig.value.port}\n`)
        certInfo.value = res || { validity: '', publicKeyAlgo: '', signatureAlgo: '' }
        isConnected.value = true
      } catch (err) {
        logs.value.push(`[连接失败] ${err}\n`)
      }
    }

    const disconnectServer = async () => {
      try {
        await window.pywebview.api.client_disconnect()
        logs.value.push("[已断开连接]\n")
        isConnected.value = false
      } catch (err) {
        logs.value.push(`[断开失败] ${err}\n`)
      }
    }

    const sendMessage = async () => {
      if (!sendMsg.value.trim()) return
      try {
        const response = await window.pywebview.api.client_send(sendMsg.value)
        // logs.value.push(`[发送] ${sendMsg.value}`)
        // if (response) logs.value.push(`[收到] ${response}`)
        sendMsg.value = ""
      } catch (err) {
        logs.value.push(`[发送失败] ${err}\n`)
      }
    }
    onMounted(() => {
      window.onNewLog2 = (msg) => {
        try {
          logs.value += String(msg) + "\n";
        } catch (e) {
          // 忽略转码错误
        }
      };
    });
    onActivated(() => {
      console.log("ClientView 被激活（切回来）");
    });

    onDeactivated(() => {
      console.log("ClientView 被切走（但缓存着）");
    });

    return {
      clientConfig,
      isConnected,
      sendMsg,
      recvMsg,
      logs,
      certInfo,
      connectServer,
      disconnectServer,
      sendMessage,
    }
  }
}
</script>

<style scoped>
.client-panel {
  padding: 20px;
}
.client-form {
  margin-top: 10px;
  padding: 10px;
  max-width: 500px;
}
.cert-info {
  margin-top: 20px;
  background: #eef6ff;
  padding: 10px;
  border-radius: 6px;
}
.recv-area {
  margin-top: 10px;
  padding: 10px;
  background: #f7f7f7;
  border-radius: 6px;
}
.recv-content {
  min-height: 40px;
}
.log-container {
  margin-top: 20px;
  background: #f5f5f5;
  border-radius: 6px;
  padding: 10px;
}
.log-line {
  font-size: 14px;
  line-height: 1.6;
  font-family: monospace;
}
.msg-box {
  margin-top: 20px;
}
</style>
