import streamlit as st
import google.generativeai as genai

# 配置 Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("请先配置 Secrets!")
    st.stop()

st.title("🔍 模型可用性侦探")

if st.button("查看我现在能用哪些模型？"):
    try:
        st.write("正在连接 Google 服务器查询...")
        # 列出所有模型
        models = genai.list_models()
        
        found_any = False
        for m in models:
            # 只要显示支持 generateContent 的模型
            if 'generateContent' in m.supported_generation_methods:
                st.success(f"✅ 可用: {m.name}")
                found_any = True
        
        if not found_any:
            st.error("没有找到任何支持生成的模型！可能是 API Key 权限问题。")
            
    except Exception as e:
        st.error(f"查询失败: {e}")
