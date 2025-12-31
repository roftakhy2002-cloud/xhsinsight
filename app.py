import streamlit as st
import pandas as pd
import requests
import time
import random
import string

# --- 1. 配置读取 ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    # 容错处理：防止 secrets 里没有配置 VALID_CODES 时报错
    if "VALID_CODES" in st.secrets:
        VALID_CODES = st.secrets["VALID_CODES"].split(",")
    else:
        VALID_CODES = []
except Exception as e:
    VALID_CODES = []
    # 暂时不阻断，方便你先看到界面（实际部署时请务必配置 Secrets）

# ==========================================
# 🛑 管理员专用密码 (生成卡密用)
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
                return "解析失败，请重试"
        return f"API请求失败: {response.status_code}"
    except Exception as e:
        return f"网络错误: {e}"

def analyze_data(df):
    """
    核心逻辑：4步去热分析法
    将用户的‘模仿冲动’转化为‘清醒的代价权衡’
    """
    # 截取前 50 行，节省 Tokens 同时足够分析模式
    data_str = df.head(50).to_string()
    
    prompt = f"""
    你是一个【反焦虑、反盲从】的社交媒体观察者。
    你的任务不是分析“这个账号好在哪”，而是帮助用户完成一次“模仿前的冷静拆解”。
    
    请根据这份对标账号的数据（前50行），严格按照以下 4 个步骤输出 Markdown 报告。
    
    【核心原则】
    1. ❌ 禁止赞美：不要出现“优秀”、“精彩”、“值得学习”等评价性词汇。
    2. ❌ 禁止打鸡血：不要鼓励用户去尝试，保持冷静、克制、甚至略带冷峻的语调。
    3. ✅ 只做描述与代价揭示。

    数据内容：
    {data_str}
    
    【报告结构】
    
    ### STEP 1｜冷静观察（去热）
    * **不要给结论，不要给评价。**
    * 用像“法医”或“说明书”一样的口吻，客观描述这个账号在发什么、频率如何、数据分布如何。
    * 例如：“该账号主要发布XX类型的图文，平均每周更新X条，标题通常采用XX结构。”
    * 目的：让用户从“我也要火”回到“我到底在看什么”。

    ### STEP 2｜吸引力解剖（他凭什么）
    * **不是分析优点，是定位“诱因”。**
    * 一针见血地指出：这个账号到底是用什么钩子勾住了用户？
    * 是“通过制造容貌焦虑来吸引关注”？是“通过展示稀缺的财富生活制造羡慕”？还是“通过极端的观点制造对立”？
    * 目的：戳破幻想，指出用户其实是被什么情绪操纵了。

    ### STEP 3｜模仿的代价（这事难在哪）
    * **这是最关键的一步。不要问“能不能做”，要问“最先死在哪”。**
    * 直白地列出模仿这个账号的【隐性门槛】和【极高风险】。
    * 例如：需要极高的财力支撑？需要极强的镜头表现力（天赋）？还是需要极厚的时间成本？
    * 告诉用户：如果你的硬件/软件达不到XX标准，模仿出来的结果会是“东施效颦”。

    ### STEP 4｜如果非要走（责任声明）
    * **不给多选，不给对比，只给一条“高代价”的现实路径。**
    * 格式必须是：“如果你一定要走这条路，那你必须：”
        1. 先放弃 [具体的舒适区或幻想]
        2. 接受 [具体的枯燥过程或痛苦]
        3. 承担 [具体的失败风险]
    * 目的：让“走这条路”变成一次清醒的代价权衡，而不是脑热冲动。
    """
    return call_custom_api(prompt)

def generate_codes(count=200, length=8):
    """后台功能：批量生成卡密"""
    chars = string.ascii_uppercase + string.digits 
    codes = set()
    while len(codes) < count:
        code = ''.join(random.choices(chars, k=length))
        codes.add(code)
    return list(codes)

# --- 3. Streamlit 页面 UI ---

# 页面基础配置：红灯图标，红灯心态
st.set_page_config(page_title="别抄了吧 - 抄前自检工具", page_icon="🛑", layout="centered")

# 初始化 Session State (状态记忆)
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'report_content' not in st.session_state:
    st.session_state.report_content = ""

# =========================================================
# 🔐 侧边栏：身份验证区
# =========================================================
with st.sidebar:
    st.header("🔐 身份验证")
    
    with st.form("login_form"):
        input_code = st.text_input("请输入卡密", type="password", help="输入后点击下方按钮验证")
        submitted = st.form_submit_button("🔴 点击验证 / 进入")
    
    # 只有分析完成后才显示重置按钮
    if st.session_state.analyzed:
        st.markdown("---")
        st.info("如需分析新的账号，请点击重置。")
        if st.button("🔄 重置 / 退出"):
            st.session_state.analyzed = False
            st.rerun()

# =========================================================
# 🎛️ 核心逻辑分流
# =========================================================

if input_code:
    
    # --- 情况 A：管理员登录 (输入 admin_boss_888) ---
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
            
            # 1. 方便复制到 Secrets 的格式
            st.text_area("复制到 Secrets (VALID_CODES):", ",".join(new_codes), height=100)
            
            # 2. 方便发货的 Excel/CSV 格式
            df_codes = pd.DataFrame(new_codes, columns=["卡密"])
            csv = df_codes.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📥 下载 Excel/CSV (用于发卡网)",
                data=csv,
                file_name=f"新卡密_{len(new_codes)}个.csv",
                mime="text/csv"
            )

    # --- 情况 B：普通用户登录 (进入“别抄了吧”工具) ---
    elif input_code in VALID_CODES:
        # 首页文案：极简、有力
        st.title("🛑 别抄了吧")
        st.caption("在你准备照着别人来之前，先停一下。") 
        
        st.markdown("---")
        st.markdown("这是一个反焦虑工具。它不教你“怎么火”，只负责帮你**看清代价**。")
        st.info("💡 请上传你**原本打算模仿**的那个对标账号数据 (CSV)。")

        uploaded_file = st.file_uploader("📂 上传对标账号数据 (.csv)", type=['csv'])

        # 核心交互区
        if not st.session_state.analyzed:
            if st.button("开始拆解 (Start) 🛑"):
                if not uploaded_file:
                    st.warning("⚠️ 请先上传 CSV 文件！")
                else:
                    status_box = st.empty()
                    try:
                        status_box.info("📊 正在读取数据...")
                        df = pd.read_csv(uploaded_file)
                        
                        # 提示语修改，符合新调性
                        status_box.info("🧠 正在进行冷峻拆解... (不给建议，只给真相)")
                        report = analyze_data(df)
                        
                        if "失败" in report or "错误" in report:
                            status_box.error(report)
                        else:
                            st.session_state.analyzed = True
                            st.session_state.report_content = report
                            st.rerun()
                    except Exception as e:
                        status_box.error(f"❌ 发生错误: {e}")

        # 结果展示区
        if st.session_state.analyzed:
            st.success("✅ 拆解完成。请认真阅读下方的“责任声明”。")
            
            # 下载功能：文件名也必须“冷”
            file_name = f"别抄了吧_深度拆解_{int(time.time())}.md"
            
            st.download_button(
                label="📥 下载拆解报告 (.md)",
                data=st.session_state.report_content,
                file_name=file_name,
                mime="text/markdown"
            )
            
            st.markdown("---")
            st.markdown(st.session_state.report_content)
    
    # --- 情况 C：卡密错误 ---
    else:
        st.error("❌ 卡密无效")
        st.warning("请检查卡密是否输入正确，或联系管理员获取新卡密。")

# --- 还没有输入时的默认引导页 ---
else:
    st.title("🛑 别抄了吧")
    st.markdown("### 在你准备照着别人来之前，先停一下。")
    st.info("👋 请在左侧侧边栏输入卡密，并点击 **“点击验证”** 按钮开启抄前自检。")
