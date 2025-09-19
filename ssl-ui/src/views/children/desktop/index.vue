<template>
<div class="desktop-main">
  <div class="desktop-main-title">
    <h2>欢迎来到ssl连接系统</h2>
  </div>

  <div class="desktop-main-mid">

    <div class="desktop-card" style="margin-right: 30px;">
      <img src="~@/assets/main/desk.webp" width="315" height="200">
      <div class="desktop-card__content">
        <p class="desktop-card__title">SSL/TSL已经成为信息安全的重要基础协议
        </p>
        <p class="desktop-card__description">可以用此将主机作为客户端或服务端进行基于TLS1.3的连接，并对证书公钥进行配置管理~</p>
      </div>
    </div>

    

  </div>

  <div class="desktop-main-title">
    <h2>你可以~</h2>
  </div>

  <div class="desktop-main-bottom">
    <div class="desktop-main-bottom-item">
      <img src="~@/assets/desktop/jiqr.svg">
      <p>作为服务端</p>
    </div>

    <div class="desktop-main-bottom-item">
      <img src="~@/assets/desktop/fwl.svg">
      <p>作为客户端</p>
    </div>
  </div>

</div>
</template>

<script setup>
// export default {
//   name: "index"
// }
function beforeRouteLeave(to,from,next){
    to.meta.keepAlive = true
    next(0)
  }
</script>

<style scoped>
.desktop-main{
  width: 100%;
  height: 100%;
  user-select: none;
  -webkit-app-region: no-drag;
}
.desktop-main-title{
  width: auto;
  height: 100px;
  line-height: 100px;
  margin-left: 30px;
}
.desktop-main-mid{
  width: auto;
  height: 200px;
  margin-left: 30px;
}

.desktop-main-bottom{
  width: auto;
  height: 100px;
  margin-left: 30px;
}

.desktop-main-bottom-item{
  width: 180px;
  height: 70px;
  border: 1px solid #eeeeee;
  border-radius: 10px;
  margin-right: 38px;
  color: #666666;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
  cursor: pointer;
  float: left;
}

.desktop-main-bottom-item img{
  width: 20px;
  height: 20px;
  margin-right: 10px;
}

.desktop-card {
  position: relative;
  width: 315px;
  height: 200px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: all 0.6s cubic-bezier(0.23, 1, 0.320, 1);
  float: left;
}

.desktop-card svg {
  width: 48px;
  fill: #333;
  transition: all 0.6s cubic-bezier(0.23, 1, 0.320, 1);
}

.desktop-card:hover {
  transform: rotate(-5deg) scale(1.1);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.desktop-card__content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-45deg);
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  background-color: #fff;
  opacity: 0;
  transition: all 0.6s cubic-bezier(0.23, 1, 0.320, 1);
}

.desktop-card:hover .desktop-card__content {
  transform: translate(-50%, -50%) rotate(0deg);
  opacity: 1;
}

.desktop-card__title {
  margin: 0;
  font-size: 24px;
  color: #333;
  font-weight: 700;
}

.desktop-card__description {
  margin: 10px 0 0;
  font-size: 14px;
  color: #777;
  line-height: 1.4;
}

.desktop-card:hover svg {
  scale: 0;
  transform: rotate(-45deg);
}


</style>
