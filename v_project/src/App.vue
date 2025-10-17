<template>
  <el-container style="height:100vh">
    <el-aside width="240px" class="sidebar">
      <div class="sidebar-header">
        <h3 style="color:white">AI评测系统</h3>
      </div>
      <el-menu :default-active="activeRoute" router class="el-menu-vertical-demo" background-color="#2c3e50" text-color="#fff" active-text-color="#1E90FF">
        <el-menu-item index="/">概述</el-menu-item>
        <el-submenu index="/datasets">
          <template #title>评测集</template>
          <el-menu-item index="/datasets/list">评测集列表</el-menu-item>
          <el-menu-item index="/datasets/create">创建评测集</el-menu-item>
          <el-menu-item index="/datasets/run">运行评测集</el-menu-item>
        </el-submenu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header style="background:linear-gradient(90deg,#1E90FF,#87CEFA); color:white;">
        <div style="font-size:1.2rem">AI评测系统 (前端)</div>
      </el-header>
      <el-main style="padding:20px; overflow:auto">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  setup() {
    const route = useRoute()
    const activeRoute = computed(() => route.path)
    return { activeRoute }
  }
}
</script>

<style>
html,body,#app { height:100%; margin:0 }
.sidebar { background: linear-gradient(180deg,#2c3e50,#1a2530); padding:10px }
.sidebar-header { padding:20px 10px }
</style>