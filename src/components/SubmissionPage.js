import React from 'react';
import { Link } from 'react-router-dom';

function SubmissionPage() {
  return (
    <div className="full-page submission-page">
      <div>
        <div className="header">
          <h2>Hệ thống nộp bài báo khoa học</h2>
          <div className="icons">
            <span>🔊</span>
            <span>🛡️</span>
            <span>⏻</span>
          </div>
        </div>

        <div className="form-grid">
          <div className="form-group">
            <label>Nhập tiêu đề đề</label>
            <input type="text" placeholder="Tiêu đề" />
          </div>
          <div className="form-group">
            <label>Nhập vào abstract</label>
            <input type="text" placeholder="Abstract" />
          </div>
          <div className="form-group">
            <label>Nhập vào từ khóa</label>
            <input type="text" placeholder="Từ khóa" />
          </div>
        </div>

        <div className="placeholder-grid">
          <div className="placeholder-box"></div>
          <div className="placeholder-box"></div>
          <div className="placeholder-box"></div>
          <div className="placeholder-box"></div>
        </div>
      </div>

      <div>
        <div className="sources-title">NGUỒN DỮ LIỆU</div>
        <div className="logos">
          <img src="/openalex.png" alt="OpenAlex" className="logo-img" />
          <img src="/scopus.png" alt="Scopus" className="logo-img" />
          <img src="/springer.png" alt="Springer" className="logo-img" />
          <img src="/crossref.png" alt="Crossref" className="logo-img" />
        </div>

        <div className="footer">
          <div>
            <strong>TUYÊN BỐ MIỄN TRỪ TRÁCH NHIỆM</strong>
            Các giới hạn pháp lý được cung cấp bởi hệ thống này dựa trên các thuật toán tự động...
          </div>
          <div>
            <strong>MÃ NGUỒN</strong>
            Dự án là mã nguồn mở, nếu muốn thêm tính năng vui lòng đóng góp...
          </div>
          <div>
            <strong>CẢM KẾT BẢO MẬT NGẦN GỌN</strong>
            Sự tôn trọng quyền riêng tư của bạn là ưu tiên của chúng tôi...
          </div>
        </div>

        {/* Nút quay lại trang tìm kiếm (tuỳ chọn) */}
        <Link to="/" style={{ position: 'absolute', top: '30px', left: '30px', fontSize: '28px' }}>
          ←
        </Link>
      </div>
    </div>
  );
}

export default SubmissionPage;