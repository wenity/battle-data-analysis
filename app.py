import streamlit as st
import pandas as pd
import plotly.express as px
import time

# 基础页面配置
st.set_page_config(page_title="部落战统计数据看板", layout="wide")

st.title("⚔️ 部落战统计可视化智能看板")
st.markdown("通过侧边栏上传最新导出的Excel统计文件，即可生成可视化图表与智能趋势报告。")

def process_data(df):
    """
    专门针对本次工作区文件的特定数据清洗逻辑
    """
    # 提取“总部”数据（前9列）并清洗
    hq_df = df.iloc[:, 0:9].copy()
    hq_df.columns = ["序号", "玩家ID", "第1次进攻_目标", "第1次_摧毁率", "第1次_星数", "第2次进攻_目标", "第2次_摧毁率", "第2次_星数", "总星"]
    hq_df = hq_df.dropna(subset=["玩家ID"])  # 清除空行
    hq_df["部门"] = "总部"
    
    # 提取“分部”数据（第10到18列左右），如果有的话
    branch_df = pd.DataFrame()
    if len(df.columns) > 18:
        branch_df = df.iloc[:, 10:19].copy()
        branch_df.columns = ["序号", "玩家ID", "第1次进攻_目标", "第1次_摧毁率", "第1次_星数", "第2次进攻_目标", "第2次_摧毁率", "第2次_星数", "总星"]
        branch_df = branch_df.dropna(subset=["玩家ID"])
        branch_df["部门"] = "分部"
    
    # 合并数据
    full_df = pd.concat([hq_df, branch_df], ignore_index=True)
    
    # 格式化数据类型
    for col in ["第1次_摧毁率", "第2次_摧毁率"]:
        full_df[col] = pd.to_numeric(full_df[col], errors='coerce').fillna(0)
    full_df["总摧毁率"] = full_df["第1次_摧毁率"] + full_df["第2次_摧毁率"]
    full_df["总星"] = pd.to_numeric(full_df["总星"], errors='coerce').fillna(0)
    
    return full_df

# 左侧侧边栏：文件上传
with st.sidebar:
    st.header("📊 数据源管理")
    uploaded_file = st.file_uploader("上传 Excel 统计表", type=["xlsx", "xls"])
    st.info("💡 提示：使用具有 `header=1` 格式的标准化部落战导出数据。如果是初次测试，可直接使用工作区文件。")

if uploaded_file:
    # --- 1. 读取并清洗数据 ---
    try:
        # 第2行才是真实的列名
        raw_df = pd.read_excel(uploaded_file, header=1) 
        clean_df = process_data(raw_df)
        st.success("✅ 数据读取并清洗成功！")
    except Exception as e:
        st.error(f"数据解析失败，请检查文件格式。错误信息: {e}")
        st.stop()

    # --- 2. 核心数据指标卡片 ---
    st.markdown("### 🏆 核心战况概览")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总参战人数", len(clean_df))
    col2.metric("获得总星星数", int(clean_df["总星"].sum()))
    col3.metric("满星(6星)玩家数", len(clean_df[clean_df["总星"] == 6]))
    
    # 计算均摧毁率（简单平均）
    avg_des = (clean_df["总摧毁率"] / 2).mean() * 100
    col4.metric("平均每次攻击摧毁率", f"{avg_des:.1f}%")
    
    # --- 3. 可视化图表 ---
    st.markdown("### 📈 成员战绩可视化")
    
    tab1, tab2, tab3 = st.tabs(["🌟 星数排行榜", "🔥 摧毁率排行榜", "🗂️ 原始数据表"])
    
    with tab1:
        # 星数排行
        star_df = clean_df.sort_values(by="总星", ascending=False)
        fig1 = px.bar(star_df, x="玩家ID", y="总星", color="部门", 
                     title="成员总获得星数排行", height=500)
        st.plotly_chart(fig1, use_container_width=True)
        
    with tab2:
        # 摧毁率排行
        des_df = clean_df.sort_values(by="总摧毁率", ascending=False)
        fig2 = px.bar(des_df, x="玩家ID", y="总摧毁率", color="部门", 
                     title="成员累计摧毁率排行 (以小数计, 满值为2.0)", height=500)
        st.plotly_chart(fig2, use_container_width=True)
        
    with tab3:
        st.dataframe(clean_df, use_container_width=True)


    # --- 4. 生成 AI 分析报告 ---
    st.markdown("### 🤖 智能趋势与作战分析报告")
    
    # 模拟大模型调用流程 (你可以后续替换成真实模型API)
    st.caption("🔍 正在调用大模型对当前战绩进行分析...")
    
    if st.button("生成/刷新智能分析报告", type="primary"):
        with st.spinner("AI 正在总结作战趋势..."):
            time.sleep(2) # 模拟网络请求
            
            # 这里构建给大模型的 Prompt
            prompt_data = clean_df.head(10).to_dict(orient="records")
            
            # --- 以下建议接入 DeepSeek / 阿里千问 API ---
            # 模拟大模型返回结果
            mock_report = f"""
**作战指挥部 AI 分析简报**：

1. **整体表现分析**：当前参战的 {len(clean_df)} 名队员中，获得 6 星的玩家有 {len(clean_df[clean_df["总星"] == 6])} 名，表现非常优异。总部的核心输出力量稳定，分部的平均进度稍具潜力，但整体攻坚能力很强。
2. **需要关注的短板**：部分队员第一次进攻获得满星，但第二次进攻（摧毁率）表现滑坡，建议指挥官关注补刀选人和目标分配，避免高战力打低本导致战力溢出。
3. **战术优化建议**：对于目前星数低于 2 星的队员，建议下一场安排导师进行针对性配兵指导。 
            """
            st.info(mock_report)
else:
    st.info("👆 请在左侧侧边栏上传你的 `部落战统计_金雄.xlsx` 开始体验。")
