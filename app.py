import streamlit as st
import pandas as pd
import requests  # 使用基础请求库，1:1 复刻 Curl
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time

# --- 1. 配置读取 ---
try:
    # 这里填你买的中转 API Key
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    GMAIL_USER = st.secrets["GMAIL_USER"]
    GMAIL_PASSWORD = st.secrets["GMAIL_PASSWORD"]
    VALID_CODES = st.secrets["VALID_CODES"].split(",")
except Exception as e:
    st.error(f"请在 Streamlit 后台配置 Secrets 密钥！错误: {e}")
    st.stop()

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

def call_custom_api(prompt):
    """
    使用 requests 库直接模拟 Curl 命令调用中转接口
    目标地址: https://api.gptsapi.net/v1beta/models/gemini-3-flash-preview:generateContent
    """
    url = "https://api.gptsapi.net/v1beta/models/gemini-3-flash-preview:generateContent"
    
    # 构造请求头 (Header)，对应 Curl 中的 -H
    headers = {
        "x-goog-api-key": API_KEY,  # 这里用 x-goog-api-key，对应 Curl 示例
        "Content-Type": "application/json"
    }
    
    # 构造请求体 (Body)，对应 Curl 中的 --data-raw
    # 这是 Google 原生的格式，不是 OpenAI 的格式
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    try:
        # 发送 POST 请求
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        # 检查是否成功
        if response.status_code == 200:
            result = response.json()
            # 解析 Google 格式的返回结果
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return f"解析失败，API 返回结构异常: {result}"
        else:
            return f"API 请求失败 (状态码 {response.status_code}): {response.text}"
            
    except Exception as e:
        return f"网络请求出错: {e}"

def analyze_data(df):
    """数据处理与 Prompt 构建"""
    data_str = df.head(50).to_string()
    
    prompt = f"""
    你是一位小红书专家。请根据这份 CSV 数据（前50行）进行诊断。
    数据内容：
    {data_str}
    
    请输出 Markdown 报告：
    1. 账号现状诊断
    2. 爆款逻辑复盘
    3. 3条改进建议
    """
    
    return call_custom_api(prompt)

# --- 3. Streamlit 页面 UI ---

st.set_page_config(page_title="小红书爆款挖掘机", page_icon="🚀")
st.title("🚀 小红书账号深度诊断 AI (Gemini 3 Preview)")

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
            
            status_box.info("🧠 AI (Gemini 3 Flash) 正在分析...")
            report = analyze_data(df)
            
            if "API 请求失败" in report or "网络请求出错" in report:
                status_box.error(report)
            else:
                status_box.info("📧 发送邮件中...")
                if send_email(user_email, report):
                    status_box.success(f"✅ 成功！报告已发至 {user_email}")
                    st.markdown("### 报告预览")
                    st.markdown(report)
                else:
                    status_box.error("❌ 邮件发送失败")
                    
        except Exception as e:
            status_box.error(f"❌ 发生错误: {e}")
