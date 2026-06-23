const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

async function request(path, options = {}) {
  const token = localStorage.getItem('access_token')
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  })
  if (!res.ok) throw new Error(`API Error: ${res.status}`)
  if (res.status === 204) return null
  return res.json()
}

export async function fetchGames(type = 'new') {
  // Django 연결 전까지 더미 데이터 반환
  return []
  // 연결 후: return request(`/games/?type=${type}&limit=6`)
}