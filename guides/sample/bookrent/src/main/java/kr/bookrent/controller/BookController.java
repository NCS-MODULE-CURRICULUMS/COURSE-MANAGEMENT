package kr.bookrent.controller;

import java.io.IOException;
import java.sql.SQLException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import kr.bookrent.dao.BookDAO;

/**
 * 도서 조회 · 등록 · 수정 · 삭제.
 *
 * 조회는 doGet, 나머지는 doPost 가 받는다.
 */
public class BookController extends HttpServlet {

    private static final long serialVersionUID = 1L;
    private final BookDAO bookDAO = new BookDAO();

    /** 조회 — 키워드가 있으면 키워드 조회, 없으면 전체 조회. */
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse res)
            throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");
        String keyword = req.getParameter("keyword");

        try {
            if (keyword != null && keyword.trim().length() > 0) {
                req.setAttribute("books", bookDAO.findByKeyword(keyword.trim()));
                req.setAttribute("keyword", keyword.trim());
            } else {
                req.setAttribute("books", bookDAO.findAll());
            }
        } catch (SQLException e) {
            throw new ServletException("도서 목록을 읽지 못했습니다", e);
        }
        req.getRequestDispatcher("/book/list.jsp").forward(req, res);
    }

    /** 등록 · 수정 · 삭제. */
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse res)
            throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");
        String action = req.getParameter("action");

        try {
            if ("delete".equals(action)) {
                bookDAO.delete(Integer.parseInt(req.getParameter("id")));
            } else if ("update".equals(action)) {
                bookDAO.update(Integer.parseInt(req.getParameter("id")),
                               req.getParameter("title"),
                               req.getParameter("author"),
                               req.getParameter("publisher"));
            } else {
                bookDAO.insert(req.getParameter("title"),
                               req.getParameter("author"),
                               req.getParameter("publisher"));
            }
        } catch (SQLException e) {
            throw new ServletException("도서를 처리하지 못했습니다", e);
        }
        res.sendRedirect(req.getContextPath() + "/books");
    }
}
