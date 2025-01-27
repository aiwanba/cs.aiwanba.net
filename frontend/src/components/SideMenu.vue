<template>
  <el-menu
    :default-active="activeMenu"
    class="side-menu"
    @select="handleSelect"
    background-color="#f8f9fa"
    text-color="#2c3e50">
    
    <el-menu-item index="dashboard">
      <el-icon><menu /></el-icon>
      <span>仪表盘</span>
    </el-menu-item>
    
    <el-sub-menu index="company">
      <template #title>
        <el-icon><office-building /></el-icon>
        <span>公司管理</span>
      </template>
      <el-menu-item index="company-list">公司列表</el-menu-item>
      <el-menu-item index="company-create">创建公司</el-menu-item>
    </el-sub-menu>
    
    <el-sub-menu index="stock">
      <template #title>
        <el-icon><trend-charts /></el-icon>
        <span>股票交易</span>
      </template>
      <el-menu-item index="stock-market">交易市场</el-menu-item>
      <el-menu-item index="stock-orders">我的订单</el-menu-item>
      <el-menu-item index="stock-positions">持仓管理</el-menu-item>
    </el-sub-menu>
    
    <el-sub-menu index="bank">
      <template #title>
        <el-icon><money /></el-icon>
        <span>银行业务</span>
      </template>
      <el-menu-item index="bank-accounts">账户管理</el-menu-item>
      <el-menu-item index="bank-transfer">转账汇款</el-menu-item>
      <el-menu-item index="bank-loan">贷款服务</el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'SideMenu',
  setup() {
    const router = useRouter()
    const activeMenu = ref('dashboard')
    
    const handleSelect = (index) => {
      switch (index) {
        case 'dashboard':
          router.push('/dashboard')
          break
        case 'company-list':
          router.push('/company/list')
          break
        case 'company-create':
          router.push('/company/create')
          break
        case 'stock-market':
          router.push('/stock/market')
          break
        case 'stock-orders':
          router.push('/stock/orders')
          break
        case 'stock-positions':
          router.push('/stock/positions')
          break
        case 'bank-accounts':
          router.push('/bank/accounts')
          break
        case 'bank-transfer':
          router.push('/bank/transfer')
          break
        case 'bank-loan':
          router.push('/bank/loan')
          break
      }
    }
    
    return {
      activeMenu,
      handleSelect
    }
  }
}
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