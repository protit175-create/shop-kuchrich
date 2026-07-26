import os
import re
from datetime import datetime
import hashlib
import requests
import time
from flask import Flask, request, redirect, url_for, jsonify, session

app = Flask(__name__)
app.secret_key = "kuchrich_secret_key_2026"

FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61583528522725"

PARTNER_ID = "49683444915"
PARTNER_KEY = "133ab8ae2e5cb85dd59fd2538a34a4ee"

# --- KẾT NỐI FIREBASE ---
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://kuchrich-shop-default-rtdb.asia-southeast1.firebasedatabase.app'
})

def load_data(node_name):
    ref = db.reference(node_name)
    data = ref.get()
    return data if data else {}

def save_data(node_name, data):
    ref = db.reference(node_name)
    ref.set(data)

USERS = load_data('users')
HISTORY = load_data('history')

# ------------------------
SERVICES = [
    {
        "id": 1,
        "title": "DỊCH VỤ GROW A GARDEN 2",
        "tag": "Đang giảm 50%",
        "badge": "100% UY TÍN + AN TOÀN",
        "img": "dich-vu-grg2.png",   
        "link": "/service/grow-a-garden"
    }
]

ITEMS_GAG = [
    {"name": "LEGENDARY SPRINKLER X10", "price": "24.000 đ", "img": "sprinkler_x10.png"},
    {"name": "LEGENDARY SPRINKLER X30", "price": "54.000 đ", "img": "sprinkler_x30.png"},
    {"name": "LEGENDARY SPRINKLER X50", "price": "84.000 đ", "img": "sprinkler_x50.png"},
    {"name": "UNICORN", "price": "34.000 đ", "img": "unicorn.png"},
    {"name": "GOLDEN DRAGONFLY", "price": "24.000 đ", "img": "golden_dragonfly.png"},
    {"name": "BEE", "price": "14.000 đ", "img": "bee.png"},
    {"name": "MUSHROOM SEED X100", "price": "54.000 đ", "img": "mushroom_seed_x100.png"},
    {"name": "BAMBOO SEED X100", "price": "10.000 đ", "img": "bamboo_seed_x100.png"},
    {"name": "MUSHROOM SEED X10", "price": "14.000 đ", "img": "mushroom_seed_x10.png"},
    {"name": "MUSHROOM SEED X100 + BAMBOO SEED X100", "price": "54.000 đ", "img": "combo_mushroom_bamboo.png"},
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
                    <a href="/profile/change-password" class="menu-item"><span class="arrow">❯</span> Đổi mật khẩu</a>
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
            
            <div class="user-dropdown" id="napTienDropdownMenu" onclick="toggleNapMenu(event)" style="display: inline-block;">
                <a href="#" class="dropdown-toggle" style="color: #9ca3af; text-decoration: none; margin: 0 15px; font-weight: 500;">NẠP TIỀN ▼</a>
                <div class="dropdown-menu" style="width: 220px; left: 10px; top: calc(100% + 5px);">
                    <a href="/profile/recharge" class="menu-item" style="padding: 8px 0;"><span class="arrow">❯</span> 💳 Nạp thẻ cào</a>
                    <a href="/nap-atm" class="menu-item" style="padding: 8px 0;"><span class="arrow">❯</span> 🏦 Chuyển khoản Bank</a>
                </div>
            </div>

            {'<a href="/admin" style="color:#f59e0b; font-weight:bold;">👑 TRANG QUẢN LÝ (ADMIN)</a>' if current_user == "Kuchrich" else ""}
            <a href="{FACEBOOK_URL}" target="_blank">FANPAGE</a>
        </nav>
        <div class="auth-btns">{auth_html}</div>
    </header>
    
    <script>
        function toggleNapMenu(event) {{
            event.stopPropagation();
            var dropdown = document.getElementById("napTienDropdownMenu");
            dropdown.classList.toggle("active");
        }}
        document.addEventListener("click", function() {{
            var napDropdown = document.getElementById("napTienDropdownMenu");
            if (napDropdown) napDropdown.classList.remove("active");
        }});
    </script>
    '''

def get_profile_layout(active_tab, main_content_html):
    current_user = session.get("user")
    balance = USERS.get(current_user, {}).get("balance", 0) if current_user else 0
    
    tabs = {"info": "", "change_password": "", "balance": "", "deposit": "", "withdraw": ""}
    if active_tab in tabs:
        tabs[active_tab] = "active"

    return f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Trang cá nhân - Kuchrich</title>
        {BASE_CSS}
    </head>
    <body>
        {get_header()}
        <div class="profile-layout">
            <div class="profile-sidebar">
                <div class="side-user-card">
                    <img class="side-avatar" src="https://api.dicebear.com/7.x/bottts/svg?seed={current_user}" alt="Avatar">
                    <div>
                        <div style="font-size: 14px; font-weight: bold; color: #fff;">{current_user}</div>
                        <div style="font-size: 13px; color: #38bdf8; font-weight: bold;">{balance:,} đ</div>
                    </div>
                </div>
                <div class="side-menu-group">
                    <div class="side-menu-title">TÀI KHOẢN</div>
                    <a href="/profile/info" class="side-menu-item {tabs['info']}">Thông tin tài khoản</a>
                    <a href="/profile/change-password" class="side-menu-item {tabs['change_password']}">Đổi mật khẩu</a>
                    <a href="/profile/history/balance" class="side-menu-item {tabs['balance']}">Biến động số dư</a>
                    <a href="/profile/history/deposit" class="side-menu-item {tabs['deposit']}">Lịch sử nạp tiền</a>
                    <a href="/profile/history/withdraw" class="side-menu-item {tabs['withdraw']}">Lịch sử mua hàng</a>
                </div>
            </div>
            <div class="profile-main">
                {main_content_html}
            </div>
        </div>
    </body>
    </html>"""

@app.route("/")
def home():
    banner_html = f"""
    <div style="text-align: center; margin: 20px 0;">
        <img src="{url_for('static', filename='dich-vu-grg2.png')}" style="max-width: 600px; width: 100%; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
    </div>
    """
    
    cards_html = ""
    for item in SERVICES:
        cards_html += f"""
        <div class="card-item" style="max-width: 350px; margin: 0 auto; cursor: pointer;" onclick="window.location.href='{item['link']}'">
            <img class="card-item-img" src="{url_for('static', filename=item['img'])}">
            <div class="card-item-body">
                <div class="card-item-title">{item['title']}</div>
                <p style="color: #ef4444; margin-bottom: 12px; font-size: 13px;">{item['tag']}</p>
                <div class="btn-submit" style="text-align: center; font-size: 14px; background:#0284c7; padding:8px; border-radius:6px; color:white; font-weight:bold;">Xem Ngay</div>
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta name='google-site-verification' content='tTmA8Wj8zOGGSbDXkTtrk0KHC1VabAkyAqxpRAnoOWY' />
    <title>Kuchrich - Shop Game Roblox</title>
    {BASE_CSS}
</head>
<body>
    {get_header()}
    <div class='container'>
        {banner_html}
        <h2 style="text-align: center; margin-bottom: 25px; color: #38bdf8;">DANH MỤC DỊCH VỤ</h2>
        <div class='card-grid' style="display: flex; justify-content: center;">
            {cards_html}
        </div>
    </div>
</body>
</html>"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username in USERS and USERS[username]["password"] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return f"""<!DOCTYPE html><html><head>{BASE_CSS}</head><body>{get_header()}<div class='container' style='text-align:center;'><h3 style='color:#ef4444;'>❌ Sai tên tài khoản hoặc mật khẩu!</h3><br><a href='/login' style='color:#38bdf8;'>Thử lại</a></div></body></html>"""
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Đăng nhập - Kuchrich</title>{BASE_CSS}</head>
    <body>
        {get_header()}
        <div class="container" style="max-width: 400px; background: #131a2e; padding: 30px; border-radius: 12px; border: 1px solid #1e293b;">
            <h2 style="text-align:center; color:#0284c7; margin-bottom:20px;">ĐĂNG NHẬP</h2>
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label style="display:block; margin-bottom: 5px; font-size:14px;">Tên tài khoản:</label>
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
        save_data('users', USERS)
        
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
                <td>{item.get('type', item.get('title', '-'))}</td>
                <td><b style="color:#ef4444;">{item.get('price', '-')}</b></td>
                <td>{item.get('time', item.get('date', '-'))}</td>
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
    
    user_history = HISTORY.get(current_user, [])
    deposit_orders = [item for item in user_history if "Nạp tiền" in item.get("title", "") or "Nạp" in item.get("type", "")]

    if not deposit_orders:
        table_body = '<tr><td colspan="5" class="empty-msg">Chưa có dữ liệu nạp tiền</td></tr>'
    else:
        table_body = ""
        for item in reversed(deposit_orders):
            table_body += f"""
            <tr>
                <td><b style="color:#38bdf8;">{item.get('id', '-')}</b></td>
                <td>{item.get('title', 'Nạp tiền')}</td>
                <td><b style="color:#10b981;">{item.get('price', '-')}</b></td>
                <td>{item.get('date', item.get('time', '-'))}</td>
                <td><span style="color:#10b981; font-weight:bold;">{item.get('status', 'Hoàn thành')}</span></td>
            </tr>
            """

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
        <tbody>{table_body}</tbody>
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
            <img class="card-item-img" src="{url_for('static', filename=item['img'])}">
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

@app.route("/api/buy", methods=["POST"])
def api_buy():
    current_user = session.get("user")
    if not current_user or current_user not in USERS:
        return jsonify({"success": False, "message": "Vui lòng đăng nhập trước khi mua!"})
    
    data = request.get_json()
    item_name = data.get("item_name")
    roblox_user = data.get("roblox_user")
    
    # --- BẢO MẬT: Tìm giá trị thật của vật phẩm từ DB/Biến trên Server ---
    price_str = ""
    price_num = 0
    item_found = False
    
    for item in ITEMS_GAG:
        if item["name"] == item_name:
            price_str = item["price"]
            try:
                # Xử lý chuỗi giá trị (VD: "54.000 đ" -> 54000)
                price_num = int(price_str.replace(" đ", "").replace(".", "").replace(",", ""))
            except:
                price_num = 0
            item_found = True
            break
            
    if not item_found or price_num == 0:
        return jsonify({"success": False, "message": "Vật phẩm không hợp lệ hoặc không tồn tại!"})
    # -------------------------------------------------------------------
        
    balance = USERS[current_user].get("balance", 0)
    if balance < price_num:
        return jsonify({"success": False, "message": "Số dư tài khoản không đủ để thanh toán!"})
        
    USERS[current_user]["balance"] -= price_num
    save_data('users', USERS)
    
    order_id = "ORD" + datetime.now().strftime("%Y%m%d%H%M%S")
    time_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    if current_user not in HISTORY:
        HISTORY[current_user] = []
        
    order_record = {
        "id": order_id,
        "type": "Mua dịch vụ",
        "item": item_name,
        "price": price_str,
        "price_num": price_num,
        "roblox_user": roblox_user,
        "time": time_str,
        "status": "Đang xử lý"
    }
    
    balance_record = {
        "id": order_id,
        "type": f"Thanh toán mua {item_name}",
        "price": f"-{price_str}",
        "time": time_str
    }
    
    HISTORY[current_user].append(order_record)
    HISTORY[current_user].append(balance_record)
    save_data('history', HISTORY)
    
    return jsonify({"success": True, "message": "Đặt hàng thành công! Đang chờ Admin duyệt đơn."})

@app.route("/admin")
def admin_page():
    current_user = session.get("user")
    if current_user != "Kuchrich":
        return f"<!DOCTYPE html><html><head>{BASE_CSS}</head><body>{get_header()}<div class='container' style='text-align:center;'><h2 style='color:#ef4444;'>🚫 CHỈ DÀNH CHO ADMIN KUCHRICH!</h2><a href='/login' style='color:#38bdf8;'>Đăng nhập Admin</a></div></body></html>"

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
            status_badge = '<span style="color:#10b981; font-weight:bold;">Đã hoàn thành</span>'
            action_btn = '<span style="color:#64748b;">-</span>'
        elif status == "Đã hủy":
            status_badge = '<span style="color:#ef4444; font-weight:bold;">Đã hủy & Hoàn tiền</span>'
            action_btn = '<span style="color:#64748b;">-</span>'
        else:
            status_badge = '<span style="color:#f59e0b; font-weight:bold;">Đang chờ xử lý</span>'
            action_btn = f'''
            <button class="btn-action" 
                data-id="{order.get('id')}" 
                data-userweb="{order.get('user_web')}" 
                data-roblox="{order.get('roblox_user')}" 
                data-item="{order.get('item')}" 
                data-price="{order.get('price')}" 
                onclick="openAdminModalFromBtn(this)">Xử lý đơn</button>
            '''

        rows += f"""
        <tr>
            <td><b style="color:#38bdf8;">{order.get('id')}</b></td>
            <td><b style="color:#fff;">{order.get('user_web')}</b></td>
            <td><code style="color:#f59e0b;">{order.get('roblox_user')}</code></td>
            <td>{order.get('item')} (<b style="color:#ef4444;">{order.get('price')}</b>)</td>
            <td>{order.get('time')}</td>
            <td>{status_badge}</td>
            <td>{action_btn}</td>
        </tr>
        """

    if not rows:
        rows = '<tr><td colspan="7" class="empty-msg">Chưa có đơn hàng nào cần xử lý</td></tr>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Trang Quản Lý Admin - Kuchrich</title>{BASE_CSS}</head>
    <body>
        {get_header()}
        <div class="container" style="max-width: 1300px;">
            <h2 class="section-title" style="color:#f59e0b;">👑 TRANG QUẢN LÝ ĐƠN HÀNG (ADMIN)</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>MÃ ĐƠN</th>
                        <th>USER WEB</th>
                        <th>ACC ROBLOX</th>
                        <th>VẬT PHẨM</th>
                        <th>THỜI GIAN</th>
                        <th>TRẠNG THÁI</th>
                        <th>THƯƠNG LƯỢNG / DUYỆT</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>

        <div class="modal-overlay" id="adminModal">
            <div class="modal-card">
                <span class="modal-close" onclick="closeAdminModal()">&times;</span>
                <div class="modal-header-title">Xử lý đơn hàng</div>
                
                <div class="admin-info-box">
                    <div><b>Mã đơn:</b> <span id="admOrderId" style="color:#38bdf8;"></span></div>
                    <div><b>Khách Web:</b> <span id="admUserWeb" style="color:#fff;"></span></div>
                    <div><b>Acc Roblox:</b> <span id="admRobloxUser" style="color:#f59e0b;"></span></div>
                    <div><b>Vật phẩm:</b> <span id="admItem"></span></div>
                    <div><b>Số tiền:</b> <span id="admPrice" style="color:#ef4444;"></span></div>
                </div>

                <div class="admin-btn-group">
                    <button class="btn-confirm-done" onclick="processOrder('complete')">✔ XÁC NHẬN HOÀN THÀNH</button>
                    <button class="btn-confirm-cancel" onclick="processOrder('cancel')">✖ HỦY ĐƠN (HOÀN TIỀN)</button>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/api/admin/process-order", methods=["POST"])
def api_admin_process_order():
    current_user = session.get("user")
    if current_user != "Kuchrich":
        return jsonify({"success": False, "message": "Không có quyền thực hiện!"})
        
    data = request.get_json()
    order_id = data.get("order_id")
    target_user = data.get("username")
    action = data.get("action")
    
    if target_user not in HISTORY:
        return jsonify({"success": False, "message": "Không tìm thấy user!"})
        
    found = False
    for order in HISTORY[target_user]:
        if order.get("id") == order_id:
            if action == "complete":
                order["status"] = "Hoàn thành"
                found = True
            elif action == "cancel":
                if order.get("status") != "Đã hủy":
                    order["status"] = "Đã hủy"
                    refund_amount = order.get("price_num")
                    if refund_amount is None:
                        try:
                            refund_amount = int(order.get("price", "0").replace(" đ", "").replace(".", "").replace(",", ""))
                        except:
                            refund_amount = 0
                    if target_user in USERS:
                        USERS[target_user]["balance"] += refund_amount
                        save_data('users', USERS)
                found = True
            break
    
    if found:
        save_data('history', HISTORY)
        return jsonify({"success": True, "message": "Thao tác thành công!"})
    else:
        return jsonify({"success": False, "message": "Không tìm thấy đơn hàng trong hệ thống!"})

# --- TRANG NẠP THẺ CÀO (GIAO DIỆN TÍCH HỢP FORM TỰ ĐỘNG) ---
@app.route("/profile/recharge")
def profile_recharge():
    current_user = session.get("user")
    if not current_user: return redirect(url_for("login"))
    
    html = f"""
    <div class="profile-page-title">Nạp thẻ cào tự động</div>
    <div class="profile-page-sub">Hệ thống nạp thẻ cào chiết khấu cao, tự động cộng tiền sau 30s</div>
    
    <div class="info-box-item" style="max-width: 600px;">
        <form id="cardForm" onsubmit="submitCard(event)">
            <div style="margin-bottom: 15px;">
                <label style="display:block; font-size:13px; color:#94a3b8; margin-bottom:5px;">Loại thẻ:</label>
                <select name="telco" class="roblox-input" required>
                    <option value="">-- Chọn loại thẻ --</option>
                    <option value="VIETTEL">Viettel</option>
                    <option value="VINAPHONE">Vinaphone</option>
                    <option value="MOBIFONE">Mobifone</option>
                </select>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display:block; font-size:13px; color:#94a3b8; margin-bottom:5px;">Mệnh giá (VND):</label>
                <select name="amount" class="roblox-input" required>
                    <option value="">-- Chọn mệnh giá --</option>
                    <option value="10000">10.000 đ</option>
                    <option value="20000">20.000 đ</option>
                    <option value="50000">50.000 đ</option>
                    <option value="100000">100.000 đ</option>
                    <option value="200000">200.000 đ</option>
                    <option value="500000">500.000 đ</option>
                </select>
            </div>

            <div style="margin-bottom: 15px;">
                <label style="display:block; font-size:13px; color:#94a3b8; margin-bottom:5px;">Mã thẻ cào:</label>
                <input type="text" name="code" class="roblox-input" required placeholder="Nhập mã thẻ...">
            </div>

            <div style="margin-bottom: 20px;">
                <label style="display:block; font-size:13px; color:#94a3b8; margin-bottom:5px;">Số seri:</label>
                <input type="text" name="serial" class="roblox-input" required placeholder="Nhập số seri...">
            </div>

            <button type="submit" class="btn-buy-now" id="btnSubmitCard">GỬI THẺ NGAY</button>
        </form>
    </div>

    <script>
    function submitCard(event) {{
        event.preventDefault();
        var form = document.getElementById('cardForm');
        var formData = new FormData(form);
        var btn = document.getElementById('btnSubmitCard');
        
        btn.innerText = "Đang gửi thẻ...";
        btn.disabled = true;

        fetch('/nap-the', {{
            method: 'POST',
            body: formData
        }})
        .then(res => res.json())
        .then(data => {{
            alert(data.message);
            if(data.status === 'success') {{
                form.reset();
            }}
            btn.innerText = "GỬI THẺ NGAY";
            btn.disabled = false;
        }})
        .catch(err => {{
            alert('Có lỗi xảy ra, vui lòng thử lại!');
            btn.innerText = "GỬI THẺ NGAY";
            btn.disabled = false;
        }});
    }}
    </script>
    """
    return get_profile_layout("deposit", html)

# --- TRANG NẠP TIỀN QUA ATM / NGÂN HÀNG ---
@app.route("/nap-atm")
def nap_atm():
    if "user" not in session:
        return redirect(url_for("login"))
    
    username = session["user"]
    noi_dung_ck = f"NAP {username.upper()}"

    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nạp tiền qua ATM - Kuchrich Shop</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body {{ background-color: #0b0f19; color: #e2e8f0; font-family: 'Segoe UI', Arial, sans-serif; min-height: 100vh; }}
            .main-card {{ background-color: #161e2e; border: 1px solid #243044; border-radius: 16px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4); }}
            .text-highlight {{ color: #ef4444; font-weight: 700; }}
            .btn-copy {{ background-color: #2563eb; color: #ffffff; border: none; border-radius: 8px; padding: 6px 14px; font-weight: 600; font-size: 0.85rem; }}
            .btn-copy:hover {{ background-color: #1d4ed8; color: white; }}
            .content-box {{ background-color: #0f172a; border: 2px dashed #ef4444; border-radius: 10px; padding: 12px 18px; }}
            .qr-wrapper {{ background-color: #ffffff; padding: 12px; border-radius: 16px; display: inline-block; }}
            .qr-img {{ max-width: 280px; width: 100%; border-radius: 8px; }}
            .alert-info-custom {{ background-color: rgba(37, 99, 235, 0.1); border: 1px solid rgba(37, 99, 235, 0.3); color: #93c5fd; border-radius: 10px; }}
        </style>
    </head>
    <body class="py-5">
        <div class="container" style="max-width: 950px;">
            <a href="/" class="text-secondary text-decoration-none mb-3 d-inline-block"><i class="fa-solid fa-arrow-left me-2"></i>Quay lại trang chủ</a>
            
            <div class="main-card p-4 p-md-5">
                <h3 class="fw-bold mb-1"><i class="fa-solid fa-building-columns text-primary me-2"></i>Nạp qua ATM (Tự động 24/7)</h3>
                <p class="text-secondary mb-4">Chuyển khoản đúng nội dung, hệ thống sẽ <b>TỰ ĐỘNG CỘNG TIỀN</b> sau 1 - 3 phút!</p>

                <div class="row g-4 align-items-center">
                    <div class="col-lg-7">
                        <div class="text-uppercase mb-4 text-primary fw-bold">Thông giải tài khoản ngân hàng</div>
                        
                        <div class="mb-3">
                            <span class="text-secondary d-block fs-7">CHỦ TÀI KHOẢN:</span>
                            <span class="fs-5 text-highlight">TRAN THI THUY AN</span>
                        </div>

                        <div class="mb-3">
                            <span class="text-secondary d-block fs-7">NGÂN HÀNG:</span>
                            <span class="fs-5 text-highlight">TPBank (Ngân hàng Tiên Phong)</span>
                        </div>

                        <div class="mb-4">
                            <span class="text-secondary d-block fs-7">SỐ TÀI KHOẢN:</span>
                            <div class="d-flex align-items-center gap-3 mt-1">
                                <span class="fs-4 text-highlight font-monospace">00096883303</span>
                                <button class="btn-copy" onclick="copyText('00096883303')"><i class="fa-regular fa-copy me-1"></i>COPY STK</button>
                            </div>
                        </div>

                        <div class="mb-4">
                            <span class="text-secondary d-block mb-2 fs-7">Nội dung chuyển khoản (BẮT BUỘC):</span>
                            <div class="content-box d-flex align-items-center justify-content-between">
                                <span class="fs-5 text-highlight font-monospace" id="copy-content">{noi_dung_ck}</span>
                                <button class="btn-copy" onclick="copyText('{noi_dung_ck}')"><i class="fa-regular fa-copy me-1"></i>COPY NỘI DUNG</button>
                            </div>
                        </div>

                        <div class="alert alert-info-custom p-3 fs-7 mb-0">
                            <i class="fa-solid fa-bolt me-2 text-warning"></i>Ghi đúng nội dung <b>{noi_dung_ck}</b> để tiền tự động cộng vào tài khoản shop nhé!
                        </div>
                    </div>

                    <div class="col-lg-5 text-center">
                        <div class="qr-wrapper">
                            <!-- Mã QR.png nằm trong static -->
                            <img src="/static/QR.png" alt="Mã QR TPBank" class="qr-img">
                        </div>
                        <p class="text-secondary fs-7 mt-3"><i class="fa-solid fa-qrcode me-1"></i>Quét mã QR để chuyển nhanh</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function copyText(text) {{
                navigator.clipboard.writeText(text).then(function() {{
                    alert('Đã sao chép: ' + text);
                }});
            }}
        </script>
    </body>
    </html>
    """

# --- CỔNG RECEIVER WEBHOOK (SEPAY TỰ ĐỘNG CỘNG TIỀN ATM) ---
@app.route("/api/webhook/sepay", methods=["POST"])
def webhook_sepay():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data"}), 400

    content = data.get("content", "").upper()
    transfer_amount = int(data.get("transferAmount", 0))

    match = re.search(r"NAP\s+([A-ZA-Z0-9_]+)", content)
    if match and transfer_amount > 0:
        username_nap = match.group(1).lower()
        
        for user_key in USERS:
            if user_key.lower() == username_nap:
                USERS[user_key]["balance"] += transfer_amount
                save_data('users', USERS)
                
                if user_key not in HISTORY:
                    HISTORY[user_key] = []
                HISTORY[user_key].append({
                    "id": f"ATM{int(datetime.now().timestamp())}",
                    "title": "Nạp tiền qua ATM (Tự động)",
                    "price": f"+{transfer_amount:,} đ",
                    "price_num": transfer_amount,
                    "date": datetime.now().strftime("%H:%M %d/%m/%Y"),
                    "status": "Hoàn thành"
                })
                save_data('history', HISTORY)
                
                return jsonify({"success": True, "message": f"Đã cộng {transfer_amount}đ cho {user_key}"}), 200

    return jsonify({"success": False, "message": "Nội dung không hợp lệ hoặc user không tồn tại"}), 200


# --- ROUTE 1: Khách hàng gửi thẻ từ Web Shop lên ---
@app.route('/nap-the', methods=['POST'])
def nap_the():
    if 'user' not in session:
        return jsonify({'status': 'error', 'message': 'Vui lòng đăng nhập trước!'})
    
    telco = request.form.get('telco')      # Viettel, Vinaphone, Mobifone...
    amount = request.form.get('amount')    # 10000, 20000, 50000...
    code = request.form.get('code')        # Mã thẻ
    serial = request.form.get('serial')    # Số seri
    
    request_id = str(int(time.time()))     # Tạo mã giao dịch ngẫu nhiên
    
    # Tạo mã MD5 sign bảo mật theo yêu cầu Thesieure
    sign_str = PARTNER_KEY + code + serial
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    # Dữ liệu gửi sang Thesieure
    payload = {
        'request_id': request_id,
        'code': code,
        'partner_id': PARTNER_ID,
        'telco': telco,
        'serial': serial,
        'amount': amount,
        'sign': sign,
        'command': 'charging'
    }
    
    try:
        # Gửi yêu cầu gạch thẻ sang Thesieure
        response = requests.post('https://thesieure.com/chargingws/v2', data=payload)
        result = response.json()
        
        # 99 nghĩa là thẻ đã gửi thành công lên hệ thống, chờ duyệt
        if result.get('status') == 99:
            db.reference(f'cards/{request_id}').set({
                'username': session['user'],
                'amount': amount,
                'status': 'pending'
            })
            return jsonify({'status': 'success', 'message': 'Gửi thẻ thành công! Vui lòng chờ 10-60s hệ thống duyệt.'})
        else:
            return jsonify({'status': 'error', 'message': result.get('message', 'Thẻ không hợp lệ hoặc bị lỗi từ nhà mạng!')})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Lỗi kết nối máy chủ nạp thẻ!'})


# --- ROUTE 2: Callback tự động nhận kết quả từ Thesieure để CỘNG TIỀN THẺ CÀO ---
@app.route('/callback_card', methods=['POST', 'GET'])
def callback_card():
    status = request.args.get('status') or request.form.get('status')
    request_id = request.args.get('request_id') or request.form.get('request_id')
    declared_value = request.args.get('declared_value') or request.form.get('declared_value')
    
    # Status = 1 nghĩa là thẻ ĐÚNG, nạp thành công
    if str(status) == '1':
        card_info = db.reference(f'cards/{request_id}').get()
        if card_info and card_info.get('status') == 'pending':
            username = card_info.get('username')
            add_amount = int(declared_value)
            
            # 1. Cập nhật trạng thái thẻ trên db
            db.reference(f'cards/{request_id}').update({'status': 'success'})
            
            # 2. Cộng tiền cho User (Đồng bộ với biến bộ nhớ USERS để web nhận diện ngay)
            if username in USERS:
                USERS[username]["balance"] += add_amount
                save_data('users', USERS)
                
                # 3. Ghi lại lịch sử nạp
                if username not in HISTORY:
                    HISTORY[username] = []
                HISTORY[username].append({
                    "id": f"CARD{int(time.time())}",
                    "title": "Nạp thẻ cào (Tự động)",
                    "price": f"+{add_amount:,} đ",
                    "price_num": add_amount,
                    "date": datetime.now().strftime("%H:%M %d/%m/%Y"),
                    "status": "Hoàn thành"
                })
                save_data('history', HISTORY)
            
    return 'OK', 200

@app.route("/profile/change-password", methods=["GET", "POST"])
def profile_change_password():
    current_user = session.get("user")
    if not current_user:
        return redirect(url_for("login"))
    
    msg = ""
    msg_type = ""

    if request.method == "POST":
        old_pass = request.form.get("old_password", "").strip()
        new_pass = request.form.get("new_password", "").strip()
        confirm_pass = request.form.get("confirm_password", "").strip()

        # Lấy thông tin pass hiện tại từ dict USERS
        user_data = USERS.get(current_user, {})
        current_db_pass = user_data.get("password", "")

        if old_pass != current_db_pass:
            msg = "Mật khẩu hiện tại không chính xác!"
            msg_type = "error"
        elif new_pass != confirm_pass:
            msg = "Mật khẩu mới và xác nhận mật khẩu không khớp!"
            msg_type = "error"
        elif old_pass == new_pass:
            msg = "Mật khẩu mới không được trùng với mật khẩu cũ!"
            msg_type = "error"
        elif len(new_pass) < 6:
            msg = "Mật khẩu mới phải có ít nhất 6 ký tự!"
            msg_type = "error"
        else:
            # Cập nhật mật khẩu mới vào Firebase & bộ nhớ USERS
            USERS[current_user]["password"] = new_pass
            save_data('users', USERS)
            msg = "Đổi mật khẩu thành công!"
            msg_type = "success"

    # HTML Giao diện trang Đổi Mật Khẩu (Chuẩn style Dark Theme của Kuchrich Shop)
    alert_html = ""
    if msg:
        border_color = "#22c55e" if msg_type == "success" else "#ef4444"
        bg_color = "rgba(34, 197, 94, 0.15)" if msg_type == "success" else "rgba(239, 68, 68, 0.15)"
        text_color = "#86efac" if msg_type == "success" else "#fca5a5"
        alert_html = f'''
        <div style="padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; border: 1px solid {border_color}; background: {bg_color}; color: {text_color}; font-size: 14px; font-weight: 600;">
            {msg}
        </div>
        '''

    html = f"""
    <div class="profile-page-title">Đổi mật khẩu</div>
    <div class="profile-page-sub">Cập nhật mật khẩu thường xuyên để bảo vệ tài khoản Roblox & số dư của bạn</div>
    
    {alert_html}

    <div class="info-box-item" style="max-width: 550px; padding: 24px;">
        <form method="POST">
            <div style="margin-bottom: 18px;">
                <label style="display:block; font-size:13px; color:#94a3b8; font-weight:600; margin-bottom:8px;">MẬT KHẨU HIỆN TẠI</label>
                <input type="password" name="old_password" class="roblox-input" required placeholder="Nhập mật khẩu hiện tại...">
            </div>

            <div style="margin-bottom: 18px;">
                <label style="display:block; font-size:13px; color:#94a3b8; font-weight:600; margin-bottom:8px;">MẬT KHẨU MỚI</label>
                <input type="password" name="new_password" class="roblox-input" minlength="6" required placeholder="Nhập mật khẩu mới (tối thiểu 6 ký tự)...">
            </div>

            <div style="margin-bottom: 24px;">
                <label style="display:block; font-size:13px; color:#94a3b8; font-weight:600; margin-bottom:8px;">XÁC NHẬN MẬT KHẨU MỚI</label>
                <input type="password" name="confirm_password" class="roblox-input" required placeholder="Nhập lại mật khẩu mới...">
            </div>

            <button type="submit" class="btn-buy-now" style="background: #0284c7;">CẬP NHẬT MẬT KHẨU</button>
        </form>
    </div>
    """
    return get_profile_layout("change_password", html)

# Lệnh khởi chạy server (LUÔN ĐẶT Ở DƯỚI CÙNG)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)