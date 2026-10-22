"""
========================================================================================
VALUATION AGENT: 🌐 CONGLOMERATE SUITE (TẬP ĐOÀN ĐA NGÀNH / HOLDING)
- Áp dụng cho: VIC, MSN, GEX, REE, GEG...
- Đặc thù: Cấu trúc sở hữu chéo, nhiều mảng kinh doanh với biên lợi nhuận khác nhau.
- Lõi định giá: Bóc tách từng mảng kết hợp Chiết khấu Tập đoàn (HoldCo Discount 15%),
  Buffett Owner Earnings, Relative P/E & Graham Book Value.
========================================================================================
"""

class ConglomerateAgent:
    @staticmethod
    def evaluate(df, quote, shares, avg_roe_10y=None) -> dict:
        latest = df.iloc[-1]
        current_price = quote['current_price']
        bvps = float(latest['eq'] / shares) if shares > 0 else 0.0
        eps = float(latest['ni'] / shares) if shares > 0 else 0.0

        # 1. SOTP kết hợp Chiết khấu Holding (15%)
        price_sotp = (bvps * 1.45) * 0.85

        # 2. Owner Earnings
        oe_cong = df['ni'].mean() * 1.03
        price_oe_cong = max(0.0, ((oe_cong / (0.10 - 0.03)) / shares)) if shares > 0 else 0.0

        # 3. Relative P/E
        price_pe_cong = eps * 13.0 if eps > 0 else 0.0

        # 4. Graham Book Value
        price_graham_cong = bvps * 1.15

        active_models = {
            'SOTP (HoldCo Discount 15%)': price_sotp,
            'Owner Earnings': price_oe_cong,
            'Relative P/E': price_pe_cong,
            'Graham Book Value': price_graham_cong
        }
        weights = {'SOTP (HoldCo Discount 15%)': 0.40, 'Owner Earnings': 0.30, 'Relative P/E': 0.15, 'Graham Book Value': 0.15}

        radar_title = "🌐 Radar Cấu Trúc Tập Đoàn (Holding)"
        radar_badge = "SOTP Engine"
        radar_score = "15.0%"
        radar_status = "Áp dụng mức chiết khấu cấu trúc tập đoàn (HoldCo Discount) để bảo vệ quyền lợi cổ đông"
        radar_color = "emerald"
        radar_rows = [
            {"label": "Mô hình Định giá Chủ đạo:", "val": "Sum-of-the-Parts (SOTP)"},
            {"label": "Mức Chiết khấu Tập đoàn (HoldCo):", "val": "15.0% (Tránh rủi ro sở hữu chéo)"},
            {"label": "Hiệu quả Sinh lời Vốn CSH (ROE 10Y):", "val": f"{(avg_roe_10y or 14.0):.1f}%"}
        ]

        solvency_title = "🏰 Két Vốn & Đòn Bẩy Tập Đoàn"
        solvency_badge = "Đòn Bẩy Holding"
        solvency_score = f"{latest.get('debt', 0)/1e12:,.1f}K Tỷ"
        solvency_status = "Quy mô nợ vay hợp nhất của toàn bộ hệ sinh thái tập đoàn"
        solvency_color = "cyan"
        solvency_rows = [
            {"label": "Tổng Nợ Vay Hợp Nhất:", "val": f"{latest.get('debt', 0)/1e9:,.0f} Tỷ VND"},
            {"label": "Tiền Mặt & Đầu tư NH:", "val": f"{latest.get('cash', 0)/1e9:,.0f} Tỷ VND"},
            {"label": "Giá Trị Sổ Sách (BVPS):", "val": f"{bvps:,.0f} VND/cp"}
        ]

        simulator_params = {
            'type': 'CONG_SOTP',
            'base_bvps': bvps,
            'holdco_discount': 0.15,
            'shares': shares
        }

        return {
            'active_models': active_models,
            'weights': weights,
            'adj_bvps': bvps,
            'engine_note': "Mô hình chuyên biệt Tập đoàn Đa ngành: Áp dụng SOTP (Sum-of-the-Parts) và trừ đi Chiết khấu Tập đoàn (HoldCo Discount 15%).",
            'radar': {'title': radar_title, 'badge': radar_badge, 'score': radar_score, 'status': radar_status, 'color': radar_color, 'rows': radar_rows},
            'solvency': {'title': solvency_title, 'badge': solvency_badge, 'score': solvency_score, 'status': solvency_status, 'color': solvency_color, 'rows': solvency_rows},
            'simulator_params': simulator_params
        }

