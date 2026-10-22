"""
========================================================================================
FINANCIAL RADAR & REAL-TIME VALUATION TERMINAL (BLOOMBERG STREAMLIT CLOUD EDITION)
Framework: Streamlit + Plotly + Multi-Agent Clean Architecture
Mô hình: 6-Domain Valuation Engines + Howard Schilit Forensic Audit + 10-Year Candlesticks
Dữ liệu: CSDL BCTC 16 Năm Lịch Sử (2010 - 2025) từ vietnam_stocks_16y.parquet
========================================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Đảm bảo đường dẫn import các package core, forensic, valuation
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from core.orchestrator import MasterOrchestrator
from core.data_engine import get_candlesticks

# 1. CẤU HÌNH TRANG STREAMLIT
st.set_page_config(
    page_title="Financial Radar • Bloomberg Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. BLOOMBERG TERMINAL DARK THEME CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    .stApp {
        background-color: #09090b;
        color: #f1f5f9;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .font-mono {
        font-family: 'JetBrains Mono', monospace;
    }
    div[data-testid="stMetric"] {
        background: rgba(18, 18, 24, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 18px;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(245, 158, 11, 0.4);
    }
    .cagr-box {
        background: rgba(18, 18, 24, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px;
        text-align: center;
    }
    .cagr-box:hover {
        border-color: rgba(245, 158, 11, 0.3);
    }
    .badge-sector {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #fbbf24;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
    }
    .flag-card {
        background: rgba(24, 24, 32, 0.9);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 4px solid #ef4444;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .flag-clean {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-left: 4px solid #10b981;
        border-radius: 10px;
        padding: 12px 16px;
        color: #34d399;
    }
</style>
""", unsafe_allow_html=True)

# 3. HEADER & TÌM KIẾM
st.markdown("""
<div style="display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #27272a; padding-bottom:12px; margin-bottom:16px;">
    <div>
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:24px;">⚡</span>
            <span style="font-size:18px; font-weight:900; font-family:'JetBrains Mono'; letter-spacing:1px; color:#f8fafc;">FINANCIAL RADAR TERMINAL</span>
            <span style="font-size:10px; font-family:'JetBrains Mono'; background:#27272a; color:#fbbf24; padding:2px 8px; border-radius:4px; font-weight:700;">BLOOMBERG EDITION</span>
        </div>
        <div style="font-size:11px; color:#71717a; font-family:'JetBrains Mono'; margin-top:2px;">
            6-Domain Architecture • Howard Schilit Shenanigans • 10-Year Candlesticks • 16-Year Parquet Core
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Gợi ý mã 6 miền ngành
cols_preset = st.columns(8)
presets = [
    ("VCB", "Ngân hàng"),
    ("VHM", "BĐS RNAV"),
    ("VIC", "Holding SOTP"),
    ("HPG", "Thép Chu kỳ"),
    ("FPT", "CFA 5-Tầng"),
    ("VSH", "Mùa vụ"),
    ("MWG", "Bán lẻ"),
    ("MSN", "Tiêu dùng")
]

selected_ticker = "HPG"
for idx, (t, lbl) in enumerate(presets):
    if cols_preset[idx].button(f"{t}", use_container_width=True, help=lbl):
        selected_ticker = t

# Thanh nhập mã cổ phiếu
col_input, col_btn = st.columns([4, 1])
with col_input:
    ticker_input = st.text_input("Nhập mã chứng khoán (HOSE, HNX, UPCoM):", value=selected_ticker).upper().strip()

if not ticker_input:
    st.info("Vui lòng nhập một mã cổ phiếu để bắt đầu phân tích.")
    st.stop()

# 4. CHẠY PHÂN TÍCH ĐA TÁC TỬ QUA MASTER ORCHESTRATOR
with st.spinner(f"Đang quét BCTC 16 năm và phân loại 6 miền ngành cho {ticker_input}..."):
    try:
        d = MasterOrchestrator.analyze(ticker_input)
    except Exception as e:
        st.error(f"Lỗi khi phân tích mã {ticker_input}: {e}")
        st.stop()

# 5. HIỂN THỊ HERO METRICS BAR
st.markdown(f"""
<div style="background:rgba(18,18,24,0.9); border:1px solid rgba(255,255,255,0.08); border-left:4px solid #f59e0b; border-radius:14px; padding:16px 20px; margin-bottom:16px;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div>
            <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                <span style="font-size:32px; font-weight:900; font-family:'JetBrains Mono'; color:#fbbf24;">{d['ticker']}</span>
                <span class="badge-sector">{d['archetype_label']}</span>
                <span style="font-size:11px; font-family:'JetBrains Mono'; color:#a1a1aa; border:1px solid #27272a; padding:2px 8px; border-radius:4px;">{d['data_source']}</span>
                <span style="font-size:11px; font-family:'JetBrains Mono'; color:#a1a1aa; border:1px solid #27272a; padding:2px 8px; border-radius:4px;">P/E: {d['pe']:.1f}x | P/B: {d['pb']:.1f}x</span>
            </div>
            <div style="font-size:16px; font-weight:700; color:#e2e8f0; margin-top:4px;">{d['company_name']}</div>
            <div style="font-size:12px; color:#71717a; margin-top:2px;">💡 <i>{d['engine_note']}</i></div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:11px; font-family:'JetBrains Mono'; color:#a1a1aa; text-transform:uppercase;">Thị Giá Real-time</div>
            <div style="font-size:30px; font-weight:900; font-family:'JetBrains Mono'; color:#ffffff;">{d['current_price']:,.0f} <span style="font-size:14px; font-weight:400; color:#71717a;">VND</span></div>
            <div style="font-size:14px; font-weight:900; font-family:'JetBrains Mono'; color:{'#34d399' if d['signal_color']=='emerald' else ('#fbbf24' if d['signal_color']=='amber' else '#f87171')};">
                {d['signal']} ({d['upside']:+.1f}%)
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 6. HỒ SƠ NĂNG LỰC 10-16 NĂM (WARREN BUFFETT ECONOMIC MOAT)
st.markdown("##### 🏆 HỒ SƠ NĂNG LỰC DÀI HẠN 10 - 16 NĂM (WARREN BUFFETT MOAT)")
tr = d['track_record_10y']
m1, m2, m3, m4 = st.columns(4)

with m1:
    rev_str = f"{tr['cagr_10y_rev']:+.1f}%/năm" if tr['cagr_10y_rev'] is not None else ("N/A (Ngân hàng)" if d['archetype']=='BANK' else "N/A")
    st.markdown(f"""<div class='cagr-box'>
        <div style='font-size:11px; color:#a1a1aa; font-family:"JetBrains Mono"; text-transform:uppercase; font-weight:700;'>📈 Doanh Thu 10Y CAGR</div>
        <div style='font-size:22px; font-weight:900; font-family:"JetBrains Mono"; color:#38bdf8; margin-top:4px;'>{rev_str}</div>
        <div style='font-size:10px; color:#71717a;'>Tăng trưởng mở rộng quy mô</div>
    </div>""", unsafe_allow_html=True)

with m2:
    ni_str = f"{tr['cagr_10y_ni']:+.1f}%/năm" if tr['cagr_10y_ni'] is not None else "N/A"
    st.markdown(f"""<div class='cagr-box'>
        <div style='font-size:11px; color:#a1a1aa; font-family:"JetBrains Mono"; text-transform:uppercase; font-weight:700;'>💰 LNST 10Y CAGR</div>
        <div style='font-size:22px; font-weight:900; font-family:"JetBrains Mono"; color:#34d399; margin-top:4px;'>{ni_str}</div>
        <div style='font-size:10px; color:#71717a;'>Tăng trưởng lợi nhuận gộp</div>
    </div>""", unsafe_allow_html=True)

with m3:
    roe_str = f"{tr['avg_roe_10y']:.1f}%" if tr['avg_roe_10y'] is not None else "N/A"
    st.markdown(f"""<div class='cagr-box'>
        <div style='font-size:11px; color:#a1a1aa; font-family:"JetBrains Mono"; text-transform:uppercase; font-weight:700;'>🎯 ROE Bình Quân 10 Năm</div>
        <div style='font-size:22px; font-weight:900; font-family:"JetBrains Mono"; color:#fbbf24; margin-top:4px;'>{roe_str}</div>
        <div style='font-size:10px; color:#71717a;'>Hiệu quả sinh lời vốn CSH</div>
    </div>""", unsafe_allow_html=True)

with m4:
    st.markdown(f"""<div class='cagr-box'>
        <div style='font-size:11px; color:#a1a1aa; font-family:"JetBrains Mono"; text-transform:uppercase; font-weight:700;'>🛡️ Cổ Tức Bền Vững</div>
        <div style='font-size:22px; font-weight:900; font-family:"JetBrains Mono"; color:#c084fc; margin-top:4px;'>{tr['div_consistency']}</div>
        <div style='font-size:10px; color:#71717a;'>Lịch sử chia tiền mặt</div>
    </div>""", unsafe_allow_html=True)

st.write("")

# 7. BIỂU ĐỒ NẾN 10 NĂM & RADAR GIAN LẬN 8 TRỤC BENEISH (HÀNG THỊ GIÁC ĐẦU TIÊN)
col_chart, col_radar = st.columns([3, 2])

with col_chart:
    st.markdown("##### 📊 BIỂU ĐỒ NẾN 10 NĂM & KHỐI LƯỢNG (PLOTLY INTERACTIVE)")
    candles = get_candlesticks(d['ticker'], years=10)
    if candles and len(candles) > 0:
        df_candles = pd.DataFrame(candles)
        df_candles['date'] = pd.to_datetime(df_candles['time'], unit='s')
        df_candles = df_candles.sort_values('date')

        fig_tv = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
        
        # Nến Candlestick
        fig_tv.add_trace(go.Candlestick(
            x=df_candles['date'],
            open=df_candles['open'],
            high=df_candles['high'],
            low=df_candles['low'],
            close=df_candles['close'],
            name='Nến Giá',
            increasing_line_color='#10b981',
            decreasing_line_color='#ef4444'
        ), row=1, col=1)

        # Volume bars
        colors_vol = ['rgba(16, 185, 129, 0.5)' if c >= o else 'rgba(239, 68, 68, 0.5)' for c, o in zip(df_candles['close'], df_candles['open'])]
        fig_tv.add_trace(go.Bar(
            x=df_candles['date'],
            y=df_candles['volume'],
            name='Khối lượng',
            marker_color=colors_vol
        ), row=2, col=1)

        fig_tv.update_layout(
            template='plotly_dark',
            paper_bgcolor='#09090b',
            plot_bgcolor='#09090b',
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_rangeslider_visible=False,
            font=dict(family="JetBrains Mono", size=10, color="#94a3b8"),
            showlegend=False
        )
        st.plotly_chart(fig_tv, use_container_width=True)
    else:
        st.info("Chưa có chuỗi nến thời gian thực.")

with col_radar:
    st.markdown("##### 🕸️ RADAR GIAN LẬN 8 TRỤC (BENEISH M-SCORE)")
    if d['forensic'] and 'radar_8_axes' in d['forensic']:
        axes = d['forensic']['radar_8_axes']
        r_names = [a['name'] for a in axes]
        r_vals = [a['value'] for a in axes]
        # Khép vòng đa giác
        r_names.append(r_names[0])
        r_vals.append(r_vals[0])

        fig_radar = go.Figure(go.Scatterpolar(
            r=r_vals,
            theta=r_names,
            fill='toself',
            fillcolor='rgba(245, 158, 11, 0.3)' if d['forensic']['composite_risk_score'] < 50 else 'rgba(239, 68, 68, 0.35)',
            line=dict(color='#f59e0b' if d['forensic']['composite_risk_score'] < 50 else '#ef4444', width=2),
            marker=dict(size=4)
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor="rgba(255,255,255,0.1)"),
                angularaxis=dict(tickfont=dict(family="JetBrains Mono", size=10, color="#cbd5e1"), linecolor="rgba(255,255,255,0.1)"),
                bgcolor='#09090b'
            ),
            paper_bgcolor='#09090b',
            height=420,
            margin=dict(l=30, r=30, t=20, b=20),
            font=dict(family="JetBrains Mono", color="#94a3b8"),
            showlegend=False
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# 8. BẢNG KIỂM TOÁN HOWARD SCHILIT 7 FINANCIAL SHENANIGANS
st.markdown("##### 🕵️ KIỂM TOÁN GIAN LẬN HOWARD SCHILIT (7 CHIÊU TRÒ XÀO NẤU LỢI NHUẬN & DÒNG TIỀN)")
flags = d['forensic'].get('schilit_flags', [])
if flags:
    st.markdown(f"<span style='color:#f87171; font-weight:700;'>Phát hiện {len(flags)} cờ đỏ cảnh báo:</span>", unsafe_allow_html=True)
    for f in flags:
        lvl_color = "#ef4444" if f['level'] == 'HIGH' else "#f59e0b"
        st.markdown(f"""
        <div class="flag-card" style="border-left-color:{lvl_color};">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="background:{lvl_color}; color:#000; font-family:'JetBrains Mono'; font-weight:800; font-size:10px; padding:2px 6px; border-radius:4px;">{f['code']}</span>
                <span style="font-weight:700; font-size:13px; color:#f8fafc;">{f['title']}</span>
            </div>
            <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">{f['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="flag-clean">
        🛡️ <b>Báo cáo tài chính đạt chuẩn kiểm toán sạch sẽ.</b> Không phát hiện dấu hiệu bất thường về dồn tích doanh thu hay xào nấu chi phí theo chuẩn mực Schilit.
    </div>
    """, unsafe_allow_html=True)

st.write("")

# 9. 3 TRỤ CỘT: CÁC TẦNG ĐỊNH GIÁ, SỨC KHỎE NGÀNH, VỐN & NỢ
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("##### 💎 CÁC TẦNG ĐỊNH GIÁ")
    st.markdown(f"<div style='font-size:12px; color:#a1a1aa;'>Giá trị hợp lý bình quân:</div><div style='font-size:24px; font-weight:900; font-family:\"JetBrains Mono\"; color:#ffffff; margin-bottom:10px;'>{d['composite_price']:,.0f} VND</div>", unsafe_allow_html=True)
    for m_k, m_v in d['active_models'].items():
        diff = ((m_v - d['current_price']) / d['current_price'] * 100) if d['current_price'] > 0 else 0.0
        diff_color = "#34d399" if diff >= 0 else "#f87171"
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #27272a; font-family:'JetBrains Mono'; font-size:12px;">
            <span style="color:#a1a1aa;">{m_k}:</span>
            <span style="font-weight:700; color:#f8fafc;">{m_v:,.0f} VND <span style="color:{diff_color}; font-size:10px;">({diff:+.1f}%)</span></span>
        </div>
        """, unsafe_allow_html=True)

with c2:
    st.markdown(f"##### {d['radar']['title']}")
    st.markdown(f"<div style='font-size:12px; color:#a1a1aa;'>Thước đo trọng yếu:</div><div style='font-size:24px; font-weight:900; font-family:\"JetBrains Mono\"; color:#34d399; margin-bottom:10px;'>{d['radar']['score']}</div>", unsafe_allow_html=True)
    for r in d['radar']['rows']:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #27272a; font-family:'JetBrains Mono'; font-size:12px;">
            <span style="color:#a1a1aa;">{r['label']}</span>
            <span style="font-weight:700; color:#f8fafc;">{r['val']}</span>
        </div>
        """, unsafe_allow_html=True)

with c3:
    st.markdown(f"##### {d['solvency']['title']}")
    st.markdown(f"<div style='font-size:12px; color:#a1a1aa;'>Chỉ số phòng thủ:</div><div style='font-size:24px; font-weight:900; font-family:\"JetBrains Mono\"; color:#38bdf8; margin-bottom:10px;'>{d['solvency']['score']}</div>", unsafe_allow_html=True)
    for s in d['solvency']['rows']:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #27272a; font-family:'JetBrains Mono'; font-size:12px;">
            <span style="color:#a1a1aa;">{s['label']}</span>
            <span style="font-weight:700; color:#f8fafc;">{s['val']}</span>
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# 10. SO SÁNH ĐỊNH GIÁ FOOTBALL FIELD & QUỸ ĐẠO BCTC 16 NĂM
ch1, ch2 = st.columns(2)

with ch1:
    st.markdown("##### 📊 SO SÁNH THỊ GIÁ VS CÁC MÔ HÌNH ĐỊNH GIÁ (VND)")
    x_bars = ['Thị Giá', *d['active_models'].keys(), 'Hợp Lý (Composite)']
    y_bars = [d['current_price'], *d['active_models'].values(), d['composite_price']]
    colors = ['#94a3b8', '#06b6d4', '#f59e0b', '#a855f7', '#3b82f6', '#ec4899', '#10b981']
    
    fig_val = go.Figure(data=[go.Bar(
        x=x_bars,
        y=y_bars,
        marker_color=colors[:len(x_bars)],
        text=[f"{v:,.0f}" for v in y_bars],
        textposition='auto',
        textfont=dict(family="JetBrains Mono", size=10, color="#ffffff")
    )])
    fig_val.update_layout(
        template="plotly_dark",
        paper_bgcolor='#09090b',
        plot_bgcolor='#09090b',
        height=360,
        margin=dict(l=10, r=10, t=20, b=20),
        font=dict(family="JetBrains Mono", size=10, color="#94a3b8")
    )
    st.plotly_chart(fig_val, use_container_width=True)

with ch2:
    st.markdown(f"##### 📈 QUỸ ĐẠO VỐN CSH & LỢI NHUẬN {d['total_years']} NĂM ({d['year_range']}) [TỶ VND]")
    fh = d['financial_history']
    fig_fin = go.Figure()
    if fh['rev'] and any(v > 0 for v in fh['rev']):
        fig_fin.add_trace(go.Scatter(x=fh['years'], y=fh['rev'], name='Doanh thu', line=dict(color='#f59e0b', width=2)))
    fig_fin.add_trace(go.Scatter(x=fh['years'], y=fh['ni'], name='Lợi nhuận ròng', line=dict(color='#10b981', width=2.5)))
    fig_fin.add_trace(go.Scatter(x=fh['years'], y=fh['eq'], name='Vốn CSH', line=dict(color='#06b6d4', dash='dash', width=2)))
    if fh['cfo'] and any(v != 0 for v in fh['cfo']) and d['archetype'] != 'BANK':
        fig_fin.add_trace(go.Scatter(x=fh['years'], y=fh['cfo'], name='Dòng tiền CFO', line=dict(color='#a855f7', dash='dot', width=1.5)))

    fig_fin.update_layout(
        template="plotly_dark",
        paper_bgcolor='#09090b',
        plot_bgcolor='#09090b',
        height=360,
        margin=dict(l=10, r=10, t=20, b=20),
        font=dict(family="JetBrains Mono", size=10, color="#94a3b8")
    )
    st.plotly_chart(fig_fin, use_container_width=True)

# 11. BỘ MÔ PHỎNG ĐỘ NHẠY TƯƠNG TÁC (SENSITIVITY SIMULATOR)
st.markdown("##### 🎮 BỘ MÔ PHỎNG ĐỘ NHẠY TƯƠNG TÁC (SENSITIVITY SIMULATOR)")
sim_p = d['simulator_params']
s_col1, s_col2, s_res = st.columns([2, 2, 2])

if sim_p['type'] == 'BANK_PB':
    with s_col1:
        s_r = st.slider("Lợi suất Vốn CSH Yêu cầu (Cost of Equity):", 8.0, 16.0, 12.5, 0.25, format="%.2f%%")
    with s_col2:
        s_roe = st.slider("Tỷ suất Sinh lời ROE Dự phóng:", 8.0, 25.0, float(tr['avg_roe_10y'] or 18.0), 0.5, format="%.1f%%")
    
    r_val = s_r / 100.0
    roe_val = s_roe / 100.0
    g_val = 0.05
    target_pb_sim = (roe_val - g_val) / (r_val - g_val) if r_val > g_val else 1.2
    sim_price = sim_p['base_bvps'] * target_pb_sim

elif sim_p['type'] == 'RE_RNAV':
    with s_col1:
        s_margin = st.slider("Biên Lợi Nhuận Gộp Quỹ Đất (Gross Margin):", 20.0, 50.0, 35.0, 1.0, format="%.1f%%")
    with s_col2:
        s_pen = st.slider("Chiết Khấu Rủi Ro Nợ Vay:", 0.0, 25.0, 10.0, 1.0, format="%.1f%%")
    
    revalued_inv = (sim_p['inv']) * (s_margin / 100.0)
    total_rnav = (d['bvps'] * sim_p['shares']) + revalued_inv - ((d['bvps'] * sim_p['shares']) * (s_pen / 100.0))
    sim_price = max(0, total_rnav / sim_p['shares'])

else:
    with s_col1:
        s_wacc = st.slider("Chi Phí Vốn Bình Quân (WACC):", 7.5, 14.0, 10.5, 0.25, format="%.2f%%")
    with s_col2:
        s_g = st.slider("Tăng Trưởng Dài Hạn (Terminal Growth g):", 1.0, 4.0, 2.5, 0.25, format="%.2f%%")
    
    wacc_v = s_wacc / 100.0
    g_v = s_g / 100.0
    if wacc_v > g_v:
        curr_f = sim_p['base_fcf']
        pv_sum = sum([curr_f * (1.05 ** yr) / ((1 + wacc_v) ** yr) for yr in range(1, 6)])
        term_val = (curr_f * (1.05 ** 5) * (1 + g_v)) / (wacc_v - g_v)
        pv_term = term_val / ((1 + wacc_v) ** 5)
        sim_price = max(0, (pv_sum + pv_term - sim_p['net_debt']) / sim_p['shares'])
    else:
        sim_price = 0

with s_res:
    diff_sim = ((sim_price - d['current_price']) / d['current_price'] * 100) if d['current_price'] > 0 else 0
    st.markdown(f"""
    <div style="background:#18181b; border:1px solid #f59e0b; border-radius:12px; padding:12px 18px; text-align:center;">
        <div style="font-size:11px; font-family:'JetBrains Mono'; color:#a1a1aa; text-transform:uppercase;">Giá Trị Mô Phỏng</div>
        <div style="font-size:24px; font-weight:900; font-family:'JetBrains Mono'; color:#fbbf24;">{sim_price:,.0f} VND</div>
        <div style="font-size:12px; font-family:'JetBrains Mono'; font-weight:700; color:{'#34d399' if diff_sim>=0 else '#f87171'};">
            Biên an toàn: {diff_sim:+.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

# 12. LUẬN ĐIỂM ĐẦU TƯ CFA (INVESTMENT THESIS)
st.write("")
st.markdown("##### 📝 LUẬN ĐIỂM ĐẦU TƯ TỔNG HỢP (CFA INVESTMENT THESIS)")
for bullet in d['thesis_bullets']:
    st.markdown(f"- {bullet}")

st.caption("Financial Radar Institutional Terminal • Multi-Agent Architecture • CFA Institute Standards")
