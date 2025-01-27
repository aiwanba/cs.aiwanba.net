<template>
  <el-menu
    :default-active="activeMenu"
    class="side-menu"
    router>
    <el-menu-item index="/dashboard">
      <el-icon><Odometer /></el-icon>
      <span>仪表盘</span>
    </el-menu-item>
    
    <el-sub-menu index="/company">
      <template #title>
        <el-icon><OfficeBuilding /></el-icon>
        <span>公司管理</span>
      </template>
      <el-menu-item index="/company/list">公司列表</el-menu-item>
      <el-menu-item index="/company/create">创建公司</el-menu-item>
    </el-sub-menu>
    
    <el-sub-menu index="/stock">
      <template #title>
        <el-icon><TrendCharts /></el-icon>
        <span>股票交易</span>
      </template>
      <el-menu-item index="/stock/market">市场行情</el-menu-item>
      <el-menu-item index="/stock/positions">我的持仓</el-menu-item>
      <el-menu-item index="/stock/orders">交易订单</el-menu-item>
    </el-sub-menu>
    
    <el-sub-menu index="/bank">
      <template #title>
        <el-icon><Money /></el-icon>
        <span>银行业务</span>
      </template>
      <el-menu-item index="/bank/accounts">账户管理</el-menu-item>
      <el-menu-item index="/bank/loan">贷款业务</el-menu-item>
      <el-menu-item index="/bank/transfer">转账汇款</el-menu-item>
    </el-sub-menu>
    
    <el-menu-item index="/settings">
      <el-icon><Setting /></el-icon>
      <span>系统设置</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Odometer,
  Office as OfficeBuilding,
  TrendCharts,
  Money,
  Setting
} from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.side-menu {
  height: 100%;
  border-right: none;
}

.el-menu-item, .el-sub-menu {
  font-size: 14px;
}
</style> 