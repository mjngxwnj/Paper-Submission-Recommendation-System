import React from 'react';
import { Link } from 'react-router-dom';

function SearchPage() {
  return (
    <div className="full-page search-page">
      <div>
        <h1>Tìm Kiếm Bài Báo, Hội Nghị, Nhà Xuất Bản</h1>
        <br />
        <input
          type="text"
          placeholder="Search..."
          className="search-input"
        />
        <div className="suggestion">
          <a href="#">Hỗ trợ tìm kiếm</a>
        </div>
      </div>

      <div></div> {/* Spacer */}

      {/* Nút chuyển sang trang nộp bài */}
      <Link to="/submission">
        <button className="nav-button" title="Chuyển đến trang nộp bài">
          🔍
        </button>
      </Link>
    </div>
  );
}

export default SearchPage;