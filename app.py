import streamlit as st
import pandas as pd
import requests
import time
import random
import string

# --- 1. 配置读取 ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    # 获取卡密列表
    VALID_CODES = st.secrets["VALID_CODES"].split(",")
except Exception as e:
    # 为了防止刚配置还没生效报错，给个默认空列表
    VALID_CODES = []
    st.error(f"请在 Streamlit 后台配置 Secrets！错误: {e}")

# ==========================================
# 🛑 管理员专用密码 (你自己设定一个复杂的)
# 当你在卡密输入框输入这个词时，会进入后台模式
ADMIN_PASSWORD = "admin_boss_888" 
# ==========================================

# --- 2. 功能函数定义 ---

# (A) 核心业务：AI 诊断
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
                return "解析失败"
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
    chars = string.ascii_uppercase + string.digits # 大写字母+数字
    codes = set() # 用集合自动去重
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

# --- 侧边栏身份验证 ---
with st.sidebar:
    st.header("🔐 身份验证")
    input_code = st.text_input("请输入卡密 (CDK)", type="password")
    
    # 只有分析完成后才显示重置按钮
    if st.session_state.analyzed:
        if st.button("🔄 重置"):
            st.session_state.analyzed = False
            st.rerun()

# =========================================================
# 🎛️ 核心逻辑分流：判断是“管理员”还是“普通用户”
# =========================================================

if input_code == ADMIN_PASSWORD:
    # >>>>> 进入管理员后台模式 <<<<<
    st.title("🏭 这里的秘密工厂 (管理员后台)")
    st.success(f"欢迎老板！当前系统已识别到管理员指令。")
    st.markdown("---")
    
    st.subheader("🛠️ 生产新卡密")
    col1, col2 = st.columns(2)
    with col1:
        gen_count = st.number_input("生成数量", value=200, step=50)
    with col2:
        gen_len = st.number_input("卡密长度", value=8)
        
    if st.button("立即生产 🚀"):
        new_codes = generate_codes(gen_count, gen_len)
        
        # 1. 显示给 Secrets 用的格式
        secrets_str = ",".join(new_codes)
        st.text_area("复制下面这段到 Streamlit Secrets (VALID_CODES):", secrets_str, height=100)
        
        # 2. 生成 CSV 供下载
        df_codes = pd.DataFrame(new_codes, columns=["卡密"])
        csv = df_codes.to_csv(index=False).encode('utf-8-sig')
        
        st.download_button(
            label="📥 下载 Excel/CSV (用于发卡网批量发货)",
            data=csv,
            file_name=f"新卡密_{len(new_codes)}个.csv",
            mime="text/csv"
        )
        st.balloons()

else:
    # >>>>> 进入普通用户模式 (原本的诊断工具) <<<<<
    st.title("🚀 小红书账号深度诊断 AI")
    st.markdown("上传数据，一键生成深度诊断报告。")

    uploaded_file = st.file_uploader("📂 请上传 CSV", type=['csv'])

    if not st.session_state.analyzed:
        if st.button("开始挖掘 (Start) 🚀"):
            if not uploaded_file or not input_code:
                st.warning("⚠️ 请输入卡密并上传文件！")
            elif input_code.strip() not in VALID_CODES:
                st.error("❌ 卡密无效！")
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
