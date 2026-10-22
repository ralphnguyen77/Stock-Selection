"""
========================================================================================
VALUATION AGENT: 🌦️ SEASONALITY SUITE (CỔ PHIẾU CHU KỲ MÙA VỤ)
- Áp dụng cho: VSH, SBA, SHP, TMP, HND, QTP (Thủy điện, Nhiệt điện), VHC, ANV, FMC (Thủy sản),
  QNS, SBT, SLS (Mía đường)...
- Đặc thù: Kết quả kinh doanh chịu ảnh hưởng lớn bởi thời tiết (El Nino, La Nina), vụ mùa.
- Lõi định giá: Chuẩn hóa 4 Năm để khử nhiễu ngắn hạn, kết hợp DDM Cổ tức & P/E Chuẩn hóa.
========================================================================================
"""

class SeasonalAgent:
    @staticmethod
    def evaluate(df, quote, shares, forensic_result) -> dict:
        latest = df.iloc[-1]
        current_price = quote['current_price']
        bvps = float(latest['eq'] / shares) if shares > 0 else 0.0
        eps = float(latest['ni'] / shares) if shares > 0 else 0.0

        # 1. Chuẩn hóa 4 năm khử nhiễu thời tiết / vụ mùa
        sub_sea = df.iloc[-4:] if len(df) >= 4 else df
        norm_ni = sub_sea['ni'].mean()
        norm_eps = norm_ni / shares if shares > 0 else eps
        norm_fcf = sub_sea['fcf'].mean() if sub_sea['fcf'].mean() > 0 else (norm_ni * 0.70)

        # 2. P/E Chuẩn hóa
        price_pe_sea = norm_eps * 10.5 if norm_eps > 0 else eps * 10.5

        # 3. Gordon Dividend DDM (Các cổ phiếu điện, mía đường thường trả cổ tức rất cao)
        div_vals = df['div_paid'].dropna().values
        avg_div = div_vals[-4:].mean() if len(div_vals) >= 4 else latest.get('div_paid', 0)
        dps = avg_div / shares if shares > 0 else 0.0
        price_ddm_sea = max(0.0, (dps * 1.03) / (0.11 - 0.03)) if dps > 0 else 0.0

        # 4. DCF Chuẩn hóa
        wacc_s = 0.10
        g_s = 0.02
        pv_fcfs = []
        curr_f = norm_fcf
        for yr in range(1, 6):
            curr_f *= 1.03
            pv_fcfs.append(curr_f / ((1 + wacc_s) ** yr))
        term_val = (curr_f * (1 + g_s)) / (wacc_s - g_s)
        pv_term = term_val / ((1 + wacc_s) ** 5)
        net_debt = latest.get('debt', 0) - latest.get('cash', 0)
        price_dcf_sea = max(0.0, (sum(pv_fcfs) + pv_term - net_debt) / shares) if shares > 0 else 0.0

        # 5. Graham Value
        price_graham_sea = bvps * 1.15

        active_models = {
            'P/E Chuẩn Hóa 4 Năm': price_pe_sea,
            'DCF Khử Nhiễu Mùa Vụ': price_dcf_sea,
            'Graham Asset Value': price_graham_sea
        }
        weights = {'P/E Chuẩn Hóa 4 Năm': 0.40, 'DCF Khử Nhiễu Mùa Vụ': 0.35, 'Graham Asset Value': 0.25}
        if price_ddm_sea > 0:
            active_models['Dividend DDM (Cổ Tức)'] = price_ddm_sea
            weights = {'P/E Chuẩn Hóa 4 Năm': 0.35, 'Dividend DDM (Cổ Tức)': 0.30, 'DCF Khử Nhiễu Mùa Vụ': 0.20, 'Graham Asset Value': 0.15}

        radar_title = "🌦️ Radar Chu Kỳ Mùa Vụ & Thủy Văn"
        radar_badge = "De-Seasonalized Model"
        radar_score = f"{norm_ni/1e9:,.0f} Tỷ"
        radar_status = "Đã khử nhiễu chu kỳ thời tiết (El Nino/La Nina) bằng trung bình động 4 năm"
        radar_color = "emerald"
        radar_rows = [
            {"label": "LNST Chuẩn Hóa 4 Năm:", "val": f"{norm_ni/1e9:,.0f} Tỷ VND/năm"},
            {"label": "Dòng Tiền FCF Chuẩn Hóa:", "val": f"{norm_fcf/1e9:,.0f} Tỷ VND/năm"},
            {"label": "Tỷ suất Cổ tức Ước tính:", "val": f"{(dps / current_price * 100):.1f}%" if current_price > 0 else "N/A"}
        ]

        solvency_title = "🏰 Sức Bền Nợ Vay Mùa Vụ"
        solvency_badge = "Phòng Thủ Tài Sản"
        solvency_score = f"{latest.get('cash', 0)/1e9:,.0f} Tỷ"
        solvency_status = "Dòng tiền ổn định đảm bảo chi trả nợ vay và cổ tức tiền mặt"
        solvency_color = "cyan"
        solvency_rows = [
            {"label": "Két Tiền Mặt:", "val": f"{latest.get('cash', 0)/1e9:,.0f} Tỷ VND"},
            {"label": "Nợ Vay Ròng:", "val": f"{net_debt/1e9:,.0f} Tỷ VND" if net_debt > 0 else "Két tiền mặt ròng"},
            {"label": "Giá Trị Sổ Sách (BVPS):", "val": f"{bvps:,.0f} VND/cp"}
        ]

        simulator_params = {
            'type': 'STANDARD_DCF',
            'base_fcf': norm_fcf,
            'wacc': wacc_s,
            'terminal_growth': g_s,
            'net_debt': net_debt,
            'shares': shares
        }

        return {
            'active_models': active_models,
            'weights': weights,
            'adj_bvps': bvps,
            'engine_note': "Mô hình chuyên biệt Cổ phiếu Mùa vụ: Chuẩn hóa 4 năm để khử nhiễu ngắn hạn do thời tiết, kết hợp mô hình cổ tức DDM & P/E.",
            'radar': {'title': radar_title, 'badge': radar_badge, 'score': radar_score, 'status': radar_status, 'color': radar_color, 'rows': radar_rows},
            'solvency': {'title': solvency_title, 'badge': solvency_badge, 'score': solvency_score, 'status': solvency_status, 'color': solvency_color, 'rows': solvency_rows},
            'simulator_params': simulator_params
        }

