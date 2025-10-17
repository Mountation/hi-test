<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="8" v-for="card in stats" :key="card.label">
        <el-card class="stat-card">
          <div class="stat-number">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="mt-4">
      <div slot="header">
        <span>评测集概览</span>
      </div>
      <el-table :data="evaluationSets" style="width:100%">
        <el-table-column prop="name" label="评测集名称"/>
        <el-table-column prop="corpora_count" label="语料数量"/>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag type="success" v-if="row.status==='active'">活跃</el-tag>
            <el-tag type="info" v-else>非活跃</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间"/>
        <el-table-column label="最近运行">
          <template #default="{ row }">
            <el-tag v-if="row.latest_run">{{ row.latest_run.version }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import api from '../services/api'
import { ref, onMounted } from 'vue'
export default {
  setup() {
    const stats = ref([
      { label: '评测集数量', value: 0 },
      { label: '语料总数', value: 0 },
      { label: '近期运行', value: 0 }
    ])

    const evaluationSets = ref([])

    onMounted(async () => {
      try {
        const res = await api.get('/');
        if (res && res.data) {
          // assume backend home view returns JSON when requested by fetch
          // if backend doesn't, these calls may need explicit endpoints
          stats.value[0].value = res.data.evaluation_sets_count || 0
          stats.value[1].value = res.data.total_corpora || 0
          stats.value[2].value = (res.data.recent_runs || []).length
          evaluationSets.value = res.data.evaluation_sets || []
        }
      } catch (e) {
        console.error(e)
      }
    })

    return { stats, evaluationSets }
  }
}
</script>

<style>
.stat-card { text-align:center; padding:20px }
.stat-number { font-size:2rem; color:#1E90FF }
</style>