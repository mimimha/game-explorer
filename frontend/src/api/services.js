// src/api/services.js
// ──────────────────────────────────────────────────────────────
// endpoints.js + index.js(axios) 를 묶어 "바로 호출하는 함수" 모음.
// 컴포넌트/스토어에서:
//   import { gameAPI } from '@/api/services'
//   const { data } = await gameAPI.list({ genre: 3, q: 'pixel' })
// ──────────────────────────────────────────────────────────────
import api from './client'
import E from './endpoints'

// ── 인증 ──
export const authAPI = {
  register: (payload) => api.post(E.auth.register, payload),  // {username,email,nickname,password1,password2,birth_date?}
  login: (payload) => api.post(E.auth.login, payload),        // {email, password}
  logout: () => api.post(E.auth.logout),
}

// ── 회원 ──
export const accountAPI = {
  getMe: () => api.get(E.accounts.me),
  updateMe: (payload) => api.patch(E.accounts.me, payload),   // {nickname?, birth_date?, profile_img?}
  deleteMe: () => api.delete(E.accounts.me),
  getMyMedals: () => api.get(E.accounts.medals),
  getMypage: () => api.get(E.accounts.mypage),
  getUserProfile: (userId) => api.get(E.accounts.userProfile(userId)),
  follow: (userId) => api.post(E.accounts.follow(userId)),
  unfollow: (userId) => api.delete(E.accounts.follow(userId)),
  getFollowers: (userId) => api.get(E.accounts.followers(userId)),
  getFollowing: (userId) => api.get(E.accounts.following(userId)),
}

// ── 게임 ──
export const gameAPI = {
  // params: { genre, platform, price_lte, is_korean, offline, ordering, q, page }
  list: (params) => api.get(E.games.list, { params }),
  detail: (gameId) => api.get(E.games.detail(gameId)),
  videos: (gameId) => api.get(E.games.videos(gameId)),
  posts: (gameId) => api.get(E.games.posts(gameId)),
  recommended: () => api.get(E.games.recommended),
  onSale: () => api.get(E.games.onSale),
  newReleases: () => api.get(E.games.newReleases),
  filterOptions: () => api.get(E.games.filterOptions),
  suggest: (q) => api.get(E.games.suggest, { params: { q } }),
  genres: () => api.get(E.games.genres),
}

// ── 찜 ──
export const wishlistAPI = {
  list: () => api.get(E.wishlist.list),
  add: (gameId) => api.post(E.wishlist.toggle(gameId)),
  remove: (gameId) => api.delete(E.wishlist.toggle(gameId)),
}

// ── 커뮤니티 ──
export const communityAPI = {
  getPosts: (params) => api.get(E.community.posts, { params }),  // params: { category, q, page }
  createPost: (payload) => api.post(E.community.posts, payload), // {title, content, category, game_id?}
  getPost: (postId) => api.get(E.community.postDetail(postId)),
  updatePost: (postId, payload) => api.patch(E.community.postDetail(postId), payload),
  deletePost: (postId) => api.delete(E.community.postDetail(postId)),
  getComments: (postId) => api.get(E.community.comments(postId)),
  createComment: (postId, payload) => api.post(E.community.comments(postId), payload), // {content}
  updateComment: (commentId, payload) => api.patch(E.community.commentDetail(commentId), payload),
  deleteComment: (commentId) => api.delete(E.community.commentDetail(commentId)),
  uploadImages: (postId, files) => {
    const fd = new FormData()
    files.forEach(f => fd.append('images', f))
    return api.post(E.community.postImages(postId), fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  deleteImage: (postId, imageId) => api.delete(E.community.postImageDetail(postId, imageId)),
}

// ── AI 추천 ──
export const recommendAPI = {
  create: (payload) => api.post(E.recommend.create, payload),  // {prompt_input}
  logs: () => api.get(E.recommend.logs),
  logDetail: (logId) => api.get(E.recommend.logDetail(logId)),
  logDelete: (logId) => api.delete(E.recommend.logDelete(logId)),
}

// ── 알림 ──
export const notificationAPI = {
  list: () => api.get(E.notifications.list),
  count: () => api.get(E.notifications.count),
  readAll: () => api.post(E.notifications.readAll),
  read: (id) => api.patch(E.notifications.read(id)),
  delete: (id) => api.delete(E.notifications.delete(id)),
}