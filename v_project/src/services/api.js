import axios from 'axios'

const api = axios.create({
  baseURL: '/',
  headers: { 'X-Requested-With': 'XMLHttpRequest' }
})

// Attach CSRF token for same-origin requests
function getCsrf() {
  const el = document.querySelector('[name=csrfmiddlewaretoken]')
  return el ? el.value : null
}

api.interceptors.request.use(config => {
  const csrf = getCsrf()
  if (csrf && (!config.headers['X-CSRFToken'])) {
    config.headers['X-CSRFToken'] = csrf
  }
  return config
})

export default api
