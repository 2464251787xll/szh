import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# 设置页面配置
st.set_page_config(
    page_title="企业数字化转型指数查询系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置matplotlib支持中文
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 加载数据
@st.cache_data
def load_data():
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建数据文件路径
    csv_path = os.path.join(script_dir, '两版合并后的年报数据_补全版.csv')
    
    try:
        # 检查文件是否存在
        if not os.path.exists(csv_path):
            # 列出当前目录内容，用于调试
            st.error(f"数据文件不存在: {csv_path}")
            st.error(f"当前目录内容: {os.listdir(script_dir)}")
            st.error(f"当前工作目录: {os.getcwd()}")
            return None
        
        # 读取CSV文件，先尝试utf-8编码
        df = pd.read_csv(csv_path, encoding='utf-8')
        return df
    except UnicodeDecodeError:
        try:
            # 尝试gbk编码
            df = pd.read_csv(csv_path, encoding='gbk')
            return df
        except Exception as e:
            st.error(f"读取CSV文件失败: {e}")
            st.error(f"文件路径: {csv_path}")
            st.error(f"文件是否存在: {os.path.exists(csv_path)}")
            if os.path.exists(csv_path):
                st.error(f"文件大小: {os.path.getsize(csv_path)} bytes")
            return None

# 主函数
def main():
    st.title("📊 企业数字化转型指数查询系统")
    st.markdown("---")
    
    # 加载数据
    df = load_data()
    
    if df is None:
        return
    
    # 获取所有股票代码和企业名称
    stock_codes = sorted(list(set(df['股票代码'].astype(str))))
    company_names = dict(zip(df['股票代码'].astype(str), df['企业名称']))
    
    # 创建侧边栏
    st.sidebar.header("🔍 查询条件")
    
    # 查询类型选择
    query_type = st.sidebar.radio(
        "查询类型:",
        ("单公司查询", "多公司对比分析")
    )
    
    selected_stocks = []
    
    if query_type == "单公司查询":
        # 股票代码查询方式
        query_option = st.sidebar.radio(
            "选择查询方式:",
            ("从列表选择", "自由输入")
        )
        
        stock_code = None
        
        if query_option == "从列表选择":
            stock_code = st.sidebar.selectbox(
                "选择股票代码:",
                options=[""] + stock_codes,
                format_func=lambda x: f"{x} - {company_names.get(x, '')}" if x else "-- 请选择 --"
            )
        else:
            stock_code = st.sidebar.text_input(
                "输入股票代码:",
                placeholder="如: 600000"
            )
        
        if stock_code:
            selected_stocks = [stock_code]
    
    else:  # 多公司对比分析
        # 支持选择多个股票代码
        selected_stocks = st.sidebar.multiselect(
            "选择要对比的股票代码:",
            options=stock_codes,
            format_func=lambda x: f"{x} - {company_names.get(x, '')}"
        )
    
    # 搜索按钮
    search_button = st.sidebar.button("查询", type="primary")
    
    # 清空按钮
    if st.sidebar.button("清空"):
        st.experimental_rerun()
    
    # 显示数据
    if search_button and selected_stocks:
        # 处理单公司查询
        if len(selected_stocks) == 1:
            stock_code = selected_stocks[0]
            company_data = df[df['股票代码'] == int(stock_code)]
            
            if not company_data.empty:
                # 获取公司基本信息
                company_name = company_data['企业名称'].iloc[0]
                years_available = sorted(list(company_data['年份']))
                
                st.header(f"📋 {company_name} ({stock_code}) 数字化转型指数")
                
                # 公司基本信息卡片
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.info(f"**企业名称:** {company_name}")
                    st.info(f"**股票代码:** {stock_code}")
                    st.info(f"**数据年份:** {min(years_available)} - {max(years_available)}")
                
                # 计算统计数据
                avg_index = company_data['数字化转型指数'].mean()
                max_index = company_data['数字化转型指数'].max()
                min_index = company_data['数字化转型指数'].min()
                
                # 显示统计数据卡片
                st.subheader("📈 数字化转型指数统计")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("平均指数", f"{avg_index:.2f}")
                with col2:
                    st.metric("最高指数", f"{max_index:.2f}")
                with col3:
                    st.metric("最低指数", f"{min_index:.2f}")
                
                # 显示详细数据表格
                st.subheader("📅 每年数字化转型指数")
                display_columns = ['年份', '技术维度', '应用维度', '词总', '数字化转型指数']
                st.dataframe(
                    company_data[display_columns].sort_values('年份'),
                    width='stretch',
                    hide_index=True
                )
                
                # 绘制趋势图
                st.subheader("📊 数字化转型指数趋势图")
                fig, ax = plt.subplots(figsize=(10, 5))
                
                company_data_sorted = company_data.sort_values('年份')
                ax.plot(
                    company_data_sorted['年份'],
                    company_data_sorted['数字化转型指数'],
                    marker='o',
                    linewidth=2,
                    color='#4CAF50'
                )
                
                # 设置字体属性
                font_properties = {'family': 'SimHei', 'size': 14}
                ax.set_title(f'{company_name} 数字化转型指数趋势', fontdict=font_properties)
                ax.set_xlabel('年份', fontdict={'family': 'SimHei', 'size': 12})
                ax.set_ylabel('数字化转型指数', fontdict={'family': 'SimHei', 'size': 12})
                ax.grid(True, alpha=0.3)
                ax.tick_params(axis='x', rotation=45)
                
                st.pyplot(fig)
                
                # 绘制技术维度与应用维度对比图
                st.subheader("📊 技术维度与应用维度对比")
                fig, ax = plt.subplots(figsize=(10, 5))
                
                width = 0.35
                x = np.arange(len(company_data_sorted['年份']))
                
                ax.bar(
                    x - width/2,
                    company_data_sorted['技术维度'],
                    width,
                    label='技术维度',
                    color='#36A2EB'
                )
                ax.bar(
                    x + width/2,
                    company_data_sorted['应用维度'],
                    width,
                    label='应用维度',
                    color='#FF6384'
                )
                
                # 设置字体属性
                font_properties = {'family': 'SimHei', 'size': 14}
                ax.set_title(f'{company_name} 技术维度与应用维度对比', fontdict=font_properties)
                ax.set_xlabel('年份', fontdict={'family': 'SimHei', 'size': 12})
                ax.set_ylabel('维度值', fontdict={'family': 'SimHei', 'size': 12})
                ax.set_xticks(x)
                ax.set_xticklabels(company_data_sorted['年份'], rotation=45, fontproperties={'family': 'SimHei', 'size': 10})
                ax.legend(prop={'family': 'SimHei', 'size': 12})
                ax.grid(True, alpha=0.3, axis='y')
                
                st.pyplot(fig)
                
                # 显示技术维度详细数据
                st.subheader("🔧 技术维度详细数据")
                tech_columns = ['年份', '人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数', '数字技术运用词频数', '技术维度']
                st.dataframe(
                    company_data[tech_columns].sort_values('年份'),
                    width='stretch',
                    hide_index=True
                )
                
            else:
                st.error(f"未找到股票代码为 {stock_code} 的公司数据！")
    
        else:  # 多公司对比分析
            if len(selected_stocks) >= 2:
                st.header(f"📊 多公司数字化转型指数对比分析")
                
                # 准备对比数据
                comparison_data = {}
                common_years = None
                
                for stock_code in selected_stocks:
                    company_data = df[df['股票代码'] == int(stock_code)].sort_values('年份')
                    if not company_data.empty:
                        company_name = company_data['企业名称'].iloc[0]
                        comparison_data[stock_code] = {
                            'name': company_name,
                            'data': company_data
                        }
                        
                        # 计算共同年份
                        years = set(company_data['年份'])
                        if common_years is None:
                            common_years = years
                        else:
                            common_years = common_years.intersection(years)
                
                if common_years and len(common_years) > 0:
                    common_years = sorted(list(common_years))
                    st.info(f"💡 共同数据年份: {min(common_years)} - {max(common_years)}")
                    
                    # 绘制多公司数字化转型指数趋势对比
                    st.subheader("📈 数字化转型指数趋势对比")
                    fig, ax = plt.subplots(figsize=(12, 6))
                    
                    colors = ['#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9C27B0', '#00BCD4']
                    color_idx = 0
                    
                    for stock_code, company_info in comparison_data.items():
                        company_name = company_info['name']
                        company_data = company_info['data']
                        
                        # 只使用共同年份的数据
                        filtered_data = company_data[company_data['年份'].isin(common_years)]
                        
                        ax.plot(
                            filtered_data['年份'],
                            filtered_data['数字化转型指数'],
                            marker='o',
                            linewidth=2,
                            label=f"{company_name} ({stock_code})")
                        color_idx += 1
                    
                    font_properties = {'family': 'SimHei', 'size': 14}
                    ax.set_title('多公司数字化转型指数趋势对比', fontdict=font_properties)
                    ax.set_xlabel('年份', fontdict={'family': 'SimHei', 'size': 12})
                    ax.set_ylabel('数字化转型指数', fontdict={'family': 'SimHei', 'size': 12})
                    ax.grid(True, alpha=0.3)
                    ax.tick_params(axis='x', rotation=45)
                    ax.legend(prop={'family': 'SimHei', 'size': 10})
                    
                    st.pyplot(fig)
                    
                    # 绘制特定年份对比柱状图
                    st.subheader("📊 特定年份数字化转型指数对比")
                    selected_year = st.selectbox("选择年份:", common_years)
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    bar_data = []
                    bar_labels = []
                    
                    for stock_code, company_info in comparison_data.items():
                        company_name = company_info['name']
                        company_data = company_info['data']
                        
                        year_data = company_data[company_data['年份'] == selected_year]
                        if not year_data.empty:
                            bar_data.append(year_data['数字化转型指数'].iloc[0])
                            bar_labels.append(f"{company_name}\n({stock_code})")
                    
                    ax.bar(
                        range(len(bar_data)),
                        bar_data,
                        color=colors[:len(bar_data)]
                    )
                    
                    ax.set_title(f'{selected_year}年 数字化转型指数对比', fontdict=font_properties)
                    ax.set_ylabel('数字化转型指数', fontdict={'family': 'SimHei', 'size': 12})
                    ax.set_xticks(range(len(bar_data)))
                    ax.set_xticklabels(bar_labels, rotation=45, ha='right', fontproperties={'family': 'SimHei', 'size': 10})
                    ax.grid(True, alpha=0.3, axis='y')
                    
                    # 添加数值标签
                    for i, v in enumerate(bar_data):
                        ax.text(i, v + 0.1, f"{v:.2f}", ha='center', va='bottom')
                    
                    st.pyplot(fig)
                    
                    # 显示各公司统计数据对比
                    st.subheader("📋 各公司统计数据对比")
                    stats_df = pd.DataFrame()
                    
                    for stock_code, company_info in comparison_data.items():
                        company_name = company_info['name']
                        company_data = company_info['data']
                        
                        # 只使用共同年份的数据
                        filtered_data = company_data[company_data['年份'].isin(common_years)]
                        
                        stats = {
                            '公司名称': company_name,
                            '股票代码': stock_code,
                            '平均指数': filtered_data['数字化转型指数'].mean(),
                            '最高指数': filtered_data['数字化转型指数'].max(),
                            '最低指数': filtered_data['数字化转型指数'].min(),
                            '指数增长趋势': filtered_data['数字化转型指数'].iloc[-1] - filtered_data['数字化转型指数'].iloc[0] if len(filtered_data) > 1 else 0
                        }
                        
                        # 将stats字典转换为DataFrame并合并
                        stats_series = pd.DataFrame([stats])
                        stats_df = pd.concat([stats_df, stats_series], ignore_index=True)
                    
                    if not stats_df.empty:
                        st.dataframe(
                            stats_df.sort_values('平均指数', ascending=False),
                            width='stretch',
                            hide_index=True
                        )
                    
                else:
                    st.warning("⚠️ 所选公司没有共同的数据年份，无法进行对比分析！")
            else:
                st.warning("⚠️ 请至少选择2家公司进行对比分析！")
    
    else:
        # 显示示例数据或说明
        st.info("请在左侧选择或输入股票代码，然后点击查询按钮查看数据。")
        
        # 显示数据统计信息
        st.subheader("📊 数据统计")
        total_companies = len(stock_codes)
        total_records = len(df)
        years_range = f"{df['年份'].min()} - {df['年份'].max()}"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("企业总数", total_companies)
        with col2:
            st.metric("数据记录总数", total_records)
        with col3:
            st.metric("数据年份范围", years_range)

if __name__ == "__main__":
    main()