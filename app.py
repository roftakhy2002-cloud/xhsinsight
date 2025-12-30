import streamlit as st
import pandas as pd
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time

# --- 配置读取 ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    GMAIL_USER = st.secrets["GMAIL_USER"]
    GMAIL_PASSWORD = st.secrets["GMAIL_PASSWORD"]
    VALID_CODES = st.secrets["VALID_CODES"].split(",")
except:
    st.error("请在 Streamlit 后台配置 Secrets 密钥！")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# --- 功能函数 ---
def send_email(to_email, report_content):
    msg = MIMEMultipart()
    msg['From'] = Header("小红书AI分析师", 'utf-8')
    msg['To'] = to_email
    msg['Subject'] = Header("【分析完成】您的账号诊断报告", 'utf-8')
    
    html_content = f"<div style='white-space: pre-wrap;'>{report_content}</div>"
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

def analyze_data(df):
    data_str = df.head(50).to_string()
    prompt = f"作为小红书运营专家，请分析这份数据（前50条）：\n{data_str}\n请给出：1.账号现状诊断 2.爆款标题规律 3.三条改进建议。使用Markdown格式。"
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model.generate_content(prompt).text

# --- 页面 UI ---
st.title("🕵️‍♂️ 小红书账号诊断器")

with st.sidebar:
    input_code = st.text_input("请输入卡密", type="password")
    user_email = st.text_input("接收邮箱")

uploaded_file = st.file_uploader("上传 CSV 表格", type=['csv'])

if st.button("开始分析"):
    if not (uploaded_file and input_code and user_email):
        st.warning("请补全信息！")
    elif input_code not in VALID_CODES:
        time.sleep(2)
        st.error("卡密错误！")
    else:
        st.info("AI 正在分析，请稍候...")
        try:
            df = pd.read_csv(uploaded_file)
            report = analyze_data(df)
            if send_email(user_email, report):
                st.success(f"报告已发送至 {user_email}！")
                st.markdown(report)
            else:
                st.error("邮件发送失败，请检查邮箱。")
        except Exception as e:
            st.error(f"出错：{e}")
