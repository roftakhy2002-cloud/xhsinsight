import streamlit as st
import pandas as pd
import requests
import time

# --- 1. 配置读取 ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    VALID_CODES = st.secrets["VALID_CODES"].split(",")
except Exception as e:
    st.error(f"请在 Streamlit 后台配置 Secrets 密钥！错误: {e}")
    st.stop()

# --- 2. 核心功能函数 ---
def call_custom_api(prompt):
    url = "https://api.gptsapi.net/v1beta/models/gemini-3-flash-preview:generateContent"
    headers = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return f"解析失败: {result}"
        else:
            return f"API 请求失败: {response.status_code}"
    except Exception as e:
        return f"网络请求出错: {e}"

def analyze_data(df):
    data_str = df.head(50).to_string()
    prompt = f"""
    你是一位小红书专家。请根据这份 CSV 数据（前50行）进行诊断。
    数据内容：{data_str}
    请输出 Markdown 报告：
    1. 📊 账号现状速览
    2. 🔥 爆款笔记复盘
    3. 🚀 下阶段增长策略
    """
    return call_custom_api(prompt)

# --- 3. Streamlit 页面 UI ---
st.set_page_config(page_title="小红书爆款挖掘机", page_icon="🚀", layout="centered")
st.title("🚀 小红书账号深度诊断 AI")
st.markdown("上传数据，一键生成深度诊断报告。**支持下载 Markdown 文件。**")

# --- 状态管理：初始化 session_state ---
# 这是一个“记忆”，用来记住用户是不是已经点过按钮了
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'report_content' not in st.session_state:
    st.session_state.report_content = ""

# 侧边栏
with st.sidebar:
    st.header("🔐 身份验证")
    input_code = st.text_input("请输入卡密 (CDK)", type="password")
    
    # 如果已经分析过了，显示重置按钮
    if st.session_state.analyzed:
        if st.button("🔄 重置/输入新卡密"):
            st.session_state.analyzed = False
            st.session_state.report_content = ""
            st.rerun()

uploaded_file = st.file_uploader("📂 请上传 CSV", type=['csv'])

# --- 核心逻辑区 ---

# 只有当没分析过的时候，才显示“开始挖掘”按钮
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
                
                status_box.info("🧠 AI 正在分析... (分析成功后按钮将锁定)")
                report = analyze_data(df)
                
                if "API 请求失败" in report or "网络请求出错" in report:
                    status_box.error(report)
                else:
                    # ✅ 成功！保存状态，并锁定
                    st.session_state.analyzed = True
                    st.session_state.report_content = report
                    st.rerun() # 强制刷新页面以显示结果区
                    
            except Exception as e:
                status_box.error(f"❌ 发生错误: {e}")

# --- 结果展示区 (分析成功后显示) ---
if st.session_state.analyzed:
    st.success("✅ 分析完成！(本页面已锁定，刷新可重新输入)")
    
    report = st.session_state.report_content
    file_name = f"小红书诊断报告_{int(time.time())}.md"
    
    st.download_button(
        label="📥 下载报告 (.md)",
        data=report,
        file_name=file_name,
        mime="text/markdown"
    )
    
    st.markdown("---")
    st.markdown(report)
