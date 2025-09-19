import { createRouter,createWebHashHistory } from "vue-router";
const router = createRouter({
  mode:"hash",
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes:[
        
    {
      path:"/",
      redirect:"/desktop",
      name:"主容器",
      component:()=> import('@/views/main/index.vue'),
      children:[
        {
          path:"/desktop",
          name:"主页",
          component:()=>import('@/views/children/desktop/index.vue'),
          meta:{
            keepAlive: true, // 组件需要缓存
          }
        },
        {
          path:"/server",
          name:"服务端",
          component: () => import('@/views/children/server/index.vue'),
          meta: {
            keepAlive: true, // 组件需要缓存
          }
        },
        {
          path:"/client",
          name:"客户端",
          component:()=>import('@/views/children/client/index.vue'),
          meta: {
            keepAlive: true, // 组件需要缓存
          }
          
        },
        
        
      ]
    }
  ]
})
export default router
