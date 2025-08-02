import streamlit as st
from tinydb import TinyDB
import pandas as pd
import plotly.express as px

# ✅ 1. TinyDB 데이터 읽기
db = TinyDB(r"D:\json\work\python\Test\json_db.json", encoding='utf-8-sig')
records = db.all()
df = pd.DataFrame(records)

print("aaaaaaa:", db.all())

# ✅ 2. 사이드바 UI
st.sidebar.header("📊 가계부 필터")
years = sorted(df['연도'].unique())
selected_year = st.sidebar.selectbox("연도 선택", years)
months = sorted(df[df['연도'] == selected_year]['월'].unique())
selected_month = st.sidebar.selectbox("월 선택", months)
categories = ["전체"] + sorted(df['카테고리'].unique())
selected_category = st.sidebar.selectbox("카테고리 선택", categories)

# ✅ 3. 페이지 제목
st.title("💰 가계부 대시보드")
st.write(f"### {selected_year}년 {selected_month}월 요약")

# ✅ 4. 선택된 월 데이터 필터링
month_df = df[(df['연도'] == selected_year) & (df['월'] == selected_month)]

# ✅ 5. 카테고리별 합계 + hover 표시할 세부내용 만들기
summary = month_df.groupby('카테고리')['금액'].sum().reset_index()
hover_df = month_df.groupby('카테고리').apply(
    lambda g: "<br>".join([f"{row.내역}: {row.금액:,}원" for _, row in g.iterrows()])
).reset_index(name="세부내역")
merged = summary.merge(hover_df, on="카테고리", how="left")

# ✅ 6. DataFrame 출력
st.subheader("📋 카테고리별 합계")
st.dataframe(merged)

# ✅ 7. Bar Chart
bar_fig = px.bar(
    merged, x='카테고리', y='금액', text='금액',
    color='카테고리',
    hover_data={'세부내역': True, '금액': ':.0f'},
    title=f"{selected_year}년 {selected_month}월 카테고리별 지출",
    color_discrete_sequence=px.colors.qualitative.Set3
)
bar_fig.update_traces(texttemplate='%{text:,}원', textposition='outside',
                      hovertemplate="<b>%{x}</b><br>총 지출: %{y:,}원<br><br>%{customdata[0]}")
st.plotly_chart(bar_fig)

# ✅ 8. Pie Chart
pie_fig = px.pie(
    merged, names='카테고리', values='금액',
    hover_data={'세부내역': True},
    title=f"{selected_year}년 {selected_month}월 카테고리 비율",
    color_discrete_sequence=px.colors.qualitative.Set3
)
pie_fig.update_traces(textinfo='label+percent',
                      hovertemplate="<b>%{label}</b><br>총 지출: %{value:,}원<br><br>%{customdata[0]}",
                      pull=[0.05]*len(merged))
st.plotly_chart(pie_fig)

# ✅ 9. 월별 총지출 라인 그래프
st.subheader("📈 월별 총지출 추이")
trend = df.groupby(['연도','월'])['금액'].sum().reset_index()
trend['연월'] = trend['연도'].astype(str) + "-" + trend['월'].astype(str).str.zfill(2)

trend_fig = px.line(trend, x='연월', y='금액', markers=True, text='금액',
                    title="📈 월별 총 지출 추이")
trend_fig.update_traces(texttemplate='%{text:,}원', textposition="top center")
st.plotly_chart(trend_fig)

# ✅ 10. 특정 카테고리 상세내역 (필터 적용)
if selected_category != "전체":
    st.subheader(f"🔍 {selected_category} 상세 내역")
    cat_df = month_df[month_df['카테고리'] == selected_category]
    detail_summary = cat_df.groupby('내역')['금액'].sum().reset_index()

    st.dataframe(detail_summary)

    detail_fig = px.bar(
        detail_summary, x='내역', y='금액', text='금액',
        color='내역',
        title=f"{selected_category} 카테고리 상세 내역",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    detail_fig.update_traces(texttemplate='%{text:,}원', textposition='outside')
    st.plotly_chart(detail_fig)
