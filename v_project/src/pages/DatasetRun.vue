<template>
  <div>
    <el-card>
      <div slot="header">运行评测集</div>
      <el-form label-width="120px">
        <el-form-item label="API 密钥">
          <el-input v-model="apiKey" type="password"/>
        </el-form-item>
      </el-form>

      <el-table :data="datasets" style="width:100%">
        <el-table-column type="selection" width="55"/>
        <el-table-column prop="name" label="评测集名称"/>
        <el-table-column prop="corpora_count" label="语料数量"/>
        <el-table-column prop="top_intents" label="意图">
          <template #default="{ row }">
            <el-tag v-for="(i,idx) in (row.top_intents || [])" :key="idx" size="small">{{ i }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center">
        <div>已选择 {{ selected.length }} 个评测集</div>
        <el-button type="primary" @click="run" :disabled="selected.length===0">开始测试</el-button>
      </div>
    </el-card>

    <el-card v-if="running" class="mt-4">
      <div>进度</div>
      <el-progress :percentage="progress" :status="progressStatus"/>
      <div style="margin-top:8px">
        <el-button type="danger" @click="cancel">取消运行</el-button>
      </div>
    </el-card>

    <div v-for="result in results" :key="result.run_id" class="mt-4">
      <el-card>
        <div slot="header">
          <span>{{ result.evaluation_set_name }} ({{ result.corpus_count }} 条)</span>
          <el-button type="success" size="small" @click="exportResult(result.run_id)">导出Excel</el-button>
        </div>
        <el-table :data="result.data">
          <el-table-column prop="content" label="语料内容"/>
          <el-table-column prop="expected_response" label="预期响应"/>
          <el-table-column prop="actual_response" label="实际响应"/>
          <el-table-column prop="score" label="评分"/>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script>
import api from '../services/api'
import { ref, onMounted } from 'vue'
import XLSX from 'xlsx'

export default {
  setup() {
    const datasets = ref([])
    const selected = ref([])
    const apiKey = ref('')

    const running = ref(false)
    const progress = ref(0)
    const progressStatus = ref('active')

    const results = ref([])

    onMounted(async () => {
      const res = await api.get('/datasets/')
      datasets.value = res.data || []
    })

    function run() {
      if (!apiKey.value) return alert('请输入API密钥')
      if (selected.value.length === 0) return alert('请选择评测集')

      const form = new FormData()
      form.append('api_key', apiKey.value)
      selected.value.forEach(id => form.append('evaluation_sets', id))

      running.value = true
      progress.value = 0

      api.post('/run_evaluation/', form).then(res => {
        if (res.data.status === 'success') {
          const runIds = res.data.run_ids || [res.data.run_id]
          // poll status
          poll(runIds)
        } else { alert(res.data.message) }
      }).catch(e => { console.error(e); alert('提交失败') })
    }

    function poll(runIds) {
      const interval = setInterval(async () => {
        const statuses = await Promise.all(runIds.map(id => api.get(`/evaluation/status/?run_id=${id}`)))
        // aggregate
        let total = 0, processed = 0
        statuses.forEach(r => {
          if (r.data.status === 'processing') {
            total += r.data.total || 0
            processed += r.data.processed || 0
          }
          if (r.data.status === 'completed') {
            // add to results
            results.value.push({ run_id: r.data.run_id, ...r.data })
          }
        })
        progress.value = total>0 ? Math.round((processed/total)*100) : 0
        if (results.value.length === runIds.length) {
          running.value = false
          clearInterval(interval)
        }
      }, 1000)
    }

    function cancel() {
      api.post('/evaluation/cancel/', `run_id=${results[0]?.run_id || ''}`, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
        .then(res => { alert(res.data.message); running.value = false })
    }

    function exportResult(runId) {
      const result = results.value.find(r => r.run_id === runId)
      if (!result) return
      const ws = XLSX.utils.json_to_sheet(result.data)
      const wb = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, '结果')
      XLSX.writeFile(wb, `评测结果_${runId}.xlsx`)
    }

    return { datasets, selected, apiKey, run, running, progress, poll, results, exportResult, cancel }
  }
}
</script>