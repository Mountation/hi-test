<template>
  <div>
    <el-card>
      <div slot="header">
        <span>评测集列表</span>
      </div>
      <el-table :data="datasets" style="width:100%">
        <el-table-column prop="name" label="名称"/>
        <el-table-column prop="description" label="描述"/>
        <el-table-column prop="corpora_count" label="语料数量"/>
        <el-table-column prop="created_at" label="创建时间"/>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button type="info" size="small" @click="view(row.id)">查看</el-button>
            <el-button type="danger" size="small" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog title="确认删除" :visible.sync="deleteDialogVisible">
      <span>确定要删除评测集 "{{ deleteTarget?.name }}" 吗？此操作不可恢复。</span>
      <template #footer>
        <el-button @click="deleteDialogVisible=false">取消</el-button>
        <el-button type="danger" @click="deleteDataset">确认删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '../services/api'
import { ref, onMounted } from 'vue'
export default {
  setup() {
    const datasets = ref([])
    const deleteDialogVisible = ref(false)
    const deleteTarget = ref(null)

    onMounted(async () => {
      await load()
    })

    async function load() {
      const res = await api.get('/datasets/');
      datasets.value = res.data || []
    }

    function view(id) {
      router.push(`/datasets/view/${id}`)
    }

    function confirmDelete(row) {
      deleteTarget.value = row
      deleteDialogVisible.value = true
    }

    async function deleteDataset() {
      if (!deleteTarget.value) return
      try {
        const res = await api.post(`/datasets/delete/${deleteTarget.value.id}/`)
        if (res.data.status === 'success') {
          deleteDialogVisible.value = false
          await load()
        }
      } catch (e) { console.error(e) }
    }

    return { datasets, deleteDialogVisible, deleteTarget, confirmDelete, deleteDataset }
  }
}
</script>