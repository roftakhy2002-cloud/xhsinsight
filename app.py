# ... 上面的代码不用动 ...

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
            
            status_box.info("🧠 AI (Gemini 3 Flash) 正在疯狂输出干货...")
            report = analyze_data(df)
            
            # 1. 检查 AI 是否报错
            if "API 请求失败" in report or "网络请求出错" in report:
                status_box.error(report)
            else:
                # 2. 【关键修改】AI 成功了！先直接展示结果，防丢！
                st.success("✅ AI 分析完成！")
                st.markdown("### 📊 账号诊断报告预览：")
                st.markdown(report) # 直接把报告打在屏幕上
                
                # 3. 然后再尝试发邮件
                status_box.info("📧 正在尝试发送邮件备份...")
                
                # 这里的逻辑：发邮件只是锦上添花，失败了也不影响看报告
                if send_email(user_email, report):
                    st.toast("✅ 邮件也发送成功了！", icon="🎉")
                else:
                    st.error("❌ 邮件发送失败（可能是密码有空格或配置不对），但你可以直接复制上面的报告。")
                    
        except Exception as e:
            status_box.error(f"❌ 发生错误: {e}")
