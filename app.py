import streamlit as st
import pandas as pd
import requests
import time
import random
import string

# --- 1. 配置读取 ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    if "VALID_CODES" in st.secrets:
        VALID_CODES = st.secrets["VALID_CODES"].split(",")
    else:
        VALID_CODES = []
except Exception as e:
    VALID_CODES = []

# ==========================================
# 🛑 管理员专用密码
ADMIN_PASSWORD = "admin_boss_888" 
# ==========================================

# --- 2. 核心功能函数 ---

def call_custom_api(prompt):
    """调用 Gemini 3 Flash Preview 接口"""
    url = "https://api.gptsapi.net/v1beta/models/gemini-3-flash-preview:generateContent"
    headers = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            try:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            except:
                return "解析失败，请重试。可能是数据量过大或模型繁忙。"
        return f"API请求失败: {response.status_code}"
    except Exception as e:
        return f"网络错误: {e}"

def generate_analysis_prompt(mode, df_a, df_b=None):
    """
    根据模式生成极度严苛的 System Prompt
    """
    
    # 数据预处理：转字符串
    data_a_str = df_a.head(50).to_string()
    data_b_str = df_b.head(50).to_string() if df_b is not None else "无"

    # 基础禁区与目标设定
    base_instructions = """
    你是一个极度冷静、反焦虑、反盲从的数据结构分析师。
    你的目标：不是“教用户怎么火”，而是输出“结构性代价”。
    你的禁区：严禁输出任何可直接照搬的选题清单、标题公式、脚本模板、Prompt或操作步骤。
    严禁出现“厉害/值得/高级/优秀”等评价性词汇。只做描述与拆分。
    """

    if mode == "单账号拆解":
        # --- 单账号逻辑 ---
        prompt = f"""
        {base_instructions}
        
        【输入数据】
        目标账号数据（前50条）：
        {data_a_str}

        【输出任务】
        请严格按照以下 5 个步骤输出 Markdown 报告：

        ### 1. 数据快照 (冷静观察)
        * 输出6行关键指标（如：发帖频率、周期性、内容类型占比、互动中位数、爆款占比、TopN帖子贡献度）。
        * 只描述分布与结构，不评价好坏。

        ### 2. 吸引力解剖 (他凭什么)
        * 从数据模式推断“吸引力来源”，只能选 1–2 个核心点（如：确定感、信息差、视觉奇观、情绪缓解、产品化叙事）。
        * 必须给出数据证据。

        ### 3. 模仿代价 (Top 5 不可复制性清单)
        * 输出 5 条“不能抄”的点。每条格式必须是：
          **差异点** → **抄的代价** (现实代价：时间/信任/资源/闭环) → **数据证据** → **等价替代** (同目标不同路径的结构替代，不是模仿技巧)。
        * 约束：不能写“你认知不够”，必须落在现实成本上。

        ### 4. 如果非要走 (唯一现实路径)
        * 只给一条路径，格式必须包含：
          * **你必须接受**：[具体的周期或反馈特征]
          * **你必须放弃**：[某种优势或幻想]
          * **你必须坚持**：[某个不可逆条件]
        * 要求：高代价、慢反馈、不可浪漫化。

        ### 5. 结语立场
        * 输出3句简短的立场句，强调“我拆的是不能抄的部分”。
        """
        return prompt

    else:
        # --- 双账号对比逻辑 (A vs B) ---
        prompt = f"""
        {base_instructions}

        【输入数据】
        大佬A表 (目标账号)：
        {data_a_str}
        
        自己B表 (当前账号)：
        {data_b_str}

        【输出任务】
        请进行“结构差异诊断”，严格按照以下结构输出 Markdown 报告：

        ### 1. 结构差异诊断 (最狠的结论)
        * 用 3 句话直击要害：**B抄A最先死在哪？**
        * 不要讲情绪，只讲结构点（如：基线差异、资源错配、内容寿命）。

        ### 2. 结构差异清单 Top7
        * 列出 7 条核心差异，每条格式：
          **维度**：A是什么 / B是什么 / 这意味着什么代价 (时间/信任/资源/闭环)。
        * 覆盖维度：位置差异(信任代理)、节奏差异(可持续性)、内容寿命(长尾)、资源差异(信息差)、闭环差异(产品化)。

        ### 3. 不可复制性与替代方案
        * 针对上述差异，给出“等价替代”方案。
        * 必须是“结构替代路径”，避免变成抄作业。

        ### 4. 如果非要走 (唯一现实路径)
        * 针对 B 的现状，给出一条路径：
          * **你必须接受**：X
          * **你必须放弃**：Y
          * **你必须坚持**：Z

        ### 5. 最小输出骨架 (总结)
        * 数据快照 (6行对比)
        * 吸引力解剖 (A的吸引力核心)
        * 立场句 (3条)
        """
        return prompt

def generate_codes(count=200, length=8):
    """后台功能：批量生成卡密"""
    chars = string.ascii_uppercase + string.digits 
    codes = set()
    while len(codes) < count:
        code = ''.join(random.choices(chars, k=length))
        codes.add(code)
    return list(codes)

# --- 3. Streamlit 页面 UI ---

st.set_page_config(page_title="别抄了吧 - 结构性拆解工具", page_icon="🛑", layout="centered")

if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'report_content' not in st.session_state:
    st.session_state.report_content = ""

# =========================================================
# 🔐 侧边栏：身份验证
# =========================================================
with st.sidebar:
    st.header("🔐 身份验证")
    with st.form("login_form"):
        input_code = st.text_input("请输入卡密", type="password")
        submitted = st.form_submit_button("🔴 点击验证 / 进入")
    
    if st.session_state.analyzed:
        st.markdown("---")
        if st.button("🔄 重置 / 换个号拆"):
            st.session_state.analyzed = False
            st.session_state.report_content = ""
            st.rerun()

# =========================================================
# 🎛️ 核心逻辑
# =========================================================

if input_code:
    # --- 管理员模式 ---
    if input_code == ADMIN_PASSWORD:
        st.title("🏭 管理员后台")
        if st.button("生产 200 个卡密"):
            codes = generate_codes()
            st.text_area("复制到 Secrets:", ",".join(codes))
            
    # --- 用户模式 ---
    elif input_code in VALID_CODES:
        st.title("🛑 别抄了吧")
        st.caption("研究爆款，是创作者最体面的拖延方式。")
        st.markdown("---")

        # 🔵 核心功能：模式选择
        mode = st.radio(
            "选择拆解模式：",
            ("单账号拆解 (只看大佬)", "双账号诊断 (大佬A vs 自己B)"),
            horizontal=True
        )

        # 📂 文件上传区
        df_a = None
        df_b = None
        
        if mode == "单账号拆解 (只看大佬)":
            st.info("💡 请上传【大佬A】的数据表 (CSV)")
            file_a = st.file_uploader("上传目标账号数据", type=['csv'], key="file_a")
            if file_a:
                df_a = pd.read_csv(file_a)
                
        else:
            st.info("💡 请分别上传【大佬A】和【你自己B】的数据表，进行残酷对比。")
            col1, col2 = st.columns(2)
            with col1:
                file_a = st.file_uploader("上传大佬A数据 (目标)", type=['csv'], key="file_a_dual")
            with col2:
                file_b = st.file_uploader("上传自己B数据 (现状)", type=['csv'], key="file_b_dual")
            
            if file_a and file_b:
                df_a = pd.read_csv(file_a)
                df_b = pd.read_csv(file_b)

        # 🚀 执行按钮
        if not st.session_state.analyzed:
            start_btn = st.button("开始冷峻拆解 (Start) 🛑")
            
            if start_btn:
                # 校验文件
                if mode == "单账号拆解 (只看大佬)" and df_a is None:
                    st.warning("⚠️ 请上传目标账号数据！")
                elif mode == "双账号诊断 (大佬A vs 自己B)" and (df_a is None or df_b is None):
                    st.warning("⚠️ 请确保两份数据都已上传！")
                else:
                    status_box = st.empty()
                    try:
                        status_box.info("📊 读取数据中...")
                        
                        # 生成对应的 Prompt
                        prompt = generate_analysis_prompt(mode.split()[0], df_a, df_b)
                        
                        status_box.info("🧠 正在进行结构性诊断... (过程可能有些刺痛，请忍耐)")
                        report = call_custom_api(prompt)
                        
                        if "失败" in report:
                            status_box.error(report)
                        else:
                            st.session_state.analyzed = True
                            st.session_state.report_content = report
                            st.rerun()
                    except Exception as e:
                        status_box.error(f"❌ 发生错误: {e}")

        # 📄 结果展示
        if st.session_state.analyzed:
            st.success("✅ 诊断完成。请查收你的结构性代价。")
            
            file_name = f"别抄了吧_{mode.split()[0]}_{int(time.time())}.md"
            st.download_button("📥 下载诊断报告 (.md)", st.session_state.report_content, file_name)
            
            st.markdown("---")
            st.markdown(st.session_state.report_content)

    else:
        st.error("❌ 卡密无效")

else:
    st.title("🛑 别抄了吧")
    st.markdown("### 在你准备照着别人来之前，先停一下。")
    st.info("👋 请输入卡密进入。")
