package kr.bookrent.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import kr.bookrent.model.Book;
import kr.bookrent.util.DBConnection;

/** 도서 표(books)를 읽고 쓴다. */
public class BookDAO {

    /** 전체 조회. */
    public List<Book> findAll() throws SQLException {
        String sql = "SELECT id, title, author, publisher FROM books ORDER BY id";

        Connection c = null;
        PreparedStatement ps = null;
        ResultSet rs = null;
        try {
            c = DBConnection.get();
            ps = c.prepareStatement(sql);
            rs = ps.executeQuery();
            return read(rs);
        } finally {
            close(rs, ps, c);
        }
    }

    /** 키워드 조회 — 제목이나 지은이에 그 글자가 들어가는 것. */
    public List<Book> findByKeyword(String keyword) throws SQLException {
        String sql = "SELECT id, title, author, publisher FROM books "
                   + " WHERE title LIKE ? OR author LIKE ? ORDER BY id";

        Connection c = null;
        PreparedStatement ps = null;
        ResultSet rs = null;
        try {
            c = DBConnection.get();
            ps = c.prepareStatement(sql);
            ps.setString(1, "%" + keyword + "%");
            ps.setString(2, "%" + keyword + "%");
            rs = ps.executeQuery();
            return read(rs);
        } finally {
            close(rs, ps, c);
        }
    }

    public void insert(String title, String author, String publisher) throws SQLException {
        String sql = "INSERT INTO books (title, author, publisher) VALUES (?, ?, ?)";

        Connection c = null;
        PreparedStatement ps = null;
        try {
            c = DBConnection.get();
            ps = c.prepareStatement(sql);
            ps.setString(1, title);
            ps.setString(2, author);
            ps.setString(3, publisher);
            ps.executeUpdate();
        } finally {
            close(null, ps, c);
        }
    }

    public void update(int id, String title, String author, String publisher)
            throws SQLException {
        String sql = "UPDATE books SET title = ?, author = ?, publisher = ? WHERE id = ?";

        Connection c = null;
        PreparedStatement ps = null;
        try {
            c = DBConnection.get();
            ps = c.prepareStatement(sql);
            ps.setString(1, title);
            ps.setString(2, author);
            ps.setString(3, publisher);
            ps.setInt(4, id);
            ps.executeUpdate();
        } finally {
            close(null, ps, c);
        }
    }

    public void delete(int id) throws SQLException {
        String sql = "DELETE FROM books WHERE id = ?";

        Connection c = null;
        PreparedStatement ps = null;
        try {
            c = DBConnection.get();
            ps = c.prepareStatement(sql);
            ps.setInt(1, id);
            ps.executeUpdate();
        } finally {
            close(null, ps, c);
        }
    }

    private List<Book> read(ResultSet rs) throws SQLException {
        List<Book> list = new ArrayList<Book>();
        while (rs.next()) {
            Book b = new Book();
            b.setId(rs.getInt("id"));
            b.setTitle(rs.getString("title"));
            b.setAuthor(rs.getString("author"));
            b.setPublisher(rs.getString("publisher"));
            list.add(b);
        }
        return list;
    }

    private void close(ResultSet rs, PreparedStatement ps, Connection c) {
        try { if (rs != null) rs.close(); } catch (SQLException ignored) { }
        try { if (ps != null) ps.close(); } catch (SQLException ignored) { }
        try { if (c != null) c.close(); } catch (SQLException ignored) { }
    }
}
