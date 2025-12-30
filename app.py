import streamlit as st
import pandas as pd
import requests
import time
import random
import string

# --- 1. 配置读取 ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    # 获取卡密列表，防止为空报错
    if "VALID_CODES" in st.secrets:
        VALID_CODES = st.secrets["VALID_CODES"].split(",")
    else:
        VALID_CODES = []
except Exception as e:
    VALID_CODES = []
    # 暂时不阻断，方便你先看到界面
    # st.error(f"请在 Streamlit 后台配置 Secrets！错误: {e}")

# ==========================================
# 🛑 管理员专用密码
ADMIN_PASSWORD = "admin_boss_888" 
# ==========================================

# --- 2. 功能函数定义 ---

# (A) 核心业务：AI 诊断 (Gemini 3 Flash)
def call_custom_api(prompt):
    url = "https://api.gptsapi.net/v1beta/models/gemini-3-flash-preview:generateContent"
    headers = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            try:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            except:
                return "解析失败，请重试"
        return f"API请求失败: {response.status_code}"
    except Exception as e:
        return f"网络错误: {e}"

def analyze_data(df):
    data_str = df.head(50).to_string()
    prompt = f"""
    你是一位小红书专家。请根据 CSV 数据（前50行）进行诊断。
    数据内容：{data_str}
    请输出 Markdown 报告：
    1. 📊 账号现状速览
    2. 🔥 爆款笔记复盘
    3. 🚀 下阶段增长策略
    """
    return call_custom_api(prompt)

# (B) 后台业务：卡密生成
def generate_codes(count=200, length=8):
    chars = string.ascii_uppercase + string.digits 
    codes = set()
    while len(codes) < count:
        code = ''.join(random.choices(chars, k=length))
        codes.add(code)
    return list(codes)

# --- 3. Streamlit 页面 UI ---

st.set_page_config(page_title="小红书爆款挖掘机", page_icon="🚀", layout="centered")

# 初始化 Session State
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'report_content' not in st.session_state:
    st.session_state.report_content = ""

# =========================================================
# 🔐 侧边栏：身份验证 (增加了表单和按钮)
# =========================================================
with st.sidebar:
    st.header("🔐 身份验证")
    
    # --- 核心修改：使用 Form 表单 ---
    with st.form("login_form"):
        # 输入框
        input_code = st.text_input("请输入卡密 (CDK)", type="password", help="输入后点击下方按钮验证")
        # 这是一个显眼的提交按钮
        submitted = st.form_submit_button("🔴 点击验证 / 登录")
    
    # 如果已经分析过了，显示重置按钮
    if st.session_state.analyzed:
        st.markdown("---")
        if st.button("🔄 重置 / 退出"):
            st.session_state.analyzed = False
            st.rerun()

# =========================================================
# 🎛️ 核心逻辑分流
# =========================================================

# 只有当 input_code 有值（用户按了回车或点了按钮）时才进行判断
if input_code:
    
    # --- 情况 A：管理员登录 ---
    if input_code == ADMIN_PASSWORD:
        st.title("🏭 管理员后台 (Secret Factory)")
        st.success(f"🔓 管理员身份已验证")
        st.markdown("---")
        
        st.subheader("🛠️ 生产新卡密")
        col1, col2 = st.columns(2)
        with col1:
            gen_count = st.number_input("生成数量", value=200, step=50)
        with col2:
            gen_len = st.number_input("卡密长度", value=8)
            
        if st.button("立即生产 🚀"):
            new_codes = generate_codes(gen_count, gen_len)
            
            # 显示 Secrets 格式
            st.text_area("复制到 Secrets (VALID_CODES):", ",".join(new_codes), height=100)
            
            # 下载 CSV
            df_codes = pd.DataFrame(new_codes, columns=["卡密"])
            csv = df_codes.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 下载 Excel/CSV", csv, f"新卡密_{len(new_codes)}.csv", "text/csv")

    # --- 情况 B：普通用户登录 ---
    elif input_code in VALID_CODES:
        st.title("🚀 小红书账号深度诊断 AI")
        st.markdown("上传数据，一键生成深度诊断报告。")

        uploaded_file = st.file_uploader("📂 请上传 CSV", type=['csv'])

        if not st.session_state.analyzed:
            # 只有验证通过了，才显示开始按钮
            if st.button("开始挖掘 (Start) 🚀"):
                if not uploaded_file:
                    st.warning("⚠️ 请先上传 CSV 文件！")
                else:
                    status_box = st.empty()
                    try:
                        status_box.info("📊 读取数据中...")
                        df = pd.read_csv(uploaded_file)
                        status_box.info("🧠 AI 正在分析...")
                        report = analyze_data(df)
                        
                        if "失败" in report or "错误" in report:
                            status_box.error(report)
                        else:
                            st.session_state.analyzed = True
                            st.session_state.report_content = report
                            st.rerun()
                    except Exception as e:
                        status_box.error(f"❌ 发生错误: {e}")

        # 结果展示
        if st.session_state.analyzed:
            st.success("✅ 分析完成！")
            file_name = f"诊断报告_{int(time.time())}.md"
            st.download_button("📥 下载报告", st.session_state.report_content, file_name)
            st.markdown(st.session_state.report_content)
    
    # --- 情况 C：卡密错误 ---
    else:
        st.error("❌ 卡密无效！请检查是否输入正确。")
        st.info("提示：输入卡密后，请点击上方的“🔴 点击验证”按钮。")

# --- 还没有输入时的默认提示 ---
else:
    st.title("🚀 小红书账号深度诊断 AI")
    st.info("👋 请在左侧侧边栏输入卡密，并点击 **“点击验证”** 按钮进入系统。")
