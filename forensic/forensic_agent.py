"""
========================================================================================
FORENSIC ACCOUNTING AGENT: BẢO ĐIỂN KIỂM TOÁN GIAN LẬN & DỰ BÁO PHÁ SẢN
- Thuật toán Beneish M-Score 8 Biến Số Toàn Diện (Howard Schilit & Messod Beneish)
- Thuật toán Altman Z''-Score (Thị trường Mới nổi & Doanh nghiệp Phi sản xuất)
- Bộ Kiểm Định 7 Chiêu Trò Gian Lận Lợi Nhuận & Dòng Tiền (Howard Schilit 4th Edition)
- Bộ Tạo Dữ Liệu Đa Giác Radar 8 Trục Phục Vụ Apache ECharts Trực Quan Hóa
========================================================================================
"""

import numpy as np
import pandas as pd

class ForensicAgent:
    """Agent chuyên trách Kiểm toán Gian lận BCTC và Sức khỏe Tài chính Doanh nghiệp."""

    @staticmethod
    def audit(df: pd.DataFrame, archetype: str = 'STANDARD') -> dict:
        """
        Thực hiện kiểm toán toàn diện trên chuỗi dữ liệu BCTC.
        Trả về kết quả chi tiết, điểm rủi ro, cờ cảnh báo Schilit và dữ liệu Radar ECharts.
        """
        if df.empty or len(df) < 2:
            return ForensicAgent._get_fallback_audit()

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # 1. TÍNH TOÁN 8 BIẾN SỐ BENEISH M-SCORE
        # -----------------------------------------------------------------------------
        # DSRI: Days Sales in Receivables Index
        dsri = 1.0
        if latest.get('rev', 0) > 0 and prev.get('rev', 0) > 0 and prev.get('ar', 0) > 0:
            dsri = (latest.get('ar', 0) / latest['rev']) / (prev.get('ar', 0) / prev['rev'])
        dsri = float(np.clip(dsri, 0.2, 5.0))

        # GMI: Gross Margin Index
        gmi = 1.0
        gm_curr = (latest.get('gp', 0) / latest['rev']) if latest.get('rev', 0) > 0 else 0.20
        gm_prev = (prev.get('gp', 0) / prev['rev']) if prev.get('rev', 0) > 0 else 0.20
        if gm_curr > 0:
            gmi = gm_prev / gm_curr
        gmi = float(np.clip(gmi, 0.2, 5.0))

        # AQI: Asset Quality Index (Tài sản phi lưu động khác PPE so với Tổng tài sản)
        aqi = 1.0
        ta_curr = latest.get('ta', 1.0)
        ta_prev = prev.get('ta', 1.0)
        if ta_curr > 0 and ta_prev > 0:
            non_curr_curr = 1.0 - (latest.get('ca', 0) + latest.get('net_ppe', 0)) / ta_curr
            non_curr_prev = 1.0 - (prev.get('ca', 0) + prev.get('net_ppe', 0)) / ta_prev
            if non_curr_prev > 0.01:
                aqi = non_curr_curr / non_curr_prev
        aqi = float(np.clip(aqi, 0.2, 5.0))

        # SGI: Sales Growth Index
        sgi = 1.0
        if prev.get('rev', 0) > 0:
            sgi = latest.get('rev', 0) / prev['rev']
        sgi = float(np.clip(sgi, 0.2, 5.0))

        # DEPI: Depreciation Index
        depi = 1.0
        depr_rate_curr = latest.get('depr', 0) / (latest.get('net_ppe', 0) + latest.get('depr', 0)) if (latest.get('net_ppe', 0) + latest.get('depr', 0)) > 0 else 0.1
        depr_rate_prev = prev.get('depr', 0) / (prev.get('net_ppe', 0) + prev.get('depr', 0)) if (prev.get('net_ppe', 0) + prev.get('depr', 0)) > 0 else 0.1
        if depr_rate_curr > 0:
            depi = depr_rate_prev / depr_rate_curr
        depi = float(np.clip(depi, 0.2, 5.0))

        # SGAI: Sales, General and Administrative expenses Index
        sgai = 1.0
        sga_rate_curr = latest.get('sga', 0) / latest['rev'] if latest.get('rev', 0) > 0 else 0.05
        sga_rate_prev = prev.get('sga', 0) / prev['rev'] if prev.get('rev', 0) > 0 else 0.05
        if sga_rate_prev > 0:
            sgai = sga_rate_curr / sga_rate_prev
        sgai = float(np.clip(sgai, 0.2, 5.0))

        # LVGI: Leverage Index (Tổng nợ / Tổng tài sản)
        lvgi = 1.0
        lev_curr = latest.get('tl', 0) / ta_curr if ta_curr > 0 else 0.5
        lev_prev = prev.get('tl', 0) / ta_prev if ta_prev > 0 else 0.5
        if lev_prev > 0:
            lvgi = lev_curr / lev_prev
        lvgi = float(np.clip(lvgi, 0.2, 5.0))

        # TATA: Total Accruals to Total Assets
        tata = (latest.get('ni', 0) - latest.get('cfo', 0)) / ta_curr if ta_curr > 0 else 0.0
        tata = float(np.clip(tata, -1.0, 1.0))

        # Công thức hồi quy chuẩn Beneish M-Score 8 biến
        m_score = (
            -4.84 
            + 0.920 * dsri 
            + 0.528 * gmi 
            + 0.404 * aqi 
            + 0.892 * sgi 
            + 0.115 * depi 
            - 0.172 * sgai 
            + 4.037 * tata 
            + 0.0327 * lvgi
        )

        if m_score < -2.22:
            m_status = "🟢 An toàn: Chất lượng lợi nhuận cao, xác suất gian lận < 5%"
            m_color = "emerald"
            m_risk_level = "LOW"
        elif m_score <= -1.78:
            m_status = "🟡 Vùng xám: Có dấu hiệu dồn tích dồn nén, cần giám sát kỹ"
            m_color = "amber"
            m_risk_level = "MEDIUM"
        else:
            m_status = "🔴 Cảnh báo đỏ: Nguy cơ thao túng BCTC & dồn tích doanh thu cao"
            m_color = "rose"
            m_risk_level = "HIGH"

        # 2. TÍNH TOÁN ALTMAN Z''-SCORE (EMERGING MARKETS)
        # -----------------------------------------------------------------------------
        x1 = (latest.get('ca', 0) - latest.get('cl', 0)) / ta_curr if ta_curr > 0 else 0.2
        x2 = latest.get('re', 0) / ta_curr if ta_curr > 0 else 0.1
        x3 = latest.get('ebit', 0) / ta_curr if ta_curr > 0 else 0.1
        x4 = latest.get('eq', 0) / latest.get('tl', 1.0) if latest.get('tl', 0) > 0 else 2.0
        z_score = float(6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4)

        if z_score > 2.60:
            z_status = "🟢 Vùng An Toàn (Safe Zone): Khả năng vỡ nợ gần như bằng 0"
            z_color = "emerald"
        elif z_score >= 1.10:
            z_status = "🟡 Vùng Cảnh Báo (Grey Zone): Đòn bẩy vừa phải, cần theo dõi dòng tiền"
            z_color = "amber"
        else:
            z_status = "🔴 Vùng Kiệt Quệ (Distress Zone): Rủi ro mất thanh khoản & tái cơ cấu nợ"
            z_color = "rose"

        # 3. RÀ SOÁT TRỌN BỘ 7 CHIÊU TRÒ SCHILIT FINANCIAL SHENANIGANS
        # -----------------------------------------------------------------------------
        schilit_flags = []
        dso_curr = (latest.get('ar', 0) / latest['rev'] * 365) if latest.get('rev', 0) > 0 else 0.0
        cfo_ni_ratio = (latest.get('cfo', 0) / latest.get('ni', 1.0)) if latest.get('ni', 0) > 0 else 0.0
        rev_growth = ((latest.get('rev', 0) - prev.get('rev', 0)) / prev['rev'] * 100) if prev.get('rev', 0) > 0 else 0.0
        ar_growth = ((latest.get('ar', 0) - prev.get('ar', 0)) / prev['ar'] * 100) if prev.get('ar', 0) > 0 else 0.0

        # EM 1: Ghi nhận doanh thu quá sớm (Revenue Too Soon)
        if ar_growth > rev_growth + 25.0 and dso_curr > 75.0:
            schilit_flags.append({
                'code': 'EM-1',
                'title': 'Ghi nhận doanh thu quá sớm (Recording Revenue Too Soon)',
                'level': 'HIGH',
                'desc': f'Tốc độ tăng khoản phải thu (+{ar_growth:.1f}%) bỏ xa tăng trưởng doanh thu (+{rev_growth:.1f}%). DSO đạt {dso_curr:.0f} ngày.',
                'icon': 'ClockAlert'
            })
        elif dsri > 1.30:
            schilit_flags.append({
                'code': 'EM-1',
                'title': 'Nghi vấn dồn nợ phải thu (Bill-and-Hold / DSRI Surge)',
                'level': 'MEDIUM',
                'desc': f'Chỉ số DSRI ở mức {dsri:.2f}x cho thấy khách hàng chưa thanh toán kịp với tốc độ ghi nhận doanh thu.',
                'icon': 'Clock'
            })

        # EM 2: Ghi nhận doanh thu giả mạo / Lợi nhuận không có tiền mặt (Bogus Revenue)
        if latest.get('ni', 0) > 0 and latest.get('cfo', 0) < 0:
            schilit_flags.append({
                'code': 'EM-2',
                'title': 'Lợi nhuận ròng dương nhưng Dòng tiền kinh doanh (CFO) âm',
                'level': 'HIGH',
                'desc': f'LNST đạt {latest.get("ni", 0)/1e9:,.0f} Tỷ nhưng CFO âm {abs(latest.get("cfo", 0))/1e9:,.0f} Tỷ. Nguy cơ lãi ảo trên giấy tờ.',
                'icon': 'AlertTriangle'
            })
        elif 0.0 < cfo_ni_ratio < 0.40 and latest.get('ni', 0) > 0:
            schilit_flags.append({
                'code': 'EM-2',
                'title': 'Chất lượng dồn tích yếu (CFO / NI < 0.4x)',
                'level': 'MEDIUM',
                'desc': f'Tỷ lệ tiền mặt thu từ HĐKD chỉ đạt {cfo_ni_ratio:.2f} lần lợi nhuận ròng.',
                'icon': 'AlertCircle'
            })

        # EM 3: Thổi phồng lợi nhuận bằng thu nhập một lần (One-Time Gains)
        ebit_margin_curr = (latest.get('ebit', 0) / latest['rev']) if latest.get('rev', 0) > 0 else 0.0
        ebit_margin_prev = (prev.get('ebit', 0) / prev['rev']) if prev.get('rev', 0) > 0 else 0.0
        if ebit_margin_curr > ebit_margin_prev + 0.08 and gm_curr <= gm_prev:
            schilit_flags.append({
                'code': 'EM-3',
                'title': 'Biên EBIT tăng vọt bất thường dù Biên Lãi Gộp đi ngang',
                'level': 'MEDIUM',
                'desc': 'Nghi vấn pha trộn thu nhập một lần (bán tài sản/hoàn nhập) vào lợi nhuận cốt lõi.',
                'icon': 'TrendingUp'
            })

        # EM 4: Đẩy chi phí kỳ này sang kỳ sau (Vốn hóa chi phí bừa bãi - Improper Capitalization)
        if aqi > 1.35 and depi > 1.25:
            schilit_flags.append({
                'code': 'EM-4',
                'title': 'Vốn hóa chi phí quá mức / Giảm tốc độ khấu hao (WorldCom Trap)',
                'level': 'HIGH',
                'desc': f'Tài sản phi lưu động khác phình to (AQI={aqi:.2f}) kết hợp tỷ lệ khấu hao giảm sút (DEPI={depi:.2f}).',
                'icon': 'Layers'
            })

        # EM 5: Giấu nhẹm nghĩa vụ nợ (Hiding Liabilities)
        if lvgi > 1.30 and latest.get('cl', 0) > latest.get('ca', 0):
            schilit_flags.append({
                'code': 'EM-5',
                'title': 'Nợ ngắn hạn vượt tài sản ngắn hạn (Working Capital Deficit)',
                'level': 'HIGH',
                'desc': f'Hệ số nợ tăng vọt {lvgi:.2f}x và vốn lưu động ròng âm {((latest.get("ca", 0)-latest.get("cl", 0))/1e9):,.0f} Tỷ.',
                'icon': 'ShieldAlert'
            })

        # EM 6: Hũ bánh quy (Cookie Jar Reserves)
        if len(df) >= 4:
            margins = [r['ni'] / r['rev'] for _, r in df.iloc[-4:].iterrows() if r.get('rev', 0) > 0]
            if len(margins) >= 4 and np.std(margins) < 0.005 and rev_growth > 30.0:
                schilit_flags.append({
                    'code': 'EM-6',
                    'title': 'Dấu hiệu làm phẳng lợi nhuận (Earnings Smoothing / Cookie Jar)',
                    'level': 'LOW',
                    'desc': 'Biên lợi nhuận phẳng tuyệt đối bất chấp doanh thu biến động mạnh.',
                    'icon': 'Database'
                })

        # EM 7: Tắm gội sạch sẽ (The Big Bath)
        if prev.get('ni', 0) < 0 and latest.get('ni', 0) > 0 and (latest.get('ni', 0) / abs(prev.get('ni', 1.0))) > 2.5:
            schilit_flags.append({
                'code': 'EM-7',
                'title': 'Khả năng có hiệu ứng The Big Bath ở năm trước',
                'level': 'LOW',
                'desc': 'Lợi nhuận năm nay bật tăng thần kỳ sau khi năm trước ghi nhận lỗ xóa sổ tài sản.',
                'icon': 'Sparkles'
            })

        # 4. TẠO DỮ LIỆU RADAR 8 TRỤC PHỤC VỤ APACHE ECHARTS
        # -----------------------------------------------------------------------------
        # Chuẩn hóa về thang điểm 0 - 100 (Càng cao càng rủi ro)
        def scale_risk(val, benchmark, max_val):
            ratio = (val - benchmark) / (max_val - benchmark) if max_val > benchmark else 0.0
            return float(np.clip(ratio * 100.0, 5.0, 100.0))

        radar_8_axes = [
            {'name': 'Phải Thu (DSRI)', 'value': scale_risk(dsri, 1.0, 2.0), 'max': 100, 'raw': f"{dsri:.2f}x"},
            {'name': 'Biên Lãi Gộp (GMI)', 'value': scale_risk(gmi, 1.0, 1.8), 'max': 100, 'raw': f"{gmi:.2f}x"},
            {'name': 'Tài Sản Khác (AQI)', 'value': scale_risk(aqi, 1.0, 2.0), 'max': 100, 'raw': f"{aqi:.2f}x"},
            {'name': 'Tăng Doanh Thu (SGI)', 'value': scale_risk(sgi, 1.0, 2.5), 'max': 100, 'raw': f"{sgi:.2f}x"},
            {'name': 'Khấu Hao (DEPI)', 'value': scale_risk(depi, 1.0, 1.8), 'max': 100, 'raw': f"{depi:.2f}x"},
            {'name': 'Chi Phí QL (SGAI)', 'value': scale_risk(sgai, 1.0, 1.8), 'max': 100, 'raw': f"{sgai:.2f}x"},
            {'name': 'Đòn Bẩy Nợ (LVGI)', 'value': scale_risk(lvgi, 1.0, 2.0), 'max': 100, 'raw': f"{lvgi:.2f}x"},
            {'name': 'Dồn Tích (TATA)', 'value': scale_risk(tata + 0.5, 0.5, 1.0), 'max': 100, 'raw': f"{tata:.2f}"}
        ]

        composite_risk_score = float(np.mean([item['value'] for item in radar_8_axes]))

        return {
            'm_score': round(m_score, 3),
            'm_status': m_status,
            'm_color': m_color,
            'm_risk_level': m_risk_level,
            'z_score': round(z_score, 2),
            'z_status': z_status,
            'z_color': z_color,
            'cfo_ni_ratio': round(cfo_ni_ratio, 2),
            'dso_days': round(dso_curr, 0),
            'gross_margin_pct': round(gm_curr * 100, 1),
            'schilit_flags': schilit_flags,
            'total_flags': len(schilit_flags),
            'radar_8_axes': radar_8_axes,
            'composite_risk_score': round(composite_risk_score, 1)
        }

    @staticmethod
    def _get_fallback_audit() -> dict:
        return {
            'm_score': -2.50,
            'm_status': "🟢 Bình thường (Dữ liệu chưa đủ 2 năm)",
            'm_color': "emerald",
            'm_risk_level': "LOW",
            'z_score': 2.80,
            'z_status': "🟢 Vùng an toàn",
            'z_color': "emerald",
            'cfo_ni_ratio': 1.0,
            'dso_days': 45.0,
            'gross_margin_pct': 25.0,
            'schilit_flags': [],
            'total_flags': 0,
            'radar_8_axes': [
                {'name': 'Phải Thu', 'value': 20, 'max': 100, 'raw': '1.0x'},
                {'name': 'Biên Gộp', 'value': 20, 'max': 100, 'raw': '1.0x'},
                {'name': 'Tài Sản Khác', 'value': 20, 'max': 100, 'raw': '1.0x'},
                {'name': 'Tăng Doanh Thu', 'value': 20, 'max': 100, 'raw': '1.0x'},
                {'name': 'Khấu Hao', 'value': 20, 'max': 100, 'raw': '1.0x'},
                {'name': 'Chi Phí QL', 'value': 20, 'max': 100, 'raw': '1.0x'},
                {'name': 'Đòn Bẩy Nợ', 'value': 20, 'max': 100, 'raw': '1.0x'},
                {'name': 'Dồn Tích', 'value': 20, 'max': 100, 'raw': '0.0'}
            ],
            'composite_risk_score': 20.0
        }

