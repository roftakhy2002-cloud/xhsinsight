import streamlit as st
import pandas as pd
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time

# --- 1. 配置读取 (Secrets) ---
try:
    # 必须在 Streamlit Cloud 后台配置这些 Secrets
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    GMAIL_USER = st.secrets["GMAIL_USER"]
    GMAIL_PASSWORD = st.secrets["GMAIL_PASSWORD"]
    # 卡密列表，用逗号分隔
    VALID_CODES = st.secrets["VALID_CODES"].split(",")
except Exception as e:
    st.error(f"请在 Streamlit 后台配置 Secrets 密钥！错误信息: {e}")
    st.stop()

# 配置 Google API
genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. 核心功能函数 ---

def send_email(to_email, report_content):
    """发送邮件功能"""
    msg = MIMEMultipart()
    msg['From'] = Header("小红书AI分析师", 'utf-8')
    msg['To'] = to_email
    msg['Subject'] = Header("【分析完成】您的账号诊断报告", 'utf-8')
    
    # 简单的 HTML 包装
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

def analyze_data(df):
    """调用 Gemini 进行分析"""
    data_str = df.head(50).to_string()
    
    prompt = f"""
    你是一位拥有10年经验的小红书顶级运营专家。请根据以下 CSV 数据（前50行）对该账号进行深度诊断。
    
    【数据内容】
    {data_str}
    
    【分析要求】
    请用 Markdown 格式输出一份报告，包含以下部分：
    1. 🕵️‍♂️ **账号现状诊断**：通过点赞数据判断其流量层级，通过标题风格判断其人设。
    2. 📈 **爆款逻辑复盘**：找出数据最好的 3 篇笔记，分析它们为什么火（标题公式、选题方向）。
    3. 💡 **未来增长建议**：给出 3 条具体的、可执行的选题建议。
    
    请语气专业、犀利，直接给出干货。
    """
    
    # --- 关键修正：使用你列表中存在的 models/gemini-flash-latest ---
    # 这个模型指向最新 Flash，既在你的列表里（不会404），额度也够用（不会429）
    model = genai.GenerativeModel("models/gemini-flash-latest")
    
    response = model.generate_content(prompt)
    return response.text

# --- 3. Streamlit 页面 UI ---

st.set_page_config(page_title="小红书爆款挖掘机", page_icon="🚀", layout="centered")

st.title("🚀 小红书账号深度诊断 AI")
st.markdown("上传 Instant Data Scraper 抓取的 CSV 表格，AI 自动分析并发送报告到您的邮箱。")

# 侧边栏：用户验证
with st.sidebar:
    st.header("🔐 身份验证")
    input_code = st.text_input("请输入卡密 (CDK)", type="password", help="请联系管理员获取")
    user_email = st.text_input("接收报告的邮箱")

# 主区域：文件上传
uploaded_file = st.file_uploader("📂 请上传 CSV 数据表", type=['csv'])

if st.button("开始挖掘 (Start) 🚀"):
    if not uploaded_file:
        st.warning("⚠️ 请先上传 CSV 文件！")
    elif not input_code:
        st.warning("⚠️ 请输入卡密！")
    elif not user_email:
        st.warning("⚠️ 请输入接收邮箱！")
    else:
        if input_code.strip() in VALID_CODES:
            status_box = st.empty()
            try:
                status_box.info("📊 正在读取数据...")
                df = pd.read_csv(uploaded_file)
                
                status_box.info("🧠 AI 正在深度思考... (约需 10-20 秒)")
                report = analyze_data(df)
                
                status_box.info("📧 报告生成完毕，正在发送邮件...")
                if send_email(user_email, report):
                    status_box.success(f"✅ 成功！深度诊断报告已发送至 {user_email}")
                    st.balloons()
                    with st.expander("点击预览报告内容"):
                        st.markdown(report)
                else:
                    status_box.error("❌ 邮件发送失败，请检查邮箱地址是否正确。")
                    
            except Exception as e:
                status_box.error(f"❌ 发生错误: {e}")
        else:
            time.sleep(2)
            st.error("❌ 卡密无效！")
