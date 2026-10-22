"""
========================================================================================
VALUATION AGENT: 🏛️ BANKING & FINANCIAL SERVICES SUITE
- Áp dụng cho: VCB, MBB, TCB, ACB, TPB, VPB, CTG, BID, SSI, VND...
- Đặc thù: Loại trừ DCF (FCFF) và Altman Z do cấu trúc bảng cân đối tiền gửi/cho vay.
- Lõi định giá: Stress-Test Nợ Xấu Ẩn (Credit Risk Haircut) -> Justified P/B theo ROE,
  P/E Ngành Ngân Hàng, Gordon DDM Cổ Tức & Graham Book Value.
========================================================================================
"""

import numpy as np

class BankingAgent:
    @staticmethod
    def evaluate(df, quote, shares, avg_roe_10y=None) -> dict:
        latest = df.iloc[-1]
        current_price = quote['current_price']
        
        # 1. Kiểm tra đệm vốn Basel II/III
        capital_buffer = (latest['eq'] / latest['ta'] * 100) if latest.get('ta', 0) > 0 else 9.0
        roa = (latest['ni'] / latest['ta'] * 100) if latest.get('ta', 0) > 0 else 1.5
        
        # 2. Stress-Test Nợ Xấu Ẩn (Haircut)
        if capital_buffer >= 9.0:
            stress_haircut = 0.0
            stress_status = "🟢 An toàn vốn cao (Đệm vốn Basel II/III vững chắc)"
        elif capital_buffer >= 7.0:
            stress_haircut = 0.05
            stress_status = "🟡 Đệm vốn trung bình, chiết khấu rủi ro tín dụng 5% BVPS"
        else:
            stress_haircut = 0.10
            stress_status = "🔴 Đòn bẩy cao, phạt nợ xấu tiềm ẩn 10% BVPS"

        bvps = float(latest['eq'] / shares) if shares > 0 else 0.0
        eps = float(latest['ni'] / shares) if shares > 0 else 0.0
        adj_bvps = bvps * (1 - stress_haircut)

        # 3. Justified P/B theo Gordon: (ROE - g) / (r - g)
        r_bank = 0.125
        g_bank = 0.05
        roe_bank = max(0.08, min(0.25, (avg_roe_10y or 16.0) / 100.0))
        target_pb = (roe_bank - g_bank) / (r_bank - g_bank) if (r_bank > g_bank) else 1.2
        target_pb = max(0.85, min(1.90, target_pb))
        price_justified_pb = adj_bvps * target_pb

        # 4. Target P/E Ngành Ngân Hàng
        bank_target_pe = 8.5 if roe_bank >= 0.16 else 7.0
        price_bank_pe = eps * bank_target_pe if eps > 0 else 0.0

        # 5. Gordon Dividend DDM
        div_vals = df['div_paid'].dropna().values
        avg_div = div_vals[-3:].mean() if len(div_vals) >= 3 else latest.get('div_paid', 0)
        dps = avg_div / shares if shares > 0 else 0.0
        price_ddm = max(0.0, (dps * 1.05) / (0.12 - 0.05)) if dps > 0 else 0.0

        # 6. Graham Book Value
        price_graham_bank = adj_bvps * 1.15

        active_models = {
            'Justified P/B (ROE)': price_justified_pb,
            'P/E Ngành Ngân Hàng': price_bank_pe,
            'Graham Book Value': price_graham_bank
        }
        weights = {'Justified P/B (ROE)': 0.45, 'P/E Ngành Ngân Hàng': 0.40, 'Graham Book Value': 0.15}
        if price_ddm > 0:
            active_models['Dividend DDM'] = price_ddm
            weights = {'Justified P/B (ROE)': 0.35, 'P/E Ngành Ngân Hàng': 0.35, 'Dividend DDM': 0.15, 'Graham Book Value': 0.15}

        pb_curr = current_price / bvps if bvps > 0 else 1.0

        radar_title = "🏛️ Sức Khỏe Ngân Hàng (Basel & ROE)"
        radar_badge = "Basel II/III"
        radar_score = f"{capital_buffer:.1f}%"
        radar_status = stress_status
        radar_color = "emerald" if capital_buffer >= 8.0 else "amber"
        radar_rows = [
            {"label": "Tỷ suất Sinh lời Tổng tài sản (ROA):", "val": f"{roa:.2f}% ({'Top ngành' if roa >= 1.5 else 'Bình thường'})"},
            {"label": "Stress-Test Nợ Xấu Ẩn:", "val": f"Khấu trừ rủi ro {stress_haircut*100:.0f}% vào BVPS"},
            {"label": "Đòn bẩy Vốn Hoạt động:", "val": f"{(latest['ta'] / latest['eq']):.1f}x (Chuẩn Basel)" if latest['eq'] > 0 else "N/A"}
        ]

        solvency_title = "🛡️ Quy Mô & Nền Tảng Tài Sản"
        solvency_badge = "Tài Sản & BVPS"
        solvency_score = f"{pb_curr:.2f}x"
        solvency_status = "Rất rẻ dưới 1.0x P/B (Vùng mua tích sản)" if pb_curr < 1.0 else ("Định giá hợp lý" if pb_curr <= 1.5 else "Định giá cao")
        solvency_color = "cyan"
        solvency_rows = [
            {"label": "Giá Trị Sổ Sách Chuẩn Hóa:", "val": f"{adj_bvps:,.0f} VND/cp (Gốc: {bvps:,.0f})"},
            {"label": "Tổng Tài Sản Ngân Hàng:", "val": f"{latest['ta']/1e12:,.1f} Nghìn Tỷ VND"},
            {"label": "Vốn Chủ Sở Hữu (Equity):", "val": f"{latest['eq']/1e9:,.0f} Tỷ VND"}
        ]

        simulator_params = {
            'type': 'BANK_PB',
            'base_bvps': adj_bvps,
            'roe': roe_bank,
            'cost_of_equity': r_bank,
            'terminal_growth': g_bank
        }

        return {
            'active_models': active_models,
            'weights': weights,
            'adj_bvps': adj_bvps,
            'engine_note': "Mô hình chuyên biệt Ngân hàng: Loại trừ DCF & Altman Z, tích hợp Stress-Test Nợ Xấu Ẩn (Credit Risk Buffer) khấu trừ trực tiếp vào BVPS, kết hợp Justified P/B theo ROE.",
            'radar': {'title': radar_title, 'badge': radar_badge, 'score': radar_score, 'status': radar_status, 'color': radar_color, 'rows': radar_rows},
            'solvency': {'title': solvency_title, 'badge': solvency_badge, 'score': solvency_score, 'status': solvency_status, 'color': solvency_color, 'rows': solvency_rows},
            'simulator_params': simulator_params
        }

