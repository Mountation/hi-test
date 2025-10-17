<template>
  <div>
    <el-card>
      <div slot="header">
        <span>查看评测集</span>
      </div>

      <div style="margin-bottom:12px">
        <el-button @click="$router.push('/datasets/list')">返回列表</el-button>
        <el-button type="success" @click="$router.push('/datasets/create')">创建新评测集</el-button>
      </div>

      <el-table :data="corpora">
        <el-table-column prop="index" label="#" width="60"/>
        <el-table-column prop="content" label="语料内容"/>
        <el-table-column prop="expected_response" label="预期响应"/>
        <el-table-column prop="intent" label="意图"/>
        <el-table-column prop="created_at" label="创建时间"/>
      </el-table>

      <el-pagination v-if="totalPages>1" :current-page.sync="page" :page-size="pageSize" :total="total" @current-change="load"/>
    </el-card>
  </div>
</template>

<script>
import api from '../services/api'
import { ref, onMounted, watch } from 'vue'
export default {
  props: ['id'],
  setup(props) {
    const corpora = ref([])
    const page = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    const totalPages = ref(1)

    async function load(p = 1) {
      const res = await api.get(`/datasets/view/${props.id}/?page=${p}`)
      corpora.value = res.data.corpora || []
      total.value = res.data.total || 0
      page.value = res.data.page || 1
      pageSize.value = res.data.page_size || 20
      totalPages.value = Math.ceil(total.value / pageSize.value)
    }

    onMounted(() => load())

    return { corpora, page, pageSize, total, totalPages, load }
  }
}
</script>