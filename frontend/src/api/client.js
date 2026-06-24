// src/api/index.js
// ──────────────────────────────────────────────────────────────
// axios 인스턴스 + 토큰 인터셉터.
// baseURL 은 .env 의 VITE_API_BASE_URL 한 곳에서만 관리한다.
//   .env.development → VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
//   .env.production  → VITE_API_BASE_URL=https://api.도메인.com/api/v1
// ──────────────────────────────────────────────────────────────
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  // 배열 파라미터를 genre=1&genre=2 형태로 (Django getlist 호환)
  paramsSerializer: { indexes: null },
})

// 요청마다 토큰 자동 첨부 (localStorage 또는 Pinia store 에서 가져옴)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  // FormData 전송 시 Content-Type을 제거해야 axios가
  // multipart/form-data; boundary=... 를 자동으로 설정한다.
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

// 401(인증 만료) 공통 처리
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default api