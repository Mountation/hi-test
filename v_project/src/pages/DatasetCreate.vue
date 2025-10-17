<template>
  <div>
    <el-card>
      <div slot="header"><span>创建评测集</span></div>
      <el-form :model="form" ref="formRef">
        <el-form-item label="评测集名称" prop="name">
          <el-input v-model="form.name"/>
        </el-form-item>
        <el-form-item label="描述" prop="desc">
          <el-input type="textarea" v-model="form.desc"/>
        </el-form-item>
        <el-form-item label="Excel 文件" prop="file">
          <input type="file" @change="onFileChange" accept=".xlsx,.xls" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submit">创建评测集</el-button>
          <el-button @click="goList">返回列表</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="uploading" class="mt-3">
      <div>上传进度</div>
      <el-progress :percentage="progress"/>
    </el-card>
  </div>
</template>

<script>
import api from '../services/api'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
export default {
  setup() {
    const form = ref({ name: '', desc: '' })
    const file = ref(null)
    const uploading = ref(false)
    const progress = ref(0)

    function onFileChange(e) {
      file.value = e.target.files[0]
    }

    function goList() { router.push('/datasets/list') }

    async function submit() {
      if (!form.value.name) { return alert('请输入名称') }
      if (!file.value) { return alert('请选择文件') }

      const fd = new FormData()
      fd.append('evaluation_set_name', form.value.name)
      fd.append('evaluation_set_desc', form.value.desc)
      fd.append('excel_file', file.value)

      uploading.value = true
      progress.value = 0

      try {
        const res = await api.post('/datasets/create/', fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.lengthComputable) {
              progress.value = Math.round((progressEvent.loaded / progressEvent.total) * 100)
            }
          }
        })
        if (res.data.status === 'success') {
          alert(res.data.message)
          router.push('/datasets/list')
        }
      } catch (e) {
        console.error(e); alert('上传失败')
      } finally {
        uploading.value = false
      }
    }

    return { form, onFileChange, submit, uploading, progress, goList }
  }
}
</script>