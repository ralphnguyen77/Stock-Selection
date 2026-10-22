"""
========================================================================================
VALUATION AGENT: 🚀 STANDARD CORPORATE & GROWTH SUITE (5 TẦNG CFA)
- Áp dụng cho: FPT, MWG, VNM, GAS, BMP, DGW, PNJ, REE...
- Đặc thù: Dòng tiền tăng trưởng bền vững, lợi thế cạnh tranh kinh tế (Economic Moat).
- Lõi định giá: 5 Tầng CFA Chuẩn mực:
  1. DCF (FCFF) Chiết khấu dòng tiền tự do 2 giai đoạn.
  2. Buffett Owner Earnings (Lợi nhuận chủ sở hữu thực chất).
  3. Benjamin Graham Formula (Graham Number & Graham Intrinsic Value).
  4. Relative P/E (Định giá tương đối theo vị thế ngành).
  5. Gordon Dividend Discount Model (DDM).
========================================================================================
"""

import numpy as np

class GrowthAgent:
    @staticmethod
    def evaluate(df, quote, shares, forensic_result) -> dict:
        latest = df.iloc[-1]
        current_price = quote['current_price']
        bvps = float(latest['eq'] / shares) if shares > 0 else 0.0
        eps = float(latest['ni'] / shares) if shares > 0 else 0.0
        net_debt = latest.get('debt', 0) - latest.get('cash', 0)

        # 1. DCF (FCFF) 2-Stage Model
        wacc_std = 0.10
        g_std = 0.025
        base_fcf = latest.get('fcf', 0) if latest.get('fcf', 0) > 0 else df['fcf'].mean()
        if base_fcf <= 0:
            base_fcf = latest.get('ni', 0) * 0.70

        pv_fcfs_std = []
        curr_f = base_fcf
        for y_idx in range(1, 6):
            curr_f *= 1.06
            pv_fcfs_std.append(curr_f / ((1 + wacc_std) ** y_idx))
        term_val_std = (curr_f * (1 + g_std)) / (wacc_std - g_std)
        pv_term_std = term_val_std / ((1 + wacc_std) ** 5)
        dcf_equity = sum(pv_fcfs_std) + pv_term_std - net_debt
        price_dcf_std = max(0.0, dcf_equity / shares) if shares > 0 else 0.0

        # 2. Buffett Owner Earnings Model
        # Owner Earnings = Net Income + D&A - Maintenance Capex (ước tính 60% tổng Capex)
        maint_capex = latest.get('capex', 0) * 0.60
        oe = latest.get('ni', 0) + latest.get('depr', 0) - maint_capex
        if oe <= 0:
            oe = df['ni'].mean()
        price_oe_std = max(0.0, ((oe * 1.03) / (0.10 - 0.03)) / shares) if shares > 0 else 0.0

        # 3. Benjamin Graham Formula
        graham_num = np.sqrt(22.5 * eps * bvps) if (eps > 0 and bvps > 0) else 0.0
        graham_int = eps * (8.5 + 2 * 5.0) * (4.4 / 3.5) if eps > 0 else 0.0
        price_graham_std = (graham_num * 0.5 + graham_int * 0.5) if graham_num > 0 else graham_int

        # 4. Relative P/E
        price_pe_std = eps * 14.5 if eps > 0 else 0.0

        # 5. Gordon Dividend DDM
        div_vals = df['div_paid'].dropna().values
        avg_div = div_vals[-3:].mean() if len(div_vals) >= 3 else latest.get('div_paid', 0)
        dps = avg_div / shares if shares > 0 else 0.0
        price_ddm_std = max(0.0, (dps * 1.03) / (0.09 - 0.03)) if dps > 0 else 0.0

        active_models = {
            'DCF (FCFF)': price_dcf_std,
            'Owner Earnings': price_oe_std,
            'Graham Value': price_graham_std,
            'Relative P/E': price_pe_std
        }
        weights = {'DCF (FCFF)': 0.35, 'Owner Earnings': 0.25, 'Relative P/E': 0.25, 'Graham Value': 0.15}
        if price_ddm_std > 0:
            active_models['Dividend DDM'] = price_ddm_std
            weights = {'DCF (FCFF)': 0.30, 'Owner Earnings': 0.20, 'Relative P/E': 0.25, 'Dividend DDM': 0.15, 'Graham Value': 0.10}

        m_score = forensic_result.get('m_score', -2.5)
        m_status = forensic_result.get('m_status', "Chất lượng lợi nhuận cao")
        m_color = forensic_result.get('m_color', "emerald")

        z_score = forensic_result.get('z_score', 3.0)
        z_status = forensic_result.get('z_status', "Cực kỳ an toàn")
        z_color = forensic_result.get('z_color', "emerald")

        cfo_ni = forensic_result.get('cfo_ni_ratio', 1.0)
        dso_val = forensic_result.get('dso_days', 45.0)
        gm_pct = forensic_result.get('gross_margin_pct', 25.0)

        radar_title = "🚦 Radar Gian Lận (Howard Schilit)"
        radar_badge = "Beneish M-Score"
        radar_score = f"{m_score:.3f}"
        radar_status = m_status
        radar_color = m_color
        radar_rows = [
            {"label": "Chất lượng Dồn tích (CFO / NI):", "val": f"{cfo_ni:.2f}x ({'Lãi tiền thật' if cfo_ni >= 1.0 else 'Dồn tích cao'})"},
            {"label": "Vòng quay Phải thu (DSO):", "val": f"{dso_val:.0f} ngày"},
            {"label": "Biên Lợi Nhuận Gộp:", "val": f"{gm_pct:.1f}%"}
        ]

        cr = (latest.get('ca', 0) / latest.get('cl', 1.0)) if latest.get('cl', 0) > 0 else 1.5
        solvency_title = "🏰 Sức Khỏe & Vỡ Nợ (Altman Z)"
        solvency_badge = "Altman Z''-Score"
        solvency_score = f"{z_score:.2f}"
        solvency_status = z_status
        solvency_color = z_color
        solvency_rows = [
            {"label": "Tiền mặt & Đầu tư ngắn hạn:", "val": f"{latest.get('cash', 0)/1e9:,.0f} Tỷ VND"},
            {"label": "Thanh toán hiện hành (CR):", "val": f"{cr:.2f}x ({'Thanh khoản tốt' if cr >= 1.2 else 'Thấp'})"},
            {"label": "Nợ vay ròng:", "val": f"{net_debt/1e9:,.0f} Tỷ VND" if net_debt > 0 else "Két tiền mặt ròng"}
        ]

        simulator_params = {
            'type': 'STANDARD_DCF',
            'base_fcf': base_fcf,
            'wacc': wacc_std,
            'terminal_growth': g_std,
            'net_debt': net_debt,
            'shares': shares
        }

        return {
            'active_models': active_models,
            'weights': weights,
            'adj_bvps': bvps,
            'engine_note': "Mô hình chuẩn CFA dành cho Doanh nghiệp Sản xuất & Tăng trưởng: 5 Tầng Định giá CFA + Kiểm toán Gian lận Beneish M-Score & Altman Z''-Score.",
            'radar': {'title': radar_title, 'badge': radar_badge, 'score': radar_score, 'status': radar_status, 'color': radar_color, 'rows': radar_rows},
            'solvency': {'title': solvency_title, 'badge': solvency_badge, 'score': solvency_score, 'status': solvency_status, 'color': solvency_color, 'rows': solvency_rows},
            'simulator_params': simulator_params
        }

