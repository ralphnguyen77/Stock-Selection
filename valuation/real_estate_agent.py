"""
========================================================================================
VALUATION AGENT: 🏢 REAL ESTATE & PROJECT DEVELOPERS SUITE
- Áp dụng cho: VHM, NVL, KBC, PDR, DIG, DXG, NLG, KDH, VRE, BCM, IDC, SZC, CEO...
- Đặc thù: Dòng tiền DCF biến động mạnh theo đợt mở bán dự án, dễ gây méo mó.
- Lõi định giá: RNAV (Revalued Net Asset Value) định giá lại Hàng tồn kho & Quỹ đất,
  Khung P/B BĐS (1.4x), P/E Chu kỳ Bàn giao, Giám sát Đòn bẩy Nợ vay / Vốn CSH.
========================================================================================
"""

import numpy as np

class RealEstateAgent:
    @staticmethod
    def evaluate(df, quote, shares) -> dict:
        latest = df.iloc[-1]
        current_price = quote['current_price']
        bvps = float(latest['eq'] / shares) if shares > 0 else 0.0
        eps = float(latest['ni'] / shares) if shares > 0 else 0.0

        # 1. RNAV (Revalued Net Asset Value)
        # Biên lãi gộp dự phóng hàng tồn kho mở bán ~35%
        revalued_inv_surplus = latest.get('inv', 0) * 0.35
        net_debt_re = latest.get('debt', 0) - latest.get('cash', 0)
        debt_penalty = max(0.0, (net_debt_re - latest.get('eq', 0) * 0.5) * 0.15) if net_debt_re > latest.get('eq', 0) * 0.5 else 0.0
        rnav_total = latest.get('eq', 0) + revalued_inv_surplus - debt_penalty
        price_rnav = max(0.0, rnav_total / shares) if shares > 0 else 0.0

        # 2. Khung P/B BĐS
        price_pb_re = bvps * 1.40

        # 3. P/E Chu kỳ Bàn giao (Trung bình 5 năm)
        sub_re = df.iloc[-5:] if len(df) >= 5 else df
        avg_re_ni = sub_re['ni'].mean()
        eps_re_cycle = avg_re_ni / shares if shares > 0 else eps
        price_pe_re = eps_re_cycle * 11.0 if eps_re_cycle > 0 else eps * 11.0

        # 4. Graham Asset Value
        price_graham_re = bvps * 1.10

        active_models = {
            'Định Giá Quỹ Đất (RNAV)': price_rnav,
            'Khung Định Giá P/B BĐS': price_pb_re,
            'P/E Chu Kỳ Bàn Giao': price_pe_re,
            'Graham Asset Value': price_graham_re
        }
        weights = {'Định Giá Quỹ Đất (RNAV)': 0.45, 'Khung Định Giá P/B BĐS': 0.30, 'P/E Chu Kỳ Bàn Giao': 0.15, 'Graham Asset Value': 0.10}

        inv_ratio = (latest.get('inv', 0) / latest['ta'] * 100) if latest.get('ta', 0) > 0 else 0.0
        net_debt_equity = (net_debt_re / latest['eq']) if latest.get('eq', 0) > 0 else 1.0

        radar_title = "🏢 Radar Quỹ Đất & Tiến Độ Dự Án"
        radar_badge = "RNAV Model"
        radar_score = f"{latest.get('inv', 0)/1e12:,.1f}K Tỷ"
        radar_status = f"Hàng tồn kho chiếm {inv_ratio:.1f}% Tổng tài sản. Biên lợi nhuận dự án ~35%."
        radar_color = "emerald" if net_debt_equity < 0.8 else "amber"
        radar_rows = [
            {"label": "Hàng Tồn Kho (Quỹ Đất Dở Dang):", "val": f"{latest.get('inv', 0)/1e9:,.0f} Tỷ VND"},
            {"label": "Đòn bẩy Nợ Vay Ròng / Vốn CSH:", "val": f"{net_debt_equity:.2f}x ({'An toàn < 0.8x' if net_debt_equity < 0.8 else 'Đòn bẩy cao'})"},
            {"label": "Giá Trị Tài Sản Ròng (RNAV):", "val": f"{rnav_total/1e12:,.1f} Nghìn Tỷ VND"}
        ]

        solvency_title = "🛡️ Sức Bền Nợ Vay & Thanh Khoản BĐS"
        solvency_badge = "Phòng Thủ Nợ Vay"
        solvency_score = f"{current_price / bvps:.2f}x" if bvps > 0 else "N/A"
        solvency_status = "Định giá P/B phản ánh quỹ đất thực tế của doanh nghiệp"
        solvency_color = "cyan"
        solvency_rows = [
            {"label": "Két Tiền Mặt & Đầu tư NH:", "val": f"{latest.get('cash', 0)/1e9:,.0f} Tỷ VND"},
            {"label": "Tổng Nợ Vay (Ngân hàng + TP):", "val": f"{latest.get('debt', 0)/1e9:,.0f} Tỷ VND"},
            {"label": "Giá Trị Sổ Sách (BVPS):", "val": f"{bvps:,.0f} VND/cp"}
        ]

        simulator_params = {
            'type': 'RE_RNAV',
            'base_bvps': bvps,
            'rnav_price': price_rnav,
            'margin': 0.35,
            'inv': latest.get('inv', 0),
            'shares': shares
        }

        return {
            'active_models': active_models,
            'weights': weights,
            'adj_bvps': bvps,
            'engine_note': "Mô hình chuyên biệt Bất Động Sản: Kích hoạt định giá Quỹ Đất (RNAV), loại bỏ DCF méo mó, định giá lại Hàng tồn kho mở bán và Khung P/B Chu kỳ.",
            'radar': {'title': radar_title, 'badge': radar_badge, 'score': radar_score, 'status': radar_status, 'color': radar_color, 'rows': radar_rows},
            'solvency': {'title': solvency_title, 'badge': solvency_badge, 'score': solvency_score, 'status': solvency_status, 'color': solvency_color, 'rows': solvency_rows},
            'simulator_params': simulator_params
        }

