<template>
  <el-table :data="rows" border stripe>
    <el-table-column prop="group" label="类别" width="130" />
    <el-table-column prop="key" label="字段" width="120" />
    <el-table-column prop="name" label="名称" width="180" />
    <el-table-column prop="value" label="数值" />
  </el-table>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ data: { type: Object, default: () => ({}) } })
const nameMap = {
  YOUNG: ['力学性能', '杨氏模量'], POISON: ['力学性能', '泊松比'], FRAE2H: ['力学性能', '塑性功转热系数'], FPERV: ['力学性能', '摩擦系数'],
  THRCND: ['热学性能', '热传导系数'], HEATCP: ['热学性能', '比热容'], MASDEN: ['热学性能', '密度'], EXPAND: ['热学性能', '热膨胀系数'], EMSVTY: ['热学性能', '发射率']
}
const rows = computed(() => Object.entries(nameMap).filter(([key]) => props.data[key]).map(([key, [group, name]]) => {
  const item = props.data[key]
  return { group, key, name, value: item.value ?? item.coefficient ?? JSON.stringify(item) }
}))
</script>
