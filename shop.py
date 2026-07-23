import json
import os
from datetime import datetime
from flask import Flask, request, redirect, url_for, jsonify, session

app = Flask(__name__)
app.secret_key = "kuchrich_secret_key_2026"

DB_FILE = "users.json"
HISTORY_FILE = "history.json"

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

USERS = load_data(DB_FILE)
HISTORY = load_data(HISTORY_FILE)

FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61583528522725"

SERVICES = [
    {
        "id": 1,
        "title": "DỊCH VỤ GROW A GARDEN 2",
        "tag": "Đang giảm 50%",
        "badge": "100% UY TÍN + AN TOÀN",
        "img": "https://via.placeholder.com/400x220/171d33/38bdf8?text=Grow+A+Garden+2",
        "link": "/service/grow-a-garden"
    }
]

ITEMS_GAG = [
    {
        "name": "LEGENDARY SPRINKLER X10", 
        "price": "24.000 đ", 
        "img": "/static/sprinkler_x10.png"
    },
    {
        "name": "LEGENDARY SPRINKLER X30", 
        "price": "54.000 đ", 
        "img": "/static/sprinkler_x30.png"
    },
    {
        "name": "LEGENDARY SPRINKLER X50", 
        "price": "84.000 đ", 
        "img": "/static/sprinkler_x50.png"
    },
    {
        "name": "UNICORN", 
        "price": "34.000 đ", 
        "img": "/static/unicorn.png"
    },
    {
        "name": "GOLDEN DRAGONFLY", 
        "price": "24.000 đ", 
        "img": "/static/golden_dragonfly.png"
    },
    {
        "name": "BEE", 
        "price": "14.000 đ", 
        "img": "/static/bee.png"
    },
    {
        "name": "MUSHROOM SEED X100", 
        "price": "54.000 đ", 
        "img": "/static/mushroom_seed_x100.png"
    },
    {
        "name": "BAMBOO SEED X100", 
        "price": "10.000 đ", 
        "img": "/static/bamboo_seed_x100.png"
    },
    {
        "name": "MUSHROOM SEED X10", 
        "price": "14.000 đ", 
        "img": "/static/mushroom_seed_x10.png"
    },
    {
        "name": "MUSHROOM SEED X100 + BAMBOO SEED X100", 
        "price": "54.000 đ", 
        "img": "/static/combo_mushroom_bamboo.png"
    },
]

BASE_CSS = """
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
    body { background-color: #0b0f19; color: #ffffff; }
    header {
        background-color: #111827; padding: 15px 50px;
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 1px solid #1f2937; position: relative; z-index: 100;
    }
    .logo { font-size: 22px; font-weight: bold; color: #38bdf8; text-decoration: none; text-transform: uppercase; letter-spacing: 1px; }
    nav a { color: #9ca3af; text-decoration: none; margin: 0 15px; font-weight: 500; }
    nav a:hover { color: #ffffff; }

    .auth-btns { display: flex; gap: 10px; align-items: center; }
    
    .btn-login {
        background-color: #0284c7; color: white; border: none; padding: 8px 18px;
        border-radius: 6px; cursor: pointer; text-decoration: none; font-weight: bold; font-size: 14px;
        transition: background 0.2s;
    }
    .btn-login:hover { background-color: #0369a1; }

    .btn-register {
        background-color: #10b981; color: white; border: none; padding: 8px 18px;
        border-radius: 6px; cursor: pointer; text-decoration: none; font-weight: bold; font-size: 14px;
        transition: background 0.2s;
    }
    .btn-register:hover { background-color: #059669; }

    .user-dropdown { position: relative; display: inline-block; }
    .user-btn-box {
        background: #111827; border: 1px solid #0284c7; border-radius: 8px;
        padding: 8px 16px; color: #ffffff; font-weight: bold; font-size: 14px;
        cursor: pointer; display: flex; align-items: center; gap: 8px;
    }
    .user-btn-box:hover { background: #1f2937; }
    
    .dropdown-menu {
        display: none; position: absolute; right: 0; top: calc(100% + 10px);
        width: 310px; background: #171d33; border: 1px solid #232a42;
        border-radius: 12px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.7);
        z-index: 999;
    }
    .user-dropdown.active .dropdown-menu { display: block; }

    .user-profile-header { display: flex; align-items: center; gap: 15px; padding-bottom: 15px; border-bottom: 1px dashed #2d3748; margin-bottom: 15px; }
    .user-avatar { width: 55px; height: 55px; border-radius: 8px; background: #2d3748; object-fit: cover; border: 1px solid #38bdf8; }
    .user-info-text { display: flex; flex-direction: column; gap: 2px; }
    .user-info-name { font-size: 14px; color: #ffffff; font-weight: bold; }
    .user-info-balance { font-size: 13px; color: #ffffff; }

    .menu-group { margin-bottom: 15px; }
    .menu-title { font-size: 12px; font-weight: 800; color: #9ca3af; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px; }
    .menu-item {
        display: flex; align-items: center; gap: 10px; color: #d1d5db;
        text-decoration: none; padding: 6px 0; font-size: 14px; transition: color 0.2s;
    }
    .menu-item:hover { color: #38bdf8; }
    .menu-item span.arrow { font-size: 11px; color: #6b7280; }

    .btn-logout-menu {
        display: block; width: 100%; background: #ef4444; color: #ffffff;
        text-align: center; text-decoration: none; padding: 10px; border-radius: 8px;
        font-weight: 700; font-size: 14px; margin-top: 10px; transition: background 0.2s;
    }
    .btn-logout-menu:hover { background: #dc2626; }
    
    .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
    .section-title { text-align: center; font-size: 26px; color: #38bdf8; margin-bottom: 30px; font-weight: bold; }

    .profile-layout { display: flex; gap: 24px; max-width: 1280px; margin: 30px auto; padding: 0 20px; }
    .profile-sidebar { width: 280px; background: #131a2e; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; height: fit-content; }
    .profile-main { flex: 1; background: #131a2e; border: 1px solid #1e293b; border-radius: 12px; padding: 30px; min-height: 500px; }

    .side-user-card { background: #182238; border: 1px solid #23314d; border-radius: 10px; padding: 15px; display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
    .side-avatar { width: 45px; height: 45px; border-radius: 8px; border: 1px solid #38bdf8; }

    .side-menu-group { margin-bottom: 20px; }
    .side-menu-title { font-size: 13px; font-weight: bold; color: #3b82f6; text-transform: capitalize; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
    .side-menu-item { display: flex; align-items: center; gap: 8px; color: #94a3b8; text-decoration: none; padding: 8px 10px; font-size: 14px; border-radius: 6px; transition: all 0.2s; }
    .side-menu-item:hover { background: #1e293b; color: #ffffff; }
    .side-menu-item.active { background: #0284c7; color: #ffffff; font-weight: bold; }

    .profile-page-title { font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 6px; }
    .profile-page-sub { font-size: 14px; color: #64748b; margin-bottom: 24px; }

    .data-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .data-table th { color: #ffffff; font-weight: bold; font-size: 13px; text-transform: uppercase; padding: 12px; border-bottom: 1px solid #1e293b; text-align: left; }
    .data-table td { padding: 16px 12px; font-size: 14px; color: #94a3b8; border-bottom: 1px solid #1e293b; }
    .empty-msg { text-align: center; padding: 40px 0; color: #ffffff; font-weight: 600; font-size: 15px; }

    .btn-action { background: #f59e0b; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 13px; }
    .btn-action:hover { background: #d97706; }

    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 20px; }
    .card-item {
        background-color: #171d33; border-radius: 8px; overflow: hidden;
        border: 1px solid #232a42; display: flex; flex-direction: column;
        transition: transform 0.2s, border-color 0.2s;
    }
    .card-item:hover { transform: translateY(-3px); border-color: #38bdf8; }
    .card-item-img { width: 100%; height: 160px; background-color: #111628; object-fit: cover; }
    .card-item-body { padding: 15px; text-align: center; background-color: #171d33; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
    .card-item-title { color: #ffffff; font-weight: 700; font-size: 14px; text-transform: uppercase; margin-bottom: 12px; line-height: 1.4; }
    .card-item-price { color: #f87171; font-weight: 800; font-size: 18px; }

    .modal-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.75); display: none; justify-content: center; align-items: center; z-index: 1000;
    }
    .modal-overlay.active { display: flex; }
    .modal-card {
        background: #171d33; width: 460px; max-width: 90%; border-radius: 10px; padding: 24px;
        border: 1px solid #28314e; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .modal-close { position: absolute; top: 15px; right: 18px; color: #9ca3af; font-size: 20px; font-weight: bold; cursor: pointer; }
    .modal-close:hover { color: #ffffff; }
    .modal-header-title { font-size: 18px; font-weight: 700; color: #ffffff; margin-bottom: 20px; }
    .modal-label { font-size: 12px; font-weight: 700; color: #9ca3af; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px; }
    .item-banner { background: linear-gradient(135deg, #0284c7, #2563eb); border-radius: 6px; padding: 14px 18px; margin-bottom: 20px; }
    .banner-price { color: #ffffff; font-weight: 800; font-size: 16px; margin-bottom: 4px; }
    .banner-title { color: #ffffff; font-weight: 800; font-size: 16px; text-transform: uppercase; }
    .payment-total { color: #f87171; font-size: 20px; font-weight: 800; margin-bottom: 20px; }
    
    .roblox-input-group { margin-bottom: 20px; }
    .roblox-input-group label { display: block; font-size: 13px; font-weight: 600; color: #d1d5db; margin-bottom: 8px; }
    .roblox-input { width: 100%; padding: 12px; background: #111628; border: 1px solid #2a3454; border-radius: 6px; color: white; font-size: 14px; outline: none; }
    .roblox-input:focus { border-color: #38bdf8; }
    
    .btn-buy-now { width: 100%; background: #02b0e8; color: #ffffff; border: none; padding: 12px; border-radius: 6px; font-weight: 800; font-size: 15px; cursor: pointer; text-transform: uppercase; }
    .btn-buy-now:hover { background: #0284c7; }

    .admin-info-box { background: #111628; border-radius: 8px; padding: 15px; margin-bottom: 20px; font-size: 14px; line-height: 1.8; }
    .admin-btn-group { display: flex; gap: 10px; margin-top: 20px; }
    .btn-confirm-done { flex: 1; background: #10b981; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; }
    .btn-confirm-cancel { flex: 1; background: #ef4444; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; }
    
    .info-box-item { background: #182238; padding: 15px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #23314d; }
    .info-box-label { font-size: 13px; color: #94a3b8; margin-bottom: 4px; }
    .info-box-val { font-size: 16px; color: #fff; font-weight: bold; }
</style>

<script>
    let currentOrderId = '';
    let currentOrderUser = '';

    function toggleUserMenu(event) {
        event.stopPropagation();
        var dropdown = document.getElementById("userDropdown");
        dropdown.classList.toggle("active");
    }
    document.addEventListener("click", function() {
        var dropdown = document.getElementById("userDropdown");
        if (dropdown) dropdown.classList.remove("active");
    });

    function openBuyModal(itemName, itemPrice) {
        document.getElementById("modalItemTitle").innerText = itemName;
        document.getElementById("modalItemBannerPrice").innerText = itemPrice;
        document.getElementById("modalItemTotal").innerText = itemPrice;
        document.getElementById("buyModal").classList.add("active");
    }

    function closeBuyModal() {
        document.getElementById("buyModal").classList.remove("active");
    }

    function submitOrder() {
        var username = document.getElementById("robloxUser").value.trim();
        var itemName = document.getElementById("modalItemTitle").innerText;
        var itemPrice = document.getElementById("modalItemTotal").innerText;

        if (!username) {
            alert("Vui lòng nhập tài khoản (Roblox)!");
            return;
        }

        fetch('/api/buy', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ item_name: itemName, price: itemPrice, roblox_user: username })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("🎉 " + data.message);
                closeBuyModal();
                location.reload();
            } else {
                alert("❌ " + data.message);
            }
        });
    }

    function openAdminModalFromBtn(btn) {
        currentOrderId = btn.getAttribute('data-id');
        currentOrderUser = btn.getAttribute('data-userweb');

        document.getElementById("admOrderId").innerText = currentOrderId;
        document.getElementById("admUserWeb").innerText = currentOrderUser;
        document.getElementById("admRobloxUser").innerText = btn.getAttribute('data-roblox');
        document.getElementById("admItem").innerText = btn.getAttribute('data-item');
        document.getElementById("admPrice").innerText = btn.getAttribute('data-price');

        document.getElementById("adminModal").classList.add("active");
    }

    function closeAdminModal() {
        document.getElementById("adminModal").classList.remove("active");
    }

    function processOrder(action) {
        let msg = action === 'complete' ? 'Xác nhận ĐÃ HOÀN THÀNH đơn này?' : 'Xác nhận HỦY ĐƠN và HOÀN TIỀN lại cho khách?';
        if (!confirm(msg)) return;

        fetch('/api/admin/process-order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                order_id: currentOrderId,
                username: currentOrderUser,
                action: action
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("✅ " + data.message);
                closeAdminModal();
                location.reload();
            } else {
                alert("❌ " + data.message);
            }
        });
    }
</script>
"""

def get_header():
    current_user = session.get("user")
    if current_user and current_user in USERS:
        balance = USERS[current_user].get("balance", 0)
        admin_link = '<a href="/admin" class="menu-item" style="color:#f59e0b;"><span class="arrow">❯</span> Trang Admin Quản Lý</a>' if current_user == "Kuchrich" else ""
        
        # ĐÃ KHÔI PHỤC ĐẦY ĐỦ MENU TÀI KHOẢN KHÁCH TRÊN HEADER
        auth_html = f'''
        <div class="user-dropdown" id="userDropdown" onclick="toggleUserMenu(event)">
            <div class="user-btn-box">
                <span>🐱</span>
                <span>{balance:,} đ</span>
                <span style="font-size: 10px;">▼</span>
            </div>
            
            <div class="dropdown-menu">
                <div class="user-profile-header">
                    <img class="user-avatar" src="https://api.dicebear.com/7.x/bottts/svg?seed={current_user}" alt="Avatar">
                    <div class="user-info-text">
                        <span class="user-info-name">Tên: {current_user}</span>
                        <span class="user-info-balance">Số dư: <b>{balance:,} đ</b></span>
                    </div>
                </div>

                <div class="menu-group">
                    <div class="menu-title">TÀI KHOẢN</div>
                    <a href="/profile/info" class="menu-item"><span class="arrow">❯</span> Thông tin tài khoản</a>
                    <a href="/profile/history/balance" class="menu-item"><span class="arrow">❯</span> Biến động số dư</a>
                    <a href="/profile/history/deposit" class="menu-item"><span class="arrow">❯</span> Lịch sử nạp tiền</a>
                    <a href="/profile/history/withdraw" class="menu-item"><span class="arrow">❯</span> Lịch sử mua hàng</a>
                    {admin_link}
                </div>

                <a href="/logout" class="btn-logout-menu">Đăng xuất</a>
            </div>
        </div>
        '''
    else:
        auth_html = '''
        <a href="/login"><button class="btn-login">ĐĂNG NHẬP</button></a>
        <a href="/register"><button class="btn-register">ĐĂNG KÝ</button></a>
        '''
    
    return f'''
    <header>
        <a href="/" class="logo">Kuchrich</a>
        <nav>
            <a href="/">TRANG CHỦ</a>
            {"<a href='/admin' style='color:#f59e0b; font-weight:bold;'>👑 TRANG QUẢN LÝ (ADMIN)</a>" if current_user == "Kuchrich" else ""}
            <a href="{FACEBOOK_URL}" target="_blank">FANPAGE ↗</a>
        </nav>
        <div class="auth-btns">{auth_html}</div>
    </header>
    '''

def get_profile_layout(active_tab, main_content_html):
    current_user = session.get("user", "")
    balance = USERS[current_user].get("balance", 0) if current_user in USERS else 0
    
    # ĐÃ KHÔI PHỤC ĐẦY ĐỦ CÁC MỤC Ở SIDEBAR BÊN TRÁI
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Trang Cá Nhân - Kuchrich</title>{BASE_CSS}</head>
    <body>
        {get_header()}
        <div class="profile-layout">
            <div class="profile-sidebar">
                <div class="side-user-card">
                    <img class="side-avatar" src="https://api.dicebear.com/7.x/bottts/svg?seed={current_user}">
                    <div class="side-user-info">
                        <div style="font-size: 13px; color: #94a3b8;">Tên: <b style="color:#fff;">{current_user}</b></div>
                        <div style="font-size: 13px; color: #94a3b8;">Số dư: <b style="color:#3b82f6;">{balance:,} đ</b></div>
                    </div>
                </div>
                
                <div class="side-menu-group">
                    <div class="side-menu-title">Tài khoản <span>▲</span></div>
                    <a href="/profile/info" class="side-menu-item {'active' if active_tab == 'info' else ''}">❯ Thông tin chung</a>
                </div>

                <div class="side-menu-group">
                    <div class="side-menu-title">Lịch sử <span>▲</span></div>
                    <a href="/profile/history/balance" class="side-menu-item {'active' if active_tab == 'balance' else ''}">❯ Biến động số dư</a>
                    <a href="/profile/history/deposit" class="side-menu-item {'active' if active_tab == 'deposit' else ''}">❯ Lịch sử nạp tiền</a>
                    <a href="/profile/history/withdraw" class="side-menu-item {'active' if active_tab == 'withdraw' else ''}">❯ Lịch sử mua dịch vụ</a>
                </div>
            </div>
            <div class="profile-main">{main_content_html}</div>
        </div>
    </body>
    </html>
    """

# ----------------------------------------------------
# ROUTES MAIN
# ----------------------------------------------------

@app.route("/")
def home():
    cards_html = ""
    for item in SERVICES:
        cards_html += f"""
        <div class="card-item" style="max-width: 350px; margin: 0 auto; cursor: pointer;" onclick="window.location.href='{item['link']}'">
            <img class="card-item-img" src="{item['img']}">
            <div class="card-item-body">
                <div class="card-item-title">{item['title']}</div>
                <p style="color: #ef4444; margin-bottom: 12px; font-size: 13px;">{item['tag']}</p>
                <div class="btn-submit" style="text-align: center; font-size: 14px; background:#0284c7; padding:8px; border-radius:6px; color:white; font-weight:bold;">Xem Ngay</div>
            </div>
        </div>
        """
    return f"<!DOCTYPE html><html><head><title>Kuchrich - Shop Game Roblox</title>{BASE_CSS}</head><body>{get_header()}<div class='container'><h2 class='section-title'>🌴 DANH MỤC DỊCH VỤ 🌴</h2>{cards_html}</div></body></html>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username in USERS and USERS[username]["password"] == password:
            session["user"] = username
            if username == "Kuchrich":
                return redirect(url_for("admin_page"))
            return redirect(url_for("home"))
        else:
            return f"<!DOCTYPE html><html><head>{BASE_CSS}</head><body>{get_header()}<div class='container' style='text-align:center;'><h3 style='color:#ef4444;'>❌ Sai tài khoản hoặc mật khẩu!</h3><br><a href='/login' style='color:#38bdf8;'>Thử lại</a></div></body></html>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Đăng nhập - Kuchrich</title>{BASE_CSS}</head>
    <body>
        {get_header()}
        <div class="container" style="max-width: 400px; background: #131a2e; padding: 30px; border-radius: 12px; border: 1px solid #1e293b;">
            <h2 style="text-align:center; color:#38bdf8; margin-bottom:20px;">ĐĂNG NHẬP</h2>
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label style="display:block; margin-bottom: 5px; font-size:14px;">Tài khoản:</label>
                    <input type="text" name="username" class="roblox-input" required placeholder="Nhập tên tài khoản...">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display:block; margin-bottom: 5px; font-size:14px;">Mật khẩu:</label>
                    <input type="password" name="password" class="roblox-input" required placeholder="Nhập mật khẩu...">
                </div>
                <button type="submit" class="btn-buy-now">ĐĂNG NHẬP</button>
            </form>
            <p style="text-align:center; margin-top:15px; font-size:14px; color:#9ca3af;">
                Chưa có tài khoản? <a href="/register" style="color:#10b981; font-weight:bold;">Đăng ký ngay</a>
            </p>
        </div>
    </body>
    </html>
    """

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return f"<!DOCTYPE html><html><head>{BASE_CSS}</head><body>{get_header()}<div class='container' style='text-align:center;'><h3 style='color:#ef4444;'>❌ Vui lòng nhập đầy đủ thông tin!</h3><br><a href='/register' style='color:#38bdf8;'>Thử lại</a></div></body></html>"

        if username in USERS:
            return f"<!DOCTYPE html><html><head>{BASE_CSS}</head><body>{get_header()}<div class='container' style='text-align:center;'><h3 style='color:#ef4444;'>❌ Tên tài khoản này đã tồn tại!</h3><br><a href='/register' style='color:#38bdf8;'>Chọn tên khác</a></div></body></html>"

        USERS[username] = {
            "password": password,
            "balance": 0
        }
        save_data(DB_FILE, USERS)
        
        session["user"] = username
        return redirect(url_for("home"))

    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Đăng ký - Kuchrich</title>{BASE_CSS}</head>
    <body>
        {get_header()}
        <div class="container" style="max-width: 400px; background: #131a2e; padding: 30px; border-radius: 12px; border: 1px solid #1e293b;">
            <h2 style="text-align:center; color:#10b981; margin-bottom:20px;">ĐĂNG KÝ TÀI KHOẢN</h2>
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label style="display:block; margin-bottom: 5px; font-size:14px;">Tên tài khoản mới:</label>
                    <input type="text" name="username" class="roblox-input" required placeholder="Nhập tên tài khoản...">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display:block; margin-bottom: 5px; font-size:14px;">Mật khẩu:</label>
                    <input type="password" name="password" class="roblox-input" required placeholder="Nhập mật khẩu...">
                </div>
                <button type="submit" class="btn-buy-now" style="background:#10b981;">TẠO TÀI KHOẢN</button>
            </form>
            <p style="text-align:center; margin-top:15px; font-size:14px; color:#9ca3af;">
                Đã có tài khoản? <a href="/login" style="color:#38bdf8; font-weight:bold;">Đăng nhập ngay</a>
            </p>
        </div>
    </body>
    </html>
    """

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# --- TẤT CẢ ROUTE TRANG CÁ NHÂN ĐÃ ĐƯỢC MỞ LẠI ---

@app.route("/profile/info")
def profile_info():
    current_user = session.get("user")
    if not current_user: return redirect(url_for("login"))
    balance = USERS[current_user].get("balance", 0)
    
    html = f"""
    <div class="profile-page-title">Thông tin tài khoản</div>
    <div class="profile-page-sub">Quản lý các thông tin cá nhân cơ bản</div>
    <div class="info-box-item">
        <div class="info-box-label">Tên tài khoản:</div>
        <div class="info-box-val">{current_user}</div>
    </div>
    <div class="info-box-item">
        <div class="info-box-label">Số dư khả dụng:</div>
        <div class="info-box-val" style="color:#38bdf8;">{balance:,} đ</div>
    </div>
    <div class="info-box-item">
        <div class="info-box-label">Trạng thái tài khoản:</div>
        <div class="info-box-val" style="color:#10b981;">Đang hoạt động</div>
    </div>
    """
    return get_profile_layout("info", html)

@app.route("/profile/history/balance")
def profile_history_balance():
    current_user = session.get("user")
    if not current_user: return redirect(url_for("login"))
    
    user_history = HISTORY.get(current_user, [])
    
    if not user_history:
        table_body = '<tr><td colspan="4" class="empty-msg">Chưa có biến động số dư nào</td></tr>'
    else:
        table_body = ""
        for item in reversed(user_history):
            table_body += f"""
            <tr>
                <td><b style="color:#38bdf8;">{item.get('id', '-')}</b></td>
                <td>{item.get('type', '-')}</td>
                <td><b style="color:#ef4444;">-{item.get('price', '-')}</b></td>
                <td>{item.get('time', '-')}</td>
            </tr>
            """

    html = f"""
    <div class="profile-page-title">Biến động số dư</div>
    <div class="profile-page-sub">Nhật ký thay đổi tiền trong tài khoản</div>
    <table class="data-table">
        <thead>
            <tr>
                <th>MÃ GD</th>
                <th>LOẠI GIAO DỊCH</th>
                <th>SỐ TIỀN</th>
                <th>THỜI GIAN</th>
            </tr>
        </thead>
        <tbody>{table_body}</tbody>
    </table>
    """
    return get_profile_layout("balance", html)

@app.route("/profile/history/deposit")
def profile_history_deposit():
    current_user = session.get("user")
    if not current_user: return redirect(url_for("login"))
    
    html = f"""
    <div class="profile-page-title">Lịch sử nạp tiền</div>
    <div class="profile-page-sub">Danh sách lượt nạp tiền qua Thẻ cào / Banking</div>
    <table class="data-table">
        <thead>
            <tr>
                <th>MÃ NẠP</th>
                <th>HÌNH THỨC</th>
                <th>SỐ TIỀN</th>
                <th>THỜI GIAN</th>
                <th>TRẠNG THÁI</th>
            </tr>
        </thead>
        <tbody>
            <tr><td colspan="5" class="empty-msg">Chưa có dữ liệu nạp tiền</td></tr>
        </tbody>
    </table>
    """
    return get_profile_layout("deposit", html)

@app.route("/profile/history/withdraw")
def profile_history_withdraw():
    current_user = session.get("user")
    if not current_user: return redirect(url_for("login"))
    
    user_history = HISTORY.get(current_user, [])
    service_orders = [item for item in user_history if item.get("type") == "Mua dịch vụ"]
    
    if not service_orders:
        table_body = '<tr><td colspan="5" class="empty-msg">Chưa có lịch sử mua dịch vụ</td></tr>'
    else:
        table_body = ""
        for item in reversed(service_orders):
            status = item.get("status", "Đang xử lý")
            if status == "Hoàn thành":
                status_badge = '<span style="color:#10b981; font-weight:bold;">Hoàn thành</span>'
            elif status == "Đã hủy":
                status_badge = '<span style="color:#ef4444; font-weight:bold;">Đã hủy (Đã hoàn tiền)</span>'
            else:
                status_badge = '<span style="color:#f59e0b; font-weight:bold;">Đang duyệt...</span>'

            table_body += f"""
            <tr>
                <td><b style="color:#38bdf8;">{item.get('id', '-')}</b></td>
                <td>{item.get('type', 'Mua dịch vụ')}</td>
                <td>
                    <b>Vật phẩm:</b> {item.get('item', '-')}<br>
                    <small>Acc Roblox: <code style="color:#f59e0b;">{item.get('roblox_user', '-')}</code> | Giá: <b style="color:#ef4444;">{item.get('price', '-')}</b></small>
                </td>
                <td>{item.get('time', '-')}</td>
                <td>{status_badge}</td>
            </tr>
            """

    html = f"""
    <div class="profile-page-title">Lịch sử mua dịch vụ</div>
    <div class="profile-page-sub">Danh sách các gói dịch vụ bạn đã thanh toán</div>
    <table class="data-table">
        <thead>
            <tr>
                <th>MÃ ĐƠN</th>
                <th>LOẠI</th>
                <th>THÔNG TIN</th>
                <th>THỜI GIAN</th>
                <th>TRẠNG THÁI</th>
            </tr>
        </thead>
        <tbody>{table_body}</tbody>
    </table>
    """
    return get_profile_layout("withdraw", html)

@app.route("/service/grow-a-garden")
def service_grow_a_garden():
    items_html = ""
    for item in ITEMS_GAG:
        price_val = item['price'].replace(' đ', '')
        items_html += f"""
        <div class="card-item" onclick="openBuyModal('{item['name']}', '{item['price']}')" style="cursor: pointer;">
            <img class="card-item-img" src="{item['img']}">
            <div class="card-item-body">
                <div class="card-item-title">{item['name']}</div>
                <div class="card-item-price">{price_val} <u>đ</u></div>
            </div>
        </div>
        """
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Grow A Garden 2 - Kuchrich</title>{BASE_CSS}</head>
    <body>
        {get_header()}
        <div class="container">
            <h2 class="section-title">🌱 VẬT PHẨM GROW A GARDEN 2 🌱</h2>
            <div class="grid">{items_html}</div>
        </div>

        <div class="modal-overlay" id="buyModal">
            <div class="modal-card">
                <span class="modal-close" onclick="closeBuyModal()">&times;</span>
                <div class="modal-header-title">Xác nhận thanh toán</div>
                <div class="modal-label">GÓI VẬT PHẨM</div>
                <div class="item-banner">
                    <div class="banner-price" id="modalItemBannerPrice">0 đ</div>
                    <div class="banner-title" id="modalItemTitle">TÊN VẬT PHẨM</div>
                </div>
                <div class="modal-label">CẦN THANH TOÁN:</div>
                <div class="payment-total" id="modalItemTotal">0 đ</div>

                <div class="roblox-input-group">
                    <label>Tài khoản (Roblox) <span>*</span></label>
                    <input type="text" class="roblox-input" id="robloxUser" placeholder="Ví dụ: hdraca">
                </div>

                <button class="btn-buy-now" onclick="submitOrder()">MUA NGAY</button>
            </div>
        </div>
    </body>
    </html>
    """

# ----------------------------------------------------
# TRANG ADMIN QUẢN LÝ DÀNH RIÊNG CHO TK: Kuchrich
# ----------------------------------------------------
@app.route("/admin")
def admin_page():
    current_user = session.get("user")
    if current_user != "Kuchrich":
        return f"<!DOCTYPE html><html><head>{BASE_CSS}</head><body>{get_header()}<div class='container' style='text-align:center;'><h2 style='color:#ef4444;'>🚫 CHỈ TRẢI NGHIỆM DÀNH CHO ADMIN KUCHRICH!</h2><a href='/login' style='color:#38bdf8;'>Đăng nhập Admin tại đây</a></div></body></html>"

    all_orders = []
    for user_name, user_hist in HISTORY.items():
        for order in user_hist:
            if order.get("type") == "Mua dịch vụ":
                order_copy = order.copy()
                order_copy["user_web"] = user_name
                all_orders.append(order_copy)
                
    all_orders.reverse()

    rows = ""
    for order in all_orders:
        status = order.get("status", "Đang xử lý")
        if status == "Hoàn thành":
            btn_action = '<span style="color:#10b981; font-weight:bold;">✅ Hoàn thành</span>'
        elif status == "Đã hủy":
            btn_action = '<span style="color:#ef4444; font-weight:bold;">❌ Đã hủy & Hoàn tiền</span>'
        else:
            btn_action = f"""
            <button class="btn-action" 
                    data-id="{order.get('id', '')}" 
                    data-userweb="{order.get('user_web', '')}" 
                    data-roblox="{order.get('roblox_user', '')}" 
                    data-item="{order.get('item', '')}" 
                    data-price="{order.get('price', '')}" 
                    onclick="openAdminModalFromBtn(this)">
                ⚙️ Xử lý đơn
            </button>
            """

        rows += f"""
        <tr>
            <td><b style="color:#38bdf8;">{order.get('id')}</b></td>
            <td><b>{order.get('user_web')}</b></td>
            <td><code style="color:#f59e0b; font-size:15px;">{order.get('roblox_user')}</code></td>
            <td>{order.get('item')}</td>
            <td><b style="color:#ef4444;">{order.get('price')}</b></td>
            <td>{order.get('time')}</td>
            <td>{btn_action}</td>
        </tr>
        """

    if not all_orders:
        rows = '<tr><td colspan="7" class="empty-msg">Chưa có đơn cày nào từ khách hàng!</td></tr>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Admin Kuchrich - Quản Lý Đơn Cày</title>{BASE_CSS}</head>
    <body>
        {get_header()}
        <div class="container">
            <h2 class="section-title" style="color:#f59e0b;">👑 PANEL QUẢN LÝ DÀNH CHO KUCHRICH 👑</h2>
            <div style="background:#131a2e; padding:25px; border-radius:12px; border:1px solid #1e293b;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>MÃ ĐƠN</th>
                            <th>USER WEB</th>
                            <th>ACC ROBLOX CẦN CÀY</th>
                            <th>VẬT PHẨM MUA</th>
                            <th>GIÁ TIỀN</th>
                            <th>THỜI GIAN</th>
                            <th>HÀNH ĐỘNG</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </div>

        <div class="modal-overlay" id="adminModal">
            <div class="modal-card">
                <span class="modal-close" onclick="closeAdminModal()">&times;</span>
                <div class="modal-header-title" style="color:#f59e0b;">⚙️ BẢNG XÁC NHẬN ĐƠN HÀNG</div>
                
                <div class="admin-info-box">
                    <div>Mã đơn: <b id="admOrderId" style="color:#38bdf8;"></b></div>
                    <div>Khách hàng (Web): <b id="admUserWeb" style="color:#fff;"></b></div>
                    <div>Acc Roblox: <b id="admRobloxUser" style="color:#f59e0b;"></b></div>
                    <div>Vật phẩm: <b id="admItem" style="color:#fff;"></b></div>
                    <div>Giá tiền: <b id="admPrice" style="color:#ef4444;"></b></div>
                </div>

                <div class="modal-label">CHỌN TRẠNG THÁI XỬ LÝ:</div>
                <div class="admin-btn-group">
                    <button class="btn-confirm-done" onclick="processOrder('complete')">✅ ĐÃ HOÀN THÀNH</button>
                    <button class="btn-confirm-cancel" onclick="processOrder('cancel')">❌ HỦY ĐƠN & HOÀN TIỀN</button>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# ----------------------------------------------------
# API MUA HÀNG & XỬ LÝ ĐƠN (ADMIN)
# ----------------------------------------------------
@app.route('/api/buy', methods=['POST'])
def buy_item():
    current_user = session.get("user")
    if not current_user or current_user not in USERS:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập tài khoản khách!'})

    data = request.get_json()
    item_name = data.get('item_name')
    raw_price = data.get('price', '0').replace('.', '').replace(' đ', '').strip()
    price = int(raw_price) if raw_price.isdigit() else 0
    roblox_user = data.get('roblox_user', '').strip()

    if not roblox_user:
        return jsonify({'success': False, 'message': 'Vui lòng nhập tài khoản Roblox!'})

    user = USERS.get(current_user)
    current_balance = user.get('balance', 0)

    if current_balance < price:
        return jsonify({'success': False, 'message': f'Số dư không đủ! Còn thiếu {price - current_balance:,} đ.'})

    user['balance'] -= price
    USERS[current_user] = user
    save_data(DB_FILE, USERS)

    if current_user not in HISTORY:
        HISTORY[current_user] = []

    new_tx = {
        "id": f"GAG{int(datetime.now().timestamp())}",
        "type": "Mua dịch vụ",
        "item": item_name,
        "price": f"{price:,} đ",
        "raw_price_num": price,
        "roblox_user": roblox_user,
        "time": datetime.now().strftime("%H:%M %d/%m/%Y"),
        "status": "Đang duyệt"
    }

    HISTORY[current_user].append(new_tx)
    save_data(HISTORY_FILE, HISTORY)

    return jsonify({'success': True, 'message': f'Mua thành công {item_name}! Đã gửi đơn cho Admin duyệt.'})

@app.route('/api/admin/process-order', methods=['POST'])
def admin_process_order():
    if session.get("user") != "Kuchrich":
        return jsonify({'success': False, 'message': 'Bạn không có quyền Admin!'})

    data = request.get_json()
    order_id = data.get('order_id')
    username = data.get('username')
    action = data.get('action')

    if username in HISTORY:
        for order in HISTORY[username]:
            if order.get("id") == order_id:
                if action == 'complete':
                    order["status"] = "Hoàn thành"
                    save_data(HISTORY_FILE, HISTORY)
                    return jsonify({'success': True, 'message': 'Đã cập nhật: HOÀN THÀNH!'})
                
                elif action == 'cancel':
                    order["status"] = "Đã hủy"
                    refund_amount = order.get("raw_price_num", 0)
                    
                    if username in USERS:
                        USERS[username]["balance"] += refund_amount
                        save_data(DB_FILE, USERS)

                    save_data(HISTORY_FILE, HISTORY)
                    return jsonify({'success': True, 'message': f'Đã HỦY ĐƠN và HOÀN LẠI {refund_amount:,}đ cho khách thành công!'})

    return jsonify({'success': False, 'message': 'Không tìm thấy đơn hàng!'})

if __name__ == "__main__":
    USERS["Kuchrich"] = {"password": "sigmaboi2012", "balance": 9999999}
    
    if "testuser" not in USERS:
        USERS["testuser"] = {"password": "123", "balance": 200000}
    
    save_data(DB_FILE, USERS)

    print("🚀 Shop đang chạy tại: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)