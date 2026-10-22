"""
========================================================================================
MASTER ORCHESTRATOR: BỘ ĐIỀU PHỐI ĐA TÁC TỬ CHO HỆ THỐNG FINANCIAL RADAR
- Kết nối Data Engine -> Forensic Audit Agent -> 6 Domain Valuation Engines
- Tổng hợp Luận điểm Đầu tư (Investment Thesis), Biên an toàn (Margin of Safety)
========================================================================================
"""

import numpy as np
import pandas as pd
from core.data_engine import get_ticker_financials, get_market_quote, classify_sector
from forensic.forensic_agent import ForensicAgent
from valuation.banking_agent import BankingAgent
from valuation.real_estate_agent import RealEstateAgent
from valuation.conglomerate_agent import ConglomerateAgent
from valuation.cyclical_agent import CyclicalAgent
from valuation.growth_agent import GrowthAgent
from valuation.seasonal_agent import SeasonalAgent

class MasterOrchestrator:
    @staticmethod
    def analyze(ticker: str) -> dict:
        raw_ticker = ticker.upper().strip()
        
        # 1. Trích xuất chuỗi lịch sử tài chính từ Parquet 16 năm
        df, is_local, data_source_text = get_ticker_financials(raw_ticker)
        quote = get_market_quote(raw_ticker)
        
        current_price = quote['current_price']
        shares = quote['shares']
        beta = quote['beta']

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else latest

        company_name = latest.get('company_name', quote.get('company_name', raw_ticker))
        sector = latest.get('sector', 'Tổng hợp')
        archetype, archetype_label = classify_sector(raw_ticker, sector)

        # Ước tính cổ phiếu lưu hành nếu thiếu
        if shares == 0:
            if archetype in ['BANK', 'FINANCIAL_SERVICE']:
                shares = int(latest['eq'] / 15000) if latest['eq'] > 0 else 1000000
            else:
                shares = int(latest['eq'] / 25000) if latest['eq'] > 0 else 1000000

        # 2. Hồ sơ năng lực dài hạn 10-16 năm (Warren Buffett Moat)
        cagr_10y_rev = None
        cagr_10y_ni = None
        avg_roe_10y = None

        if len(df) >= 10:
            y_latest = int(latest['year'])
            row_10y = df[df['year'] == str(y_latest - 10)]
            if not row_10y.empty and row_10y.iloc[0]['rev'] > 0 and latest['rev'] > 0:
                cagr_10y_rev = float(((latest['rev'] / row_10y.iloc[0]['rev']) ** (1/10) - 1) * 100)
            if not row_10y.empty and row_10y.iloc[0]['ni'] > 0 and latest['ni'] > 0:
                cagr_10y_ni = float(((latest['ni'] / row_10y.iloc[0]['ni']) ** (1/10) - 1) * 100)
                
            sub_10 = df.iloc[-10:]
            valid_roe = [(r['ni'] / r['eq'] * 100) for _, r in sub_10.iterrows() if r['eq'] > 0]
            if valid_roe:
                avg_roe_10y = float(np.mean(valid_roe))
        else:
            valid_roe = [(r['ni'] / r['eq'] * 100) for _, r in df.iterrows() if r['eq'] > 0]
            if valid_roe:
                avg_roe_10y = float(np.mean(valid_roe))

        div_cnt = len(df[df.get('div_paid', 0) > 0])
        div_consistency = f"{div_cnt}/{len(df)} năm"

        eps = float(latest['ni'] / shares) if shares > 0 else 0.0
        bvps = float(latest['eq'] / shares) if shares > 0 else 0.0
        mkt_cap = float(current_price * shares)
        pe_curr = (current_price / eps) if eps > 0 else 0.0
        pb_curr = (current_price / bvps) if bvps > 0 else 0.0

        # 3. Kích hoạt Forensic Accounting Agent (Beneish, Altman & Schilit Shenanigans)
        forensic_res = ForensicAgent.audit(df, archetype)

        # 4. Điều phối sang Domain Valuation Agent chuyên biệt
        if archetype in ['BANK', 'FINANCIAL_SERVICE']:
            val_res = BankingAgent.evaluate(df, quote, shares, avg_roe_10y)
        elif archetype == 'REAL_ESTATE':
            val_res = RealEstateAgent.evaluate(df, quote, shares)
        elif archetype == 'CONGLOMERATE':
            val_res = ConglomerateAgent.evaluate(df, quote, shares, avg_roe_10y)
        elif archetype == 'CYCLICAL':
            val_res = CyclicalAgent.evaluate(df, quote, shares)
        elif archetype == 'SEASONAL':
            val_res = SeasonalAgent.evaluate(df, quote, shares, forensic_res)
        else:
            val_res = GrowthAgent.evaluate(df, quote, shares, forensic_res)

        active_models = val_res['active_models']
        weights = val_res['weights']
        engine_note = val_res['engine_note']
        radar = val_res['radar']
        solvency = val_res['solvency']
        simulator_params = val_res['simulator_params']

        # 5. Tính toán Composite Fair Value & Tín hiệu đầu tư
        tot_w = sum([weights[k] for k in active_models if active_models[k] > 0])
        composite_price = sum([active_models[k] * weights[k] for k in active_models if active_models[k] > 0]) / tot_w if tot_w > 0 else 0.0

        upside = ((composite_price - current_price) / current_price) * 100 if current_price > 0 else 0.0
        if upside >= 25.0:
            signal = "🟢 STRONG BUY"
            action = "Định giá chiết khấu sâu, vùng gom tích sản hấp dẫn"
            signal_color = "emerald"
        elif upside >= 10.0:
            signal = "🟢 BUY"
            action = "Thị giá thấp hơn giá trị nội tại, có biên an toàn"
            signal_color = "emerald"
        elif upside >= -10.0:
            signal = "🟡 FAIRLY VALUED / HOLD"
            action = "Thị giá phản ánh tương đối đúng giá trị doanh nghiệp"
            signal_color = "amber"
        else:
            signal = "🔴 OVERVALUED"
            action = "Thị giá cao hơn giá trị nội tại, thận trọng rủi ro điều chỉnh"
            signal_color = "rose"

        # 6. Tạo Investment Thesis ngắn gọn chuẩn CFA
        thesis_bullets = []
        if avg_roe_10y and avg_roe_10y >= 18.0:
            thesis_bullets.append(f"🏆 Lợi thế kinh tế (Moat) mạnh: ROE bình quân 10 năm đạt {avg_roe_10y:.1f}%.")
        if forensic_res['total_flags'] == 0 and forensic_res['m_score'] < -2.22:
            thesis_bullets.append("🛡️ Báo cáo tài chính sạch sẽ, không có cờ đỏ gian lận Schilit hay dồn tích.")
        elif forensic_res['total_flags'] > 0:
            thesis_bullets.append(f"⚠️ Cảnh báo: Phát hiện {forensic_res['total_flags']} cờ đỏ gian lận/dồn tích kế toán.")
        if upside > 20.0:
            thesis_bullets.append(f"🎯 Biên an toàn định giá đạt +{upside:.1f}%, thị giá hiện tại đang chiết khấu hấp dẫn.")
        elif upside < -15.0:
            thesis_bullets.append(f"⚠️ Thị giá đang đắt hơn định giá hợp lý {abs(upside):.1f}%.")

        return {
            'ticker': raw_ticker,
            'company_name': company_name,
            'sector': sector,
            'archetype': archetype,
            'archetype_label': archetype_label,
            'engine_note': engine_note,
            'data_source': data_source_text,
            'total_years': len(df),
            'year_range': f"{df['year'].min()} - {df['year'].max()}",
            'current_price': current_price,
            'market_cap': mkt_cap,
            'shares': shares,
            'beta': beta,
            'bvps': bvps,
            'eps': eps,
            'pe': round(pe_curr, 2),
            'pb': round(pb_curr, 2),
            'signal': signal,
            'action': action,
            'signal_color': signal_color,
            'composite_price': round(composite_price, 0),
            'upside': round(upside, 1),
            'active_models': active_models,
            'weights': weights,
            'track_record_10y': {
                'cagr_10y_rev': cagr_10y_rev,
                'cagr_10y_ni': cagr_10y_ni,
                'avg_roe_10y': avg_roe_10y,
                'div_consistency': div_consistency
            },
            'radar': radar,
            'solvency': solvency,
            'forensic': forensic_res,
            'simulator_params': simulator_params,
            'thesis_bullets': thesis_bullets,
            'financial_history': {
                'years': list(df['year']),
                'rev': [round(v/1e9) for v in df.get('rev', [])] if 'rev' in df.columns else [],
                'ni': [round(v/1e9) for v in df['ni']],
                'eq': [round(v/1e9) for v in df['eq']],
                'cfo': [round(v/1e9) for v in df.get('cfo', [])] if 'cfo' in df.columns else [],
                'fcf': [round(v/1e9) for v in df.get('fcf', [])] if 'fcf' in df.columns else []
            }
        }

