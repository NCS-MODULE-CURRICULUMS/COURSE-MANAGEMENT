<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>도서 목록 — 도서 관리 시스템</title>
  <style>
    body{font-family:"Malgun Gothic",sans-serif;margin:40px;line-height:1.7}
    h1{font-size:20px;border-bottom:2px solid #000;padding-bottom:8px}
    h2{font-size:16px;margin-top:28px}
    table{border-collapse:collapse;margin:16px 0}
    th,td{border:1px solid #999;padding:6px 12px;font-size:14px}
    th{background:#f2f2f2}
    form{display:inline}
  </style>
</head>
<body>

<h1>도서 목록</h1>

<!-- 키워드 조회 -->
<form method="get" action="books">
  <input type="text" name="keyword" value="${keyword}" placeholder="제목 또는 지은이">
  <button type="submit">검색</button>
  <a href="books">전체 보기</a>
</form>

<table>
  <tr><th>번호</th><th>제목</th><th>지은이</th><th>펴낸곳</th><th>수정</th><th>삭제</th></tr>
  <c:forEach var="b" items="${books}">
    <tr>
      <td>${b.id}</td>
      <td>${b.title}</td>
      <td>${b.author}</td>
      <td>${b.publisher}</td>
      <td>
        <form method="post" action="books">
          <input type="hidden" name="action" value="update">
          <input type="hidden" name="id" value="${b.id}">
          <input type="text" name="title" value="${b.title}" size="10">
          <input type="text" name="author" value="${b.author}" size="6">
          <input type="text" name="publisher" value="${b.publisher}" size="6">
          <button type="submit">수정</button>
        </form>
      </td>
      <td>
        <form method="post" action="books">
          <input type="hidden" name="action" value="delete">
          <input type="hidden" name="id" value="${b.id}">
          <button type="submit">삭제</button>
        </form>
      </td>
    </tr>
  </c:forEach>
</table>

<h2>도서 등록</h2>
<form method="post" action="books">
  <input type="text" name="title" placeholder="제목" required>
  <input type="text" name="author" placeholder="지은이">
  <input type="text" name="publisher" placeholder="펴낸곳">
  <button type="submit">등록</button>
</form>

<p><a href="<%= request.getContextPath() %>/">처음으로</a></p>

</body>
</html>
