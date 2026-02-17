from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
import sqlite3
import os
import time


app = Flask(__name__)

active_users = {}  # {ip: last_seen_timestamp}
ONLINE_TIMEOUT = 30000  

@app.before_request
def track_online():
    ip = request.remote_addr
    now = time.time()

    active_users[ip] = now

    expired = []
    for user_ip, last_seen in active_users.items():
        if now - last_seen > ONLINE_TIMEOUT:
            expired.append(user_ip)

    for user_ip in expired:
        del active_users[user_ip]

# ================= DEADLINE CỐ ĐỊNH =================
def lay_2_chu_cuoi(ten):
    parts = ten.strip().split()
    if len(parts) >= 2:
        return parts[-2] + " " + parts[-1]
    return ten

activity_deadlines = {

    # 👉 #NOTE: Sửa thời gian ở đây (giờ Việt Nam)
    # Format: "YYYY-MM-DD HH:MM:SS"

    "Bắt đầu Tháng Thanh niên": "2026-02-20 23:59:09",
    "ĐTN nộp CTTN và MHGP": "2026-02-28 16:59:00",
    "Lớp cảm tình Đoàn (đăng cai)": "2026-02-22 18:59:06",
    "Chuyên đề kỹ năng 'Vững vàng báo cáo - Tự tin lan tỏa tri thức' 1": "2026-02-20 20:59:50",
    "Chuyên đề kỹ năng 'Vững vàng báo cáo - Tự tin lan tỏa tri thức' 2": "2026-03-20 20:59:00",
    "Trắc nghiệm và truyền thông Nghị Quyết 57": "2026-02-19 13:59:00",
    "Tuổi trẻ Địa chất tự hào dưới cờ Đảng 1": "2026-02-20 23:59:40",
    "Tuổi trẻ Địa chất tự hào dưới cờ Đảng 2": "2026-03-19 23:59:00",
    "Giao lưu cầu lông 1": "2026-02-20 14:59:34",
    "Mở chuỗi/ recap/ timeline tổ chức/ set avt...TTN": "2026-02-25 23:59:23",
    "Không gian học nhóm 1": "2026-02-20 20:59:59",
    "Không gian học nhóm 2": "2026-02-22 20:59:00",
    "Góc yêu sách mùa 2 (1)": "2026-02-20 20:59:59",
    "Góc yêu sách mùa 2 (2)": "2026-03-20 20:59:00",
    "Những câu chuyện 'Thời hoa lửa' 1": "2026-02-20 15:59:47",
    "Chủ nhật xanh 1": "2026-02-20 15:59:37",
    "Chủ nhật xanh 2": "2026-03-16 15:59:00",
    "Workshop làm hoa - vòng tay 1": "2026-02-20 14:59:35",
    "Workshop làm hoa - vòng tay 2": "2026-03-16 14:59:00",
    "Giao lưu cầu lông 2": "2026-03-04 18:59:00",
    "Những câu chuyện 'Thời hoa lửa' 2": "2026-02-26 23:59:00",
    "Giao lưu cầu lông 3": "2026-03-08 11:59:00",
    "Quốc tế phụ nữ 8/3": "2026-03-05 23:59:51",
    "Nghị Quyết 59": "2026-02-21 23:59:00",
    "Buổi gặp mặt 'Tiếp lửa truyền thống - Nối tiếp hành trình tuổi trẻ' 1": "2026-02-21 17:59:22",
    "Buổi gặp mặt 'Tiếp lửa truyền thống - Nối tiếp hành trình tuổi trẻ' 2": "2026-03-20 17:59:00",
    "Giao lưu văn nghệ 1": "2026-02-19 23:59:32",
    "Giao lưu văn nghệ 2": "2026-03-15 23:59:00",
    "Những câu chuyện 'Thời hoa lửa' 3": "2026-02-28 23:59:00",
    "Chương trình 'Hành trình thanh niên theo dấu chân về nguồn' 1": "2026-02-21 23:59:28",
    "Chương trình 'Hành trình thanh niên theo dấu chân về nguồn' 2": "2026-03-21 23:59:00",
    "Tổ chức 'Thử thách 7 ngày sống xanh' 1": "2026-02-20 23:59:43",
    "Nghị quyết 66": "2026-02-22 23:59:48",
    "95 năm rực cháy khát vọng tuổi trẻ": "2026-02-22 23:59:21",
    "Tổ chức 'Thử thách 7 ngày sống xanh' 2": "2026-02-21 23:59:00",
    "Những câu chuyện 'Thời hoa lửa' 4": "2026-03-03 23:59:00",
    "Thành lập 2 đội": "2026-02-24 23:59:58",
    "Tổ chức 'Thử thách 7 ngày sống xanh' 3": "2026-02-23 23:59:00",
    "Tổ chức 'Thử thách 7 ngày sống xanh' 4": "2026-03-25 23:59:00",
    "Nghị quyết 68": "2026-02-28 23:59:57",
    "Giao lưu cầu lông 4": "2026-03-20 11:59:00",
    "Ngọn lửa Thanh niên": "2026-02-28 23:59:00",
    "Chào mừng 30 năm thành lập trường": "2026-02-28 23:59:44",
    "Kêu gọi hưởng ứng 'Giờ trái đất'": "2026-02-28 23:59:43",
    "Tổng kết Tháng Thanh Niên": "2026-03-31 23:59:55",
}

app.secret_key = "super-secret-key"
DB = "database.db"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Bảng submissions
    c.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten TEXT,
        thuoc TEXT,
        email TEXT,
        hoat_dong TEXT,
        noi_dung TEXT,
        link_cong_khai TEXT,
        thoi_gian_nop TEXT,
        deadline TEXT,
        ket_qua_deadline TEXT,
        trang_thai TEXT,
        diem REAL,
        nhan_xet TEXT,
        tinh_trang TEXT,
        ten_phoi_hop TEXT,
        vai_tro TEXT,
        loai TEXT,
        can_sua INTEGER DEFAULT 0
    )
    """)

    # Bảng xin dời deadline
    c.execute("""
    CREATE TABLE IF NOT EXISTS extension_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten TEXT,
        email TEXT,
        hoat_dong TEXT,
        noi_dung TEXT,
        so_ngay_xin INTEGER,
        ly_do TEXT,
        trang_thai TEXT,
        so_ngay_duyet INTEGER
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ================= ADMIN ACCOUNTS =================
admins = {
    "admin1": "ttn263",
    "admin2": "456"
}
failed_admin = {}


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]
        ip = request.remote_addr

        if user not in admins or admins[user] != pw:
            failed_admin[ip] = failed_admin.get(ip, 0) + 1

            if failed_admin[ip] >= 2:
                return "Thiết bị này đã bị khóa"

            return "Sai tài khoản"

        session["admin"] = user
        failed_admin[ip] = 0
        return redirect("/admin")

    return """
    <h2>Admin Login</h2>
    <form method="post">
        Username:<br><input name="username"><br>
        Password:<br><input type="password" name="password"><br><br>
        <button type="submit">Login</button>
    </form>
    """

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")

# ================= TRANG NỘP =================
@app.route("/", methods=["GET", "POST"])
def home():

    email = session.get("email")
    thongbao = ""

    if email:
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute("""
            SELECT id, hoat_dong
            FROM submissions
            WHERE email=? AND trang_thai='Đã chấm'
            ORDER BY id DESC
        """, (email,))

        rows = c.fetchall()
        conn.close()

        for i, r in enumerate(rows, start=1):
            thongbao += f"""
            <p style="color:red; font-weight:bold;">
                {i}. <a href="/xem-ket-qua/{r[0]}" style="color:red;">
                {r[1]}
                </a>
            </p>
            """

    if request.method == "POST":

        conn = sqlite3.connect(DB, check_same_thread=False)

        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM submissions WHERE email=?", (request.form["email"],))
        so_lan = c.fetchone()[0] + 1


        thoi_gian_nop = datetime.now()
        hoat_dong = request.form["hoat_dong"]
        noi_dung = request.form["noi_dung"]

        deadline_str = activity_deadlines.get(hoat_dong)

        if deadline_str:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")

            # ===== KIỂM TRA CÓ ĐƯỢC DUYỆT DỜI KHÔNG =====
            conn2 = sqlite3.connect(DB, check_same_thread=False)
            c2 = conn2.cursor()

            email = request.form["email"]

            c2.execute("""
            SELECT so_ngay_duyet FROM extension_requests
            WHERE hoat_dong=? AND noi_dung=? 
            AND email=? 
            AND trang_thai='Đồng ý'
            """, (hoat_dong, noi_dung, email))

            ext = c2.fetchone()
            conn2.close()

            if ext and ext[0]:
                deadline += timedelta(days=ext[0])


            if thoi_gian_nop <= deadline:
                ket_qua = "Đúng hạn"
            else:
                tre = thoi_gian_nop - deadline

                ngay = tre.days
                gio = tre.seconds // 3600
                phut = (tre.seconds % 3600) // 60

                ket_qua = f"Trễ {ngay} ngày {gio} giờ {phut} phút"

        else:
            deadline = None
            ket_qua = "Không có deadline"

        c.execute("""
            INSERT INTO submissions
            (ten,thuoc,email,hoat_dong,noi_dung,link_cong_khai,
             thoi_gian_nop,deadline,ket_qua_deadline,
             trang_thai,tinh_trang,ten_phoi_hop,vai_tro)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            request.form["ten"],
            request.form["thuoc"],
            request.form["email"],
            hoat_dong,
            noi_dung,
            request.form["link_cong_khai"],
            str(thoi_gian_nop),
            str(deadline) if deadline else "",
            ket_qua,
            "Chua cham",
            request.form.get("tinh_trang"),
            request.form.get("ten_phoi_hop"),
            request.form.get("vai_tro")
        ))

        conn.commit()
        conn.close()

        session["email"] = request.form["email"]


        # ====== TÍNH LỜI CHÚC ======
        ten_2 = lay_2_chu_cuoi(request.form["ten"])
        today = datetime.now()
        loi_chuc = ""

        if today <= datetime(2026, 2, 27):

            if so_lan == 1:
                loi_chuc = f"""
                🧧 Mừng Xuân Bính Ngọ 2026, Đoàn khoa Địa chất kính chúc {ten_2} và gia đình an khang thịnh vượng, vạn sự như ý, phú quý song toàn. 🎊
                """

            elif so_lan == 2 and "Đúng hạn" in ket_qua:
                loi_chuc = f"""
                ✨ Gửi {ten_2},
                Đoàn khoa Địa chất trân trọng ghi nhận và chân thành cảm ơn sự tận tâm của bạn khi vẫn hoàn thành công việc trong những ngày Tết bận rộn.  
                Kính chúc bạn và gia đình năm mới thịnh vượng, phát đạt và an khang viên mãn.❤️
                """

            elif "Trễ" in ket_qua:
                loi_chuc = f"""
                ✨ Gửi {ten_2},
                dù tiến độ có đôi chút chậm trễ, Đoàn khoa Địa chất vẫn trân trọng tinh thần trách nhiệm của bạn. 
                Kính chúc bạn và gia đình năm mới thịnh vượng, phát đạt và bình an dài lâu.❤️
                """

            else:
                loi_chuc = f"""
                🎀 Chào đón Xuân Bính Ngọ 2026, Đoàn khoa Địa chất kính chúc {ten_2} và gia đình một năm phát tài, hạnh phúc tròn đầy. 🎉
                """

        return f"""
        <h2 style='text-align:center;'>Nộp thành công!</h2>
        <div style='text-align:center; margin-top:20px;'>
        {loi_chuc}
        </div>
        """

    return """
    <div style="text-align:center; margin-bottom:20px;">
    <div style="font-size:32px; font-weight:bold; color:#8B0000;">
        ĐOÀN KHOA ĐỊA CHẤT
    </div>
    <div style="font-size:18px; color:#8B0000;">
        Trường Đại học Khoa học tự nhiên, ĐHQG - HCM
    </div>
    </div>

    <h2>Nộp bài</h2>
    <form method="post">
        <div style="display:flex; gap:20px;">
            <div>
                Tên:<br>
                <input name="ten">
            </div>

            <div>
                Thuộc:<br>
                <select name="thuoc">
                    <option>Đoàn</option>
                    <option>Hội</option>
                    <option>CLB/Đội/Nhóm/Ban</option>
                    <option>Thanh niên hỗ trợ nhiệt tình (CTV)</option>
                </select>
            </div>
        </div>
        <br>

        Email:<br><input name="email"><br>

        Hoạt động:<br>
        <select name="hoat_dong">
            <option>Bắt đầu Tháng Thanh niên</option>
            <option>ĐTN nộp CTTN và MHGP</option>
            <option>Lớp cảm tình Đoàn (đăng cai)</option>
            <option>Chuyên đề kỹ năng 'Vững vàng báo cáo - Tự tin lan tỏa tri thức' 1</option>
            <option>Chuyên đề kỹ năng 'Vững vàng báo cáo - Tự tin lan tỏa tri thức' 2</option>
            <option>Trắc nghiệm và truyền thông Nghị Quyết 57</option>
            <option>Tuổi trẻ Địa chất tự hào dưới cờ Đảng 1</option>
            <option>Tuổi trẻ Địa chất tự hào dưới cờ Đảng 2</option>
            <option>Giao lưu cầu lông 1</option>
            <option>Mở chuỗi/ recap/ timeline tổ chức/ set avt...TTN</option>
            <option>Không gian học nhóm 1</option>
            <option>Không gian học nhóm 2</option>
            <option>Góc yêu sách mùa 2 (1)</option>
            <option>Góc yêu sách mùa 2 (2)</option>
            <option>Những câu chuyện 'Thời hoa lửa' 1</option>
            <option>Chủ nhật xanh 1</option>
            <option>Chủ nhật xanh 2</option>
            <option>Workshop làm hoa - vòng tay 1</option>
            <option>Workshop làm hoa - vòng tay 2</option>
            <option>Giao lưu cầu lông 2</option>
            <option>Những câu chuyện 'Thời hoa lửa' 2</option>
            <option>Giao lưu cầu lông 3</option>
            <option>Quốc tế phụ nữ 8/3</option>
            <option>Nghị Quyết 59</option>
            <option>Buổi gặp mặt 'Tiếp lửa truyền thống - Nối tiếp hành trình tuổi trẻ' 1</option>
            <option>Buổi gặp mặt 'Tiếp lửa truyền thống - Nối tiếp hành trình tuổi trẻ' 2</option>
            <option>Giao lưu văn nghệ 1</option>
            <option>Giao lưu văn nghệ 2</option>
            <option>Những câu chuyện 'Thời hoa lửa' 3</option>
            <option>Chương trình 'Hành trình thanh niên theo dấu chân về nguồn' 1</option>
            <option>Chương trình 'Hành trình thanh niên theo dấu chân về nguồn' 2</option>
            <option>Tổ chức 'Thử thách 7 ngày sống xanh' 1</option>
            <option>Nghị quyết 66</option>
            <option>95 năm rực cháy khát vọng tuổi trẻ</option>
            <option>Tổ chức 'Thử thách 7 ngày sống xanh' 2</option>
            <option>Những câu chuyện 'Thời hoa lửa' 4</option>
            <option>Thành lập 2 đội</option>
            <option>Tổ chức 'Thử thách 7 ngày sống xanh' 3</option>
            <option>Tổ chức 'Thử thách 7 ngày sống xanh' 4</option>
            <option>Nghị quyết 68</option>
            <option>Giao lưu cầu lông 4</option>
            <option>Ngọn lửa Thanh niên</option>
            <option>Chào mừng 30 năm thành lập trường</option>
            <option>Kêu gọi hưởng ứng 'Giờ trái đất'</option>
            <option>Tổng kết Tháng Thanh Niên</option>
            <option>Khác (ghi tên hoạt động dưới phần điền link)</option>
            <option>Đề xuất, kiến nghị,...(về thành viên không tham gia, về hoạt động,...KÈM MINH CHỨNG) </option>
        </select><br>

        Nội dung:<br>
        <select name="noi_dung">
            <option>Bản kế hoạch</option>
            <option>Biểu mẫu (form, aloha, sheet,...)</option>
            <option>Canva, AI (poster, slide,...)</option>
            <option>Bài truyền thông (caption đăng bài truyền thông hoặc tổng kết)</option>
            <option>Dự trù kinh phí</option>
            <option>Hình ảnh (truyền thông)</option>
            <option>Video</option>
            <option>Kịch bản</option>
            <option>Văn bản gửi mail, tin nhắn,...</option>
            <option>Truyền thông vận động (kêu gọi tham gia, tương tác,...)</option>
            <option>Báo cáo tổng kết trên Masterplan</option>
            <option>Hình ảnh/ video sau chương trình</option>
            <option>Khác (ghi tên nội dung dưới phần điền link)</option>
            <option>Gặp vấn đề, khó khăn, có ý tưởng mới,...</option>
        </select><br>

        Link (công khai):<br><input name="link_cong_khai"><br><br>

         <b>Tình trạng làm việc:</b><br>
         <input type="radio" name="tinh_trang" value="Tu lam" checked> 1 mình tự làm<br>
         <input type="radio" name="tinh_trang" value="Nhieu nguoi"> Nhiều hơn 1 người<br><br>

         <div style="margin-left:30px;">
             Tên phối hợp:
             <input name="ten_phoi_hop">

             &nbsp;&nbsp;&nbsp;

             Vai trò:
             <select name="vai_tro">
                 <option>Chia đều việc</option>
                 <option>Hỗ trợ phần nhỏ dưới 20%</option>
                 <option>-</option>
             </select>
         </div><br><br>

        <button type="submit">Nộp</button>
    

    </form>

    <br>
    <a href="/login">Admin Login</a>

    <br><br>
    <a href="/xin-doi">Xin dời deadline</a>

    <p>
        <a href="/check-deadlines" style="color:blue;">
            👉 Xem thời gian còn lại các hoạt động
        </a>
    </p>
    """


@app.route("/xin-doi", methods=["GET", "POST"])
def xin_doi():

    if request.method == "POST":

        conn = sqlite3.connect(DB, check_same_thread=False)
        c = conn.cursor()

        c.execute("""
            INSERT INTO extension_requests
            (ten,email,hoat_dong,noi_dung,so_ngay_xin,ly_do,trang_thai)
            VALUES (?,?,?,?,?,?,?)
        """, (
            request.form["ten"],
            request.form["email"],
            request.form["hoat_dong"],
            request.form["noi_dung"],
            int(request.form["so_ngay"]),
            request.form["ly_do"],
            "Chờ duyệt"
        ))

        conn.commit()
        conn.close()

        session["email"] = request.form["email"]


        return "Đã gửi yêu cầu xin dời deadline!"

    return """
    <h2>Xin dời deadline</h2>

    <form method="post">

        Họ và tên:<br>
        <input name="ten"><br><br>

        Email:<br>
        <input name="email"><br><br>

        Hoạt động xin dời:<br>
        <select name="hoat_dong">
            <option>Bắt đầu Tháng Thanh niên</option>
            <option>ĐTN nộp CTTN và MHGP</option>
            <option>Lớp cảm tình Đoàn (đăng cai)</option>
            <option>Chuyên đề kỹ năng 'Vững vàng báo cáo - Tự tin lan tỏa tri thức' 1</option>
            <option>Chuyên đề kỹ năng 'Vững vàng báo cáo - Tự tin lan tỏa tri thức' 2</option>
            <option>Trắc nghiệm và truyền thông Nghị Quyết 57</option>
            <option>Tuổi trẻ Địa chất tự hào dưới cờ Đảng 1</option>
            <option>Tuổi trẻ Địa chất tự hào dưới cờ Đảng 2</option>
            <option>Giao lưu cầu lông 1</option>
            <option>Mở chuỗi/ recap/ timeline tổ chức/ set avt...TTN</option>
            <option>Không gian học nhóm 1</option>
            <option>Không gian học nhóm 2</option>
            <option>Góc yêu sách mùa 2 (1)</option>
            <option>Góc yêu sách mùa 2 (2)</option>
            <option>Những câu chuyện 'Thời hoa lửa' 1</option>
            <option>Chủ nhật xanh 1</option>
            <option>Chủ nhật xanh 2</option>
            <option>Workshop làm hoa - vòng tay 1</option>
            <option>Workshop làm hoa - vòng tay 2</option>
            <option>Giao lưu cầu lông 2</option>
            <option>Những câu chuyện 'Thời hoa lửa' 2</option>
            <option>Giao lưu cầu lông 3</option>
            <option>Quốc tế phụ nữ 8/3</option>
            <option>Nghị Quyết 59</option>
            <option>Buổi gặp mặt 'Tiếp lửa truyền thống - Nối tiếp hành trình tuổi trẻ' 1</option>
            <option>Buổi gặp mặt 'Tiếp lửa truyền thống - Nối tiếp hành trình tuổi trẻ' 2</option>
            <option>Giao lưu văn nghệ 1</option>
            <option>Giao lưu văn nghệ 2</option>
            <option>Những câu chuyện 'Thời hoa lửa' 3</option>
            <option>Chương trình 'Hành trình thanh niên theo dấu chân về nguồn' 1</option>
            <option>Chương trình 'Hành trình thanh niên theo dấu chân về nguồn' 2</option>
            <option>Tổ chức 'Thử thách 7 ngày sống xanh' 1</option>
            <option>Nghị quyết 66</option>
            <option>95 năm rực cháy khát vọng tuổi trẻ</option>
            <option>Tổ chức 'Thử thách 7 ngày sống xanh' 2</option>
            <option>Những câu chuyện 'Thời hoa lửa' 4</option>
            <option>Thành lập 2 đội</option>
            <option>Tổ chức 'Thử thách 7 ngày sống xanh' 3</option>
            <option>Tổ chức 'Thử thách 7 ngày sống xanh' 4</option>
            <option>Nghị quyết 68</option>
            <option>Giao lưu cầu lông 4</option>
            <option>Ngọn lửa Thanh niên</option>
            <option>Chào mừng 30 năm thành lập trường</option>
            <option>Kêu gọi hưởng ứng 'Giờ trái đất'</option>
            <option>Tổng kết Tháng Thanh Niên</option>
            <option>Khác (ghi tên hoạt động dưới phần điền lý do)</option>
        </select><br><br>

        Nội dung xin dời:<br>
        <select name="noi_dung">
            <option>Bản kế hoạch</option>
            <option>Biểu mẫu (form, aloha, sheet,...)</option>
            <option>Canva, AI (poster, slide,...)</option>
            <option>Bài truyền thông (caption đăng bài truyền thông hoặc tổng kết)</option>
            <option>Dự trù kinh phí</option>
            <option>Hình ảnh (truyền thông)</option>
            <option>Video</option>
            <option>Kịch bản</option>
            <option>Văn bản gửi mail, tin nhắn,...</option>
            <option>Truyền thông vận động (kêu gọi tham gia, tương tác,...)</option>
            <option>Báo cáo tổng kết trên Masterplan</option>
            <option>Hình ảnh/ video sau chương trình</option>
            <option>Khác (ghi tên nội dung dưới phần điền lý do)</option>
        </select><br><br>

        Số ngày xin dời:<br>
        <select name="so_ngay">
            """ + "".join([f"<option>{i}</option>" for i in range(1,11)]) + """
        </select><br><br>

        Lý do:<br>
        <textarea name="ly_do" rows="4" cols="50"></textarea><br><br>

        <button type="submit">Gửi yêu cầu</button>
    </form>

    <br>
    <a href="/">Quay lại trang nộp</a>
    """

# ================= ADMIN PAGE =================
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/login")

    # LẤY SUBMISSIONS
    conn = sqlite3.connect(DB, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM submissions ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()


    # ====== PHẦN XIN DỜI ======


    table = ""

    for r in rows:

        trang_thai = r[10]   # cột trang_thai

        if trang_thai == "Đã chấm":
            mau_tt = "green"
        else:
            mau_tt = "red"

        table += f"""
        <tr>
            <td>{r[0]}</td>
            <td>{r[1]}</td>
            <td>{r[4]}</td>
            <td>{r[7]}</td>
            <td>{r[9]}</td>
            <td style="color:{mau_tt}; font-weight:bold;">
                {trang_thai}
            </td>
            <td><a href="/detail/{r[0]}">Xem</a></td>
        </tr>
        """


    conn = sqlite3.connect(DB, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM extension_requests")
    ext_rows = c.fetchall()
    conn.close()

    ext_table = ""

    for e in ext_rows:
        trangthai = e[7] if e[7] else ""

        if "Được duyệt" in trangthai:
            mau = "green"
        elif "Không được duyệt" in trangthai:
            mau = "red"
        else:
            mau = "black"

        ext_table += f"""
        <tr>
            <td>{e[0]}</td>
            <td>{e[1]}</td>
            <td>{e[3]}</td>
            <td>{e[4]}</td>
            <td>{e[5]} ngày</td>
            <td style="color:{mau}; font-weight:bold;">
                {trangthai}
            </td>
            <td>
                <form action="/duyet/{e[0]}" method="post">
                    <select name="so_ngay_duyet">
                        {''.join([f"<option value='{i}'>{i}</option>" for i in range(1,11)])}
                    </select>
                    <button name="action" value="dongy">Đồng ý</button>
                    <button name="action" value="khong">Không</button>
                </form>
            </td>
        </tr>
        """


    return f"""
    <h2>Admin Panel ({session['admin']})</h2>
    <h3>👁 Online: {len(active_users)} người</h3>

    <a href="/logout">Logout</a><br><br>

    <table border="1" cellpadding="5">
        <tr>
            <th>ID</th>
            <th>Tên</th>
            <th>Hoạt động</th>
            <th>Thời gian nộp</th>
            <th>Kết quả deadline</th>
            <th>Trạng thái</th>
            <th>Xem</th>
        </tr>
        {table}
    </table>


    <h2>Yêu cầu xin dời deadline</h2>
    <table border="1">
        <tr>
            <th>ID</th>
            <th>Tên</th>
            <th>Hoạt động</th>
            <th>Nội dung</th>
            <th>Xin dời</th>
            <th>Trạng thái</th>
            <th>Duyệt</th>
        </tr>
        {ext_table}
    </table>
    """

@app.route("/detail/<int:id>", methods=["GET", "POST"])
def detail(id):

    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB, check_same_thread=False)
    c = conn.cursor()

    # Nếu admin bấm lưu điểm
    if request.method == "POST":
        try:
            diem_input = request.form["diem"].replace(",", ".")
            diem = float(diem_input)
        except:
            return "Điểm không hợp lệ"

        nhan_xet = request.form["nhan_xet"]

        # Xếp loại tự động
        if diem == 10:
            loai = "Xuất sắc"
        elif diem >= 8:
            loai = "Giỏi"
        elif diem >= 7:
            loai = "Khá"
        elif diem >= 5:
            loai = "Trung bình"
        elif diem >= 3:
            loai = "Yếu"
        else:
            loai = "Kém"

        c.execute("""
        UPDATE submissions
        SET diem=?, nhan_xet=?, loai=?, trang_thai='Đã chấm'
        WHERE id=?
        """, (diem, nhan_xet, loai, id))



        conn.commit()

    c.execute("SELECT * FROM submissions WHERE id=?", (id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "Không tìm thấy"

    ketqua = row[9] or ""

    if "Trễ" in ketqua:
        mau = "red"
    elif "Đúng hạn" in ketqua:
        mau = "green"
    else:
        mau = "black"

    diem = row[11] if row[11] else ""
    nhan_xet = row[12] if row[12] else ""
    loai = row[16] if len(row) > 16 and row[16] else ""

    return f"""
    <h2>Chi tiết bài nộp</h2>

    <b>Tên:</b> {row[1]}<br>
    <b>Email:</b> {row[3]}<br>
    <b>Hoạt động:</b> {row[4]}<br>
    <b>Nội dung:</b> {row[5]}<br>
    <b>Link công khai:</b> <a href="{row[6]}" target="_blank">{row[6]}</a><br>
    <b>Thời gian nộp:</b> {row[7]}<br>
    <b>Deadline:</b> {row[8]}<br><br>

    <h3 style="color:{mau};">
        {row[9]}
    </h3>

    <hr>
    <h3>Chấm điểm</h3>

    <form method="post">
        Điểm: <input name="diem" value="{diem}" required><br><br>
        Nhận xét:<br>
        <textarea name="nhan_xet" rows="3" cols="40">{nhan_xet}</textarea><br><br>
        <button>Lưu</button>
    </form>

    <br>

    <h3>Kết quả hiện tại:</h3>
    Điểm: <b>{diem}</b><br>
    Xếp loại: <b>{loai}</b><br>
    Nhận xét: <b>{nhan_xet}</b>

    <br><br>
    <a href="/admin">Quay lại</a>
    """

# ================= DUYỆT XIN DỜI =================
@app.route("/duyet/<int:id>", methods=["POST"])
def duyet(id):

    if "admin" not in session:
        return redirect("/login")

    action = request.form["action"]
    so_ngay = request.form.get("so_ngay_duyet")

    conn = sqlite3.connect(DB, check_same_thread=False)
    c = conn.cursor()

    if action == "dongy":
        trangthai = f"Được duyệt, {so_ngay} ngày"
        c.execute("""
            UPDATE extension_requests
            SET trang_thai=?, so_ngay_duyet=?
            WHERE id=?
        """, (trangthai, int(so_ngay), id))
    else:
        trangthai = "Không được duyệt"
        c.execute("""
            UPDATE extension_requests
            SET trang_thai=?
            WHERE id=?
        """, (trangthai, id))

    conn.commit()
    conn.close()

    return redirect("/admin")



@app.route("/log_tab", methods=["POST"])
def log_tab():
    data = request.get_json()
    print("TAB EVENT:", data)
    return "", 200


@app.route("/xem-ket-qua/<int:id>", methods=["GET","POST"])
def xem_ket_qua(id):

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if request.method == "POST":
        link_moi = request.form["link_moi"]

        c.execute("""
        UPDATE submissions
        SET link_cong_khai=?, can_sua=0
        WHERE id=?
        """, (link_moi, id))

        conn.commit()
        conn.close()
        return redirect("/")

    c.execute("SELECT * FROM submissions WHERE id=?", (id,))
    row = c.fetchone()
    conn.close()

    # index theo bảng của bạn
    hoat_dong = row[4]
    noi_dung = row[5]
    diem = row[11]
    nhan_xet = row[12]
    loai = row[16]

    return f"""
    <h2>{hoat_dong}</h2>
    <p>{noi_dung}</p>

    <p><b>Điểm:</b> {diem}</p>
    <p><b>Xếp loại:</b> {loai}</p>
    <p><b>Nhận xét:</b> {nhan_xet}</p>

    <hr>
    <h3>Sửa bài và nộp lại</h3>

    <form method="post">
        <input name="link_moi" placeholder="Link bài đã sửa">
        <button>NỘP</button>
    </form>
    """


@app.route("/check-deadlines")
def check_deadlines():
    return render_template("check_deadlines.html", deadlines=activity_deadlines)


if __name__ == "__main__":
    app.run(debug=True)

