import streamlit as st
import pandas as pd
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time
import random

# --- 1. 配置读取 ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    GMAIL_USER = st.secrets["GMAIL_USER"]
    GMAIL_PASSWORD = st.secrets["GMAIL_PASSWORD"]
    VALID_CODES = st.secrets["VALID_CODES"].split(",")
except Exception as e:
    st.error(f"请在 Streamlit 后台配置 Secrets 密钥！错误: {e}")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. 核心功能函数 ---

def send_email(to_email, report_content):
    """发送邮件功能"""
    msg = MIMEMultipart()
    msg['From'] = Header("小红书AI分析师", 'utf-8')
    msg['To'] = to_email
    msg['Subject'] = Header("【分析完成】您的账号诊断报告", 'utf-8')
    
    html_content = f"""
    <div style="font-family: sans-serif; padding: 20px; color: #333;">
        <h2 style="color: #FF2442;">📊 您的账号诊断报告已生成</h2>
        <hr style="border: 1px solid #eee;">
        <div style="white-space: pre-wrap; background-color: #f9f9f9; padding: 15px; border-radius: 5px; line-height: 1.6;">
        {report_content}
        </div>
        <hr style="border: 1px solid #eee;">
        <p style="color: gray; font-size: 12px;">此报告由 AI 自动生成，仅供参考。</p>
    </div>
    """
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

def analyze_data_with_retry(df):
    """带重试机制的 AI 分析"""
    data_str = df.head(40).to_string() # 稍微减少行数，节省 Token，防止限流
    
    prompt = f"""
    你是一位小红书专家。请根据这份 CSV 数据（前40行）进行诊断。
    数据内容：
    {data_str}
    
    请输出 Markdown 报告：
    1. 账号现状诊断（流量/人设）
    2. 爆款逻辑复盘（标题/选题）
    3. 3条改进建议
    """
    
    # 使用你列表里有的 "Flash Lite" 模型，它是最轻量的，最不容易 429
    model = genai.GenerativeModel("models/gemini-2.0-flash-lite-preview-02-05")
    
    # --- 智能重试循环 (核心防报错逻辑) ---
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 尝试请求
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            # 如果是 429 (限流) 或者是 503 (服务器忙)
            if "429" in error_msg or "503" in error_msg:
                wait_time = 5 + (attempt * 2) # 第一次等5秒，第二次等7秒...
                st.warning(f"⏳ 遇流控限制，系统正在自动重试 (第 {attempt+1}/{max_retries} 次)... 请耐心等待 {wait_time} 秒")
                time.sleep(wait_time)
            else:
                # 如果是其他错误，直接报错
                raise e
    
    return "⚠️ 系统繁忙，重试 3 次后仍被限制。请过 5 分钟后再试。"

# --- 3. Streamlit 页面 UI ---

st.set_page_config(page_title="小红书爆款挖掘机", page_icon="🚀")
st.title("🚀 小红书账号深度诊断 AI")

with st.sidebar:
    st.header("🔐 身份验证")
    input_code = st.text_input("请输入卡密", type="password")
    user_email = st.text_input("接收邮箱")

uploaded_file = st.file_uploader("📂 上传 CSV", type=['csv'])

if st.button("开始挖掘 🚀"):
    if not uploaded_file or not input_code or not user_email:
        st.warning("⚠️ 请补全所有信息！")
    elif input_code.strip() not in VALID_CODES:
        st.error("❌ 卡密无效！")
    else:
        status_box = st.empty()
        try:
            status_box.info("📊 读取数据中...")
            df = pd.read_csv(uploaded_file)
            
            status_box.info("🧠 AI 正在分析 (若遇卡顿会自动重试)...")
            report = analyze_data_with_retry(df)
            
            if "⚠️" in report:
                status_box.error(report)
            else:
                status_box.info("📧 发送邮件中...")
                if send_email(user_email, report):
                    status_box.success(f"✅ 成功！报告已发至 {user_email}")
                    st.balloons()
                    st.markdown("### 报告预览")
                    st.markdown(report)
                else:
                    status_box.error("❌ 邮件发送失败")
                    
        except Exception as e:
            status_box.error(f"❌ 发生错误: {e}")
