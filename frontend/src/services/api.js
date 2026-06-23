import { gameAPI } from '@/api/services'

const TYPE_MAP = {
  recommendation: () => gameAPI.recommended(),
  discount: () => gameAPI.onSale(),
  new: () => gameAPI.newReleases(),
}

export async function fetchGames(type = 'new') {
  const call = TYPE_MAP[type] ?? TYPE_MAP.new
  const { data } = await call()
  return Array.isArray(data) ? data : (data.results ?? [])
}
