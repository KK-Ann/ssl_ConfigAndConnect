<template>
  <div class="payment-main">
    

    <!-- 证书和私钥配置 -->
    <el-row style="margin-left: 20px;">
      
        <el-form label-width="120px">
          <el-form-item label="没有证书？">
            <!-- <el-button type="warning" @click="generateCert">
              生成证书和私钥
            </el-button> -->
            
              <el-button  class="action-button" @click="openDialog">
                生成证书和私钥
              </el-button>
            
          </el-form-item>
          <el-form-item label="证书文件 (.crt)">
            <el-upload
              action=""
              :auto-upload="false"
              :on-change="handleCertChange"
              accept=".crt"
            >
              <el-button class="action-button" >
                选择证书
              </el-button>
              <span v-if="serverConfig.certName" style="margin-left: 10px;">
                {{ serverConfig.certName }}
              </span>
            </el-upload>
          </el-form-item>

          <el-form-item label="私钥文件 (.key)">
            <el-upload
              action=""
              :auto-upload="false"
              :on-change="handleKeyChange"
              accept=".key"
            >
              <el-button class="action-button" >选择私钥</el-button>
              <span v-if="serverConfig.keyName" style="margin-left: 10px;">
                {{ serverConfig.keyName }}
              </span>
            </el-upload>
          </el-form-item>

          <el-form-item label="监听端口">
            <el-input
              v-model="serverConfig.port"
              placeholder="默认 8443"
              style="width: 200px;"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="success" @click="startServer" :disabled="serverRunning">
              启动服务端
            </el-button>
            <el-button type="danger" @click="stopServer" :disabled="!serverRunning">
              停止服务端
            </el-button>
          </el-form-item>
        </el-form>

      
    </el-row>
     <!-- 弹出框 -->
    <el-dialog
      title="生成证书"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form label-width="120px">
        <el-form-item label="证书类型">
          <el-select v-model="form.cert_type" placeholder="选择类型">
            <el-option v-for="t in options.cert_types" :key="t" :label="t" :value="t"/>
          </el-select>
        </el-form-item>

        <el-form-item v-if="form.cert_type === 'RSA'" label="RSA 位数">
          <el-select v-model="form.rsa_bits">
            <el-option v-for="bits in options.rsa_bits" :key="bits" :label="bits" :value="bits"/>
          </el-select>
        </el-form-item>

        <el-form-item v-if="form.cert_type === 'EC'" label="椭圆曲线">
          <el-select v-model="form.curve">
            <el-option v-for="c in options.curves" :key="c" :label="c" :value="c"/>
          </el-select>
        </el-form-item>

        <el-form-item label="签名算法">
          <el-select v-model="form.hash_alg">
            <el-option v-for="h in options.hash_algs" :key="h" :label="h" :value="h"/>
          </el-select>
        </el-form-item>

        <el-form-item label="通用名 (CN)">
          <el-input v-model="form.common_name" placeholder="如: localhost"/>
        </el-form-item>

        <el-form-item label="有效期 (天)">
          <el-input-number v-model="form.valid_days" :min="1" :max="3650"/>
        </el-form-item>
      
        
        <el-form-item label="证书保存路径">
          <el-input v-model="form.cert_file" placeholder="如: ./server_cert.pem"/>
        </el-form-item>

        
        <el-form-item label="私钥保存路径">
          <el-input v-model="form.key_file" placeholder="如: ./server_key.pem"/>
        </el-form-item>
      </el-form>
      <!-- 弹框按钮 -->
      <template #footer>
        <el-button class="action-button"@click="dialogVisible = false">取消</el-button>
        <el-button type="success" @click="generateCert">生成</el-button>
      </template>
    </el-dialog>
     
    <!-- 连接日志 -->
    <div style="margin: 20px;">
      <h3>连接日志</h3>
      <el-input
        type="textarea"
        :rows="10"
        v-model="serverLog"
        readonly
      />
    </div>
  </div>
</template>
<script>
import { ref, onMounted } from "vue";
import { ElMessage, ElNotification } from "element-plus";

import { onActivated, onDeactivated } from "vue";
export default {
  name: "ServerView",
  setup() {
    const dialogVisible = ref(false);
    const result = ref(null);

    const options = {
      cert_types: ["RSA", "EC"],
      rsa_bits: [2048, 3072, 4096],
      curves: ["secp256r1", "secp384r1", "secp521r1"],
      hash_algs: ["SHA256", "SHA384", "SHA512"]
    };

    const form = ref({
      cert_type: "RSA",
      rsa_bits: 2048,
      curve: "secp256r1",
      hash_alg: "SHA256",
      common_name: "localhost",
      valid_days: 365,
      key_file: "./server_key.key",
      cert_file: "./server_cert.crt"
    });

    const serverConfig = ref({
      certName: "",
      keyName: "",
      port: "8443"
    });

    const serverRunning = ref(false);
    const serverLog = ref("等待启动...\n");

    function openDialog() {
      dialogVisible.value = true;
    }

    async function generateCert() {
      try {
        const res = await window.pywebview.api.generate_certificate(form.value);
        result.value = res;
        // 更新表单路径
        form.value.cert_file = res.cert_file || form.value.cert_file;
        form.value.key_file = res.key_file || form.value.key_file;
        serverConfig.value.certName = res.cert_file ? res.cert_file.split("/").pop() : serverConfig.value.certName;
        serverConfig.value.keyName = res.key_file ? res.key_file.split("/").pop() : serverConfig.value.keyName;

        ElMessage.success(res.message);
        dialogVisible.value = false;
        ElNotification({
          title: "证书生成成功 🎉",
          message: `提示: ${res.message}\n证书: ${res.cert_file}\n私钥: ${res.key_file}`,
          type: "success",
          duration: 4500
        });
      } catch (err) {
        ElMessage.error("生成证书失败: " + err);
      }
    }

    const handleCertChange = (file) => {
      serverConfig.value.certName = file.name;
      serverLog.value += `[INFO] 已选择证书: ${file.name}\n`;
    };

    const handleKeyChange = (file) => {
      serverConfig.value.keyName = file.name;
      serverLog.value += `[INFO] 已选择私钥: ${file.name}\n`;
    };

    async function startServer() {
      const certPath = form.value.cert_file;
      const keyPath = form.value.key_file;
      const port = parseInt(serverConfig.value.port) || 8443;

      if (!certPath || !keyPath) {
        serverLog.value += "[ERROR] 请先生成或填写证书/私钥保存路径！\n";
        return;
      }

      try {
        const res = await window.pywebview.api.start_server(port, certPath, keyPath);
        serverRunning.value = true;
        serverLog.value += `[INFO] 后端响应: ${res}\n`;
      } catch (err) {
        serverLog.value += `[ERROR] 启动失败: ${err}\n`;
      }
    }

    async function stopServer() {
      try {
        const res = await window.pywebview.api.stop_server();
        serverRunning.value = false;
        serverLog.value += `[INFO] 后端响应: ${res}\n`;
      } catch (err) {
        serverLog.value += `[ERROR] 停止失败: ${err}\n`;
      }
    }

    onMounted(() => {
      window.onNewLog = (msg) => {
        try {
          serverLog.value += String(msg) + "\n";
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
      dialogVisible,
      result,
      options,
      form,
      serverConfig,
      serverRunning,
      serverLog,
      openDialog,
      generateCert,
      handleCertChange,
      handleKeyChange,
      startServer,
      stopServer
    };
  }
};
</script>


<style scoped>


.desktop-main-title{
  width: auto;
  height: 100px;
  line-height: 100px;
  margin-left: 30px;
}
.action-button {
  background-color: #6558d3;
  border-radius: 6px;
  color: #fff;
  font-weight: 500;
  
  text-align: center;
  border: 0;
  outline: 0;

  padding: 0.625em 0.75em;
  text-decoration: none;
  cursor: pointer;
}

.action-button:hover,
.action-button:focus {
  background-color: #4133B7;
}

</style>
