<template>
  <footer class="footer">
    <div class="footer-container">
    <div class="footer-left">
      <h3>방구석 탐험대</h3>
      <p>당신의 취향을 찾아 떠나는 인디 게임 탐험기</p>
      <p>© 2026 취향저격이조. All Rights Reserved.</p>
    </div>

    <div class="footer-center">
      <h4>탐험대 바로가기</h4>
      <ul>
        <li><RouterLink to="/explore">게임 라이브러리</RouterLink></li>
        <li><RouterLink to="/community">커뮤니티</RouterLink></li>
        <li><RouterLink to="/profile">마이페이지</RouterLink></li>
      </ul>
    </div>

    <div class="footer-right">
      <h4>개발 정보</h4>
      <p>팀원: 장민화(FE), 김채원(BE)</p>
      <div class="social-links">
        <a href="https://lab.ssafy.com/als2612/13-pjt" target="_blank">GitHub Repository</a>
      </div>
      <p class="api-credit">Data powered by RAWG API, STEAM API, Youtube API</p>
    </div>
    </div>
    </footer>
      
</template>

<style scoped>
.footer {
  margin-top: 120px;
  background-color: #FFFDF7;
  border-top: 1px solid #D8C4A3;
  font-size: 14px;
  color: #6B5A45;
  font-family: 'Pretendard', sans-serif;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px;

  display: flex;
  justify-content: space-between;
  gap: 64px;
}

/* 왼쪽 */
.footer-left h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #3A2410;
  font-family: 'Pretendard', sans-serif;
}

.footer-left p {
  line-height: 1.6;
  color: #6B5A45;
}

.footer-left p:last-child {
  margin-top: 12px;
  font-size: 13px;
  color: #9e8c78;
}

/* 가운데 / 오른쪽 공통 */
.footer-center h4,
.footer-right h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #3A2410;
  font-family: 'Pretendard', sans-serif;
}

/* 링크 목록 */
.footer-center ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-center li {
  margin-bottom: 8px;
}

.footer-center a {
  color: #6B5A45;
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-center a:hover {
  color: #D97706;
}

/* 오른쪽 */
.footer-right p {
  margin-bottom: 8px;
  color: #6B5A45;
}

.social-links a {
  display: inline-block;
  margin-top: 8px;
  font-weight: 600;
  color: #D97706;
  text-decoration: none;
}

.social-links a:hover {
  text-decoration: underline;
}

.api-credit {
  margin-top: 16px;
  font-size: 12px;
  color: #9e8c78;
}

/* 반응형 */
@media (max-width: 768px) {
  .footer-container {
    flex-direction: column;
    gap: 32px;
  }
}
</style>