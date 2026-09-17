package kr.bookrent.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * 데이터베이스 연결을 얻는 곳.
 *
 * 접속 정보를 한 곳에 모아 둔다. 운영 서버가 바뀌면 이 파일만 고치면 된다.
 */
public class DBConnection {

    private static final String DRIVER = "com.mysql.cj.jdbc.Driver";

    /** db-a 가 데이터베이스 서버의 이름, 3306 이 MySQL 의 포트다. */
    private static final String URL =
            "jdbc:mysql://db-a:3306/bookrent?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Seoul";

    private static final String USER = "root";
    private static final String PASSWORD = "bookrent";

    static {
        try {
            Class.forName(DRIVER);
        } catch (ClassNotFoundException e) {
            throw new IllegalStateException("JDBC 드라이버를 찾을 수 없습니다", e);
        }
    }

    public static Connection get() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }

    private DBConnection() {
    }
}
