"""
========================================================================================
VALUATION AGENT: 🔄 CYCLICAL COMMODITIES SUITE (HÀNG HÓA CHU KỲ NẶNG)
- Áp dụng cho: HPG, HSG, NKG, DPM, DCM, DGC, PVD, PVS, BSR, HT1, BCC...
- Đặc thù: Lợi nhuận bùng nổ ở đỉnh chu kỳ và chạm đáy ở suy thoái hàng hóa.
- Lõi định giá: Chuẩn hóa Chu kỳ 7 Năm (Mid-Cycle Normalization), Khung định giá
  P/B Valuation Band (Gom đáy < 1.1x vs Chốt lời > 2.0x), DCF Dòng tiền chuẩn hóa.
========================================================================================
"""

class CyclicalAgent:
    @staticmethod
    def evaluate(df, quote, shares) -> dict:
        latest = df.iloc[-1]
        current_price = quote['current_price']
        bvps = float(latest['eq'] / shares) if shares > 0 else 0.0
        eps = float(latest['ni'] / shares) if shares > 0 else 0.0

        # 1. Chuẩn hóa chu kỳ 7 năm (Mid-Cycle Normalization)
        sub_cycle = df.iloc[-7:] if len(df) >= 7 else df
        mid_cycle_ni = sub_cycle['ni'].mean()
        mid_cycle_eps = mid_cycle_ni / shares if shares > 0 else eps
        mid_cycle_fcf = sub_cycle['fcf'].mean() if sub_cycle['fcf'].mean() > 0 else (mid_cycle_ni * 0.6)

        # 2. Khung P/B Chu kỳ
        target_pb_cycle = 1.35
        price_pb_cycle = bvps * target_pb_cycle

        # 3. P/E Chuẩn hóa 7 năm
        price_pe_cycle = mid_cycle_eps * 10.0 if mid_cycle_eps > 0 else eps * 10.0

        # 4. DCF Chuẩn hóa chu kỳ
        wacc_c = 0.105
        g_c = 0.02
        pv_fcfs_c = []
        curr_f = mid_cycle_fcf
        for y_idx in range(1, 6):
            curr_f *= 1.04
            pv_fcfs_c.append(curr_f / ((1 + wacc_c) ** y_idx))
        term_val_c = (curr_f * (1 + g_c)) / (wacc_c - g_c)
        pv_term_c = term_val_c / ((1 + wacc_c) ** 5)
        net_debt_c = latest.get('debt', 0) - latest.get('cash', 0)
        price_dcf_cycle = max(0.0, (sum(pv_fcfs_c) + pv_term_c - net_debt_c) / shares) if shares > 0 else 0.0

        # 5. Owner Earnings Chu kỳ
        price_oe_cycle = max(0.0, ((mid_cycle_ni * 1.03) / (0.10 - 0.03)) / shares) if shares > 0 else 0.0

        active_models = {
            'P/B Chu Kỳ (Tài Sản)': price_pb_cycle,
            'P/E Chuẩn Hóa 7 Năm': price_pe_cycle,
            'DCF Dòng Tiền Chu Kỳ': price_dcf_cycle,
            'Owner Earnings Chu Kỳ': price_oe_cycle
        }
        weights = {'P/B Chu Kỳ (Tài Sản)': 0.40, 'P/E Chuẩn Hóa 7 Năm': 0.30, 'DCF Dòng Tiền Chu Kỳ': 0.15, 'Owner Earnings Chu Kỳ': 0.15}

        current_pb = current_price / bvps if bvps > 0 else 1.0
        if current_pb < 1.1:
            cycle_phase = "VÙNG ĐÁY CHU KỲ (P/B < 1.1x - Vùng gom tích sản hấp dẫn)"
            radar_color = "emerald"
        elif current_pb <= 1.8:
            cycle_phase = "GIỮA CHU KỲ (P/B 1.1x - 1.8x - Định giá cân bằng)"
            radar_color = "amber"
        else:
            cycle_phase = "ĐỈNH CHU KỲ (P/B > 1.8x - Thận trọng đảo chiều)"
            radar_color = "rose"

        radar_title = "🔄 Định Vị Chu Kỳ Hàng Hóa"
        radar_badge = "P/B Valuation Band"
        radar_score = f"{current_pb:.2f}x"
        radar_status = cycle_phase
        radar_rows = [
            {"label": "Vị thế Chu kỳ Doanh nghiệp:", "val": cycle_phase},
            {"label": "LNST Chuẩn Hóa 7 Năm:", "val": f"{mid_cycle_ni/1e9:,.0f} Tỷ VND/năm"},
            {"label": "Biên An Toàn Tài Sản:", "val": f"Bảo kê bởi BVPS ({bvps:,.0f} VND/cp)"}
        ]

        solvency_title = "🏰 Sức Bền Tài Chính Trong Khủng Hoảng"
        solvency_badge = "Phòng Thủ Chu Kỳ"
        solvency_score = f"{latest.get('cash', 0)/1e9:,.0f} Tỷ"
        solvency_status = "Két tiền mặt và đòn bẩy ròng giúp vượt qua mùa đông suy thoái hàng hóa"
        solvency_color = "cyan"
        solvency_rows = [
            {"label": "Tiền mặt / Vốn CSH:", "val": f"{(latest.get('cash', 0) / latest.get('eq', 1.0) * 100):.1f}%"},
            {"label": "Tổng Nợ Vay Ròng:", "val": f"{net_debt_c/1e9:,.0f} Tỷ VND" if net_debt_c > 0 else "Két tiền mặt ròng"},
            {"label": "Giá Trị Sổ Sách (BVPS):", "val": f"{bvps:,.0f} VND/cp"}
        ]

        simulator_params = {
            'type': 'STANDARD_DCF',
            'base_fcf': mid_cycle_fcf,
            'wacc': wacc_c,
            'terminal_growth': g_c,
            'net_debt': net_debt_c,
            'shares': shares
        }

        return {
            'active_models': active_models,
            'weights': weights,
            'adj_bvps': bvps,
            'engine_note': "Mô hình chuyên biệt Cổ phiếu Chu kỳ Hàng hóa: Chuẩn hóa Lợi nhuận 7 năm (Mid-Cycle) và Khung định giá P/B Band để chống bẫy mua đỉnh/bán đáy.",
            'radar': {'title': radar_title, 'badge': radar_badge, 'score': radar_score, 'status': radar_status, 'color': radar_color, 'rows': radar_rows},
            'solvency': {'title': solvency_title, 'badge': solvency_badge, 'score': solvency_score, 'status': solvency_status, 'color': solvency_color, 'rows': solvency_rows},
            'simulator_params': simulator_params
        }

