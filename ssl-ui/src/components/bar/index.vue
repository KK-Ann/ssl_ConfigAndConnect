<template>
  <div class="title-bar" :style="{width:expandState?'':'510px'}">

    <div class="title-bar-left" :style="{backgroundColor:expandState?'rgba(221, 228, 234,0.9)':'#fff'}">
      <img src="~@/assets/bar/logo.svg" alt="图标" class="icon" />
      <div class="title">ssl连接系统</div>
    </div>

    <div class="title-bar-right">
      <div class="operating-button close-button" @click="closeWindow">
        <img src="~@/assets/bar/close.svg" />
      </div>
      <div class="operating-button minimum-button" @click="minimumWindow">
        <img src="~@/assets/bar/minimum.svg" />
      </div>
      <div v-if="expandState" class="operating-button expand-button" @click="expandWindow">
        <img src="~@/assets/bar/expand.svg" />
      </div>
      <div style="width: 10px;"></div>
    </div>


  </div>
</template>


<script>
export default {
  name: "TitleBar",
  data(){
    return{
      expandState:false,
    }
  },
  mounted() {
    this.expandState = !(this.$route.path === "/" || this.$route.path === '/login');
  },
  methods: {
    async closeWindow() {
      // pywebview: prefer calling python API if available
      try {
        
        await window.pywebview.api.close_window();
        return;
        
      } catch (e) {}
      // // Electron fallback
      // if (window.ipcRenderer && typeof window.ipcRenderer.send === "function") {
      //   window.ipcRenderer.send("close");
      //   return;
      // }
      // // Browser fallback
      // if (typeof window.close === "function") {
      //   window.close();
      // }
    },

    async minimumWindow() {
      try {
        if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.minimize_window === "function") {
          await window.pywebview.api.minimize_window();
          return;
        }
      } catch (e) {}
      // if (window.ipcRenderer && typeof window.ipcRenderer.send === "function") {
      //   window.ipcRenderer.send("minimizing");
      //   return;
      // }
      // // no-op in plain browser
    },

    async expandWindow() {
      const payload = {
        screenWidth: window.screen?.width || 0,
        screenHeight: window.screen?.height || 0,
      };
      try {
        if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.expand_window === "function") {
          await window.pywebview.api.expand_window(payload);
          return;
        }
      } catch (e) {}
      // if (window.ipcRenderer && typeof window.ipcRenderer.send === "function") {
      //   window.ipcRenderer.send("expandWindow", payload);
      //   return;
      // }
      // // browser: try fullscreen
      // try {
      //   const el = document.documentElement;
      //   if (el.requestFullscreen) await el.requestFullscreen();
      // } catch (e) {}
    },
  },
};
</script>

<style scoped>
@import "./index.css";
</style>
