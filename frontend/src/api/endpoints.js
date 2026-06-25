// ═══════════════════════════════════════════════════════════════════
// 백엔드 urls.py 에 등록된 모든 엔드포인트 모음 (프론트 연결용)
//
// - baseURL(http://127.0.0.1:8000/api/v1)은 axios 인스턴스에서 붙으므로
//   여기 경로들은 전부 그 뒤에 이어붙는 부분만 적는다.
// - 고정 경로 → 문자열 / {id} 들어가는 경로 → 함수
// - 각 줄 끝 주석 = HTTP 메서드 + 토큰 필요 여부(🔒=토큰 필요)
// ═══════════════════════════════════════════════════════════════════

const ENDPOINTS = {
  // ── 인증 (dj-rest-auth) ──────────────────────────────────────────
  auth: {
    register: '/auth/registration/',   // POST            회원가입
    login: '/auth/login/',             // POST            로그인
    logout: '/auth/logout/',           // POST   🔒       로그아웃
  },

  // ── 회원 (accounts) ──────────────────────────────────────────────
  accounts: {
    me: '/accounts/me/',               // GET·PATCH·DELETE 🔒  내 프로필 조회·수정·탈퇴
    medals: '/accounts/me/medals/',    // GET    🔒       내 획득 메달
    mypage: '/accounts/mypage/',       // GET    🔒       마이페이지 집계
    userProfile: (userId) => `/accounts/users/${userId}/`,    // GET            특정 유저 프로필
    follow: (userId) => `/accounts/users/${userId}/follow/`,      // POST·DELETE 🔒 팔로우 토글
    followers: (userId) => `/accounts/users/${userId}/followers/`, // GET 팔로워 목록
    following: (userId) => `/accounts/users/${userId}/following/`, // GET 팔로잉 목록
  },

  // ── 게임 (games) ─────────────────────────────────────────────────
  games: {
    list: '/games/',                       // GET            목록(필터·정렬·검색)
    detail: (gameId) => `/games/${gameId}/`,       // GET            상세
    posts: (gameId) => `/games/${gameId}/posts/`,  // GET            게임 관련 글
    recommended: '/games/recommended/',    // GET            오늘의 추천(홈01)
    onSale: '/games/on-sale/',             // GET            할인 중(홈02)
    newReleases: '/games/new-releases/',   // GET            최근 출시(홈03)
    filterOptions: '/games/filter-options/', // GET          실데이터 기반 필터 옵션
    suggest: '/games/suggest/',             // GET ?q=      제목 자동완성
    genres: '/genres/',                    // GET            분류 목록
  },

  // ── 찜 (wishlists) ───────────────────────────────────────────────
  wishlist: {
    list: '/wishlist/',                    // GET    🔒       내 찜 목록
    toggle: (gameId) => `/games/${gameId}/wishlist/`,  // POST·DELETE 🔒 찜 추가/해제
  },

  // ── 커뮤니티 (community) ─────────────────────────────────────────
  community: {
    posts: '/posts/',                                   // GET / POST 🔒  글 목록·작성
    postDetail: (postId) => `/posts/${postId}/`,        // GET / PATCH·DELETE 🔒 글 상세·수정·삭제
    comments: (postId) => `/posts/${postId}/comments/`, // GET / POST 🔒  댓글 목록·작성
    commentDetail: (commentId) => `/comments/${commentId}/`, // PATCH·DELETE 🔒 댓글 수정·삭제
    postImages: (postId) => `/posts/${postId}/images/`,      // POST 🔒  이미지 업로드
    postImageDetail: (postId, imageId) => `/posts/${postId}/images/${imageId}/`, // DELETE 🔒  이미지 삭제
  },

  // ── AI 추천 (recommendations) ────────────────────────────────────
  recommend: {
    create: '/recommend/',                 // POST   🔒       추천 받기
    logs: '/recommend/logs/',              // GET    🔒       최근 추천 기록
    logDetail: (logId) => `/recommend/logs/${logId}/`, // GET 🔒  추천 기록 상세
    logDelete: (logId) => `/recommend/logs/${logId}/delete/`, // DELETE 🔒  추천 기록 삭제
  },

  // ── 알림 (notifications) ─────────────────────────────────────────
  notifications: {
    list: '/accounts/notifications/',                              // GET    🔒  알림 목록
    count: '/accounts/notifications/count/',                       // GET    🔒  읽지 않은 수
    readAll: '/accounts/notifications/read-all/',                  // POST   🔒  전체 읽음
    read: (id) => `/accounts/notifications/${id}/read/`,          // PATCH  🔒  단건 읽음
    delete: (id) => `/accounts/notifications/${id}/`,             // DELETE 🔒  단건 삭제
  },
}

export default ENDPOINTS