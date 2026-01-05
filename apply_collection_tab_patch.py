#!/usr/bin/env python3
"""
수금 탭 패치 스크립트
이 스크립트는 flask_dashboard.py에 수금 탭 기능을 추가합니다.

사용법: python apply_collection_tab_patch.py
"""

import re
import shutil
from datetime import datetime

FILE_PATH = r'C:\Users\BFL\Desktop\business_metrics\flask_dashboard.py'

# 백업 생성
backup_path = FILE_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print("=" * 60)
print("수금 탭 패치 스크립트")
print("=" * 60)

# 파일 읽기
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 백업
shutil.copy(FILE_PATH, backup_path)
print(f"✓ 백업 생성: {backup_path}")

changes_made = 0

# 1. 수금 탭 버튼 추가 (검사항목 탭 버튼 다음에)
if "showTab('collection')" not in content:
    old_pattern = """<div class="tab-card" onclick="showTab('foodItem')">
                <div class="tab-icon">🔬</div>
                <div class="tab-label">검사항목</div>
            </div>
        </section>"""

    new_pattern = """<div class="tab-card" onclick="showTab('foodItem')">
                <div class="tab-icon">🔬</div>
                <div class="tab-label">검사항목</div>
            </div>
            <div class="tab-card" onclick="showTab('collection')">
                <div class="tab-icon">💵</div>
                <div class="tab-label">수금</div>
            </div>
        </section>"""

    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        changes_made += 1
        print("✓ 수금 탭 버튼 추가 완료")
    else:
        print("⚠ 수금 탭 버튼 위치를 찾을 수 없습니다")

# 2. 수금 탭 UI 추가 (AI 분석 탭 이전에)
if 'id="collection"' not in content:
    collection_ui = '''
        <!-- 수금 탭 -->
        <div id="collection" class="tab-content">
            <!-- 수금 KPI -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px;">
                <div class="card" style="text-align: center; padding: 20px;">
                    <div style="color: #6b7280; font-size: 13px; margin-bottom: 8px;">총 매출</div>
                    <div id="collectionTotalSales" style="font-size: 24px; font-weight: 700; color: #2563eb;">-</div>
                </div>
                <div class="card" style="text-align: center; padding: 20px;">
                    <div style="color: #6b7280; font-size: 13px; margin-bottom: 8px;">수금 완료</div>
                    <div id="collectionPaid" style="font-size: 24px; font-weight: 700; color: #059669;">-</div>
                </div>
                <div class="card" style="text-align: center; padding: 20px;">
                    <div style="color: #6b7280; font-size: 13px; margin-bottom: 8px;">미수금</div>
                    <div id="collectionUnpaid" style="font-size: 24px; font-weight: 700; color: #dc2626;">-</div>
                </div>
                <div class="card" style="text-align: center; padding: 20px;">
                    <div style="color: #6b7280; font-size: 13px; margin-bottom: 8px;">수금률</div>
                    <div id="collectionRate" style="font-size: 24px; font-weight: 700; color: #7c3aed;">-</div>
                </div>
            </div>

            <!-- 평균 수금 기간 -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
                <div class="card" style="text-align: center; padding: 20px;">
                    <div style="color: #6b7280; font-size: 13px; margin-bottom: 8px;">평균 수금 기간</div>
                    <div id="avgCollectionDays" style="font-size: 24px; font-weight: 700; color: #0891b2;">-</div>
                </div>
                <div class="card" style="text-align: center; padding: 20px;">
                    <div style="color: #6b7280; font-size: 13px; margin-bottom: 8px;">최단 수금</div>
                    <div id="minCollectionDays" style="font-size: 24px; font-weight: 700; color: #059669;">-</div>
                </div>
                <div class="card" style="text-align: center; padding: 20px;">
                    <div style="color: #6b7280; font-size: 13px; margin-bottom: 8px;">최장 수금</div>
                    <div id="maxCollectionDays" style="font-size: 24px; font-weight: 700; color: #dc2626;">-</div>
                </div>
            </div>

            <!-- 차트 영역 -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">📊 담당별 수금 현황</span>
                    </div>
                    <div class="card-body"><div class="chart-container"><canvas id="collectionByManagerChart"></canvas></div></div>
                </div>
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">📈 월별 수금 추이</span>
                    </div>
                    <div class="card-body"><div class="chart-container"><canvas id="collectionMonthlyChart"></canvas></div></div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">⏱️ 수금 기간 분포</span>
                    </div>
                    <div class="card-body"><div class="chart-container"><canvas id="collectionDaysChart"></canvas></div></div>
                </div>
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">🥧 입금 구분별 현황</span>
                    </div>
                    <div class="card-body"><div class="chart-container"><canvas id="collectionTypeChart"></canvas></div></div>
                </div>
            </div>

            <!-- 미수금 업체 목록 -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">🚨 미수금 업체 현황</span>
                    <span class="card-badge" id="unpaidCountBadge">0건</span>
                </div>
                <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                    <table class="data-table" id="unpaidTable">
                        <thead>
                            <tr>
                                <th>업체명</th>
                                <th>접수일자</th>
                                <th>미수금액</th>
                                <th>경과일</th>
                                <th>영업담당</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- AI 분석 탭 -->'''

    if '<!-- AI 분석 탭 -->' in content:
        content = content.replace('<!-- AI 분석 탭 -->', collection_ui)
        changes_made += 1
        print("✓ 수금 탭 UI 추가 완료")
    else:
        print("⚠ AI 분석 탭 위치를 찾을 수 없습니다")

# 3. JavaScript 함수 추가 (세션 정보 로드 함수 이전에)
if 'updateCollectionTab' not in content:
    js_code = '''
        // ============ 수금 탭 ============
        let collectionData = null;
        let collectionCharts = {};

        async function updateCollectionTab() {
            const year = document.getElementById('yearSelect').value;
            try {
                const res = await fetch(`/api/collection?year=${year}`);
                collectionData = await res.json();
                updateCollectionKPI();
                updateCollectionCharts();
                updateUnpaidTable();
            } catch (e) {
                console.error('수금 데이터 로드 실패:', e);
            }
        }

        function updateCollectionKPI() {
            if (!collectionData) return;
            document.getElementById('collectionTotalSales').textContent = formatCurrency(collectionData.total_sales || 0);
            document.getElementById('collectionPaid').textContent = formatCurrency(collectionData.paid_amount || 0);
            document.getElementById('collectionUnpaid').textContent = formatCurrency(collectionData.unpaid_amount || 0);
            document.getElementById('collectionRate').textContent = (collectionData.collection_rate || 0) + '%';
            document.getElementById('avgCollectionDays').textContent = (collectionData.avg_days || 0) + '일';
            document.getElementById('minCollectionDays').textContent = (collectionData.min_days || 0) + '일';
            document.getElementById('maxCollectionDays').textContent = (collectionData.max_days || 0) + '일';
        }

        function updateCollectionCharts() {
            if (!collectionData) return;

            // 담당별 수금 차트
            const managerCtx = document.getElementById('collectionByManagerChart');
            if (managerCtx) {
                if (collectionCharts.manager) collectionCharts.manager.destroy();
                const managerData = collectionData.by_manager || [];
                collectionCharts.manager = new Chart(managerCtx, {
                    type: 'bar',
                    data: {
                        labels: managerData.map(d => d[0]),
                        datasets: [{
                            label: '수금',
                            data: managerData.map(d => d[1].paid),
                            backgroundColor: 'rgba(34, 197, 94, 0.7)'
                        }, {
                            label: '미수금',
                            data: managerData.map(d => d[1].unpaid),
                            backgroundColor: 'rgba(239, 68, 68, 0.7)'
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true }, y: { stacked: true, ticks: { callback: v => (v/100000000).toFixed(1) + '억' } } } }
                });
            }

            // 월별 수금 차트
            const monthlyCtx = document.getElementById('collectionMonthlyChart');
            if (monthlyCtx) {
                if (collectionCharts.monthly) collectionCharts.monthly.destroy();
                const monthlyData = collectionData.by_month || [];
                collectionCharts.monthly = new Chart(monthlyCtx, {
                    type: 'line',
                    data: {
                        labels: monthlyData.map(d => d[0] + '월'),
                        datasets: [{
                            label: '수금액',
                            data: monthlyData.map(d => d[1].paid),
                            borderColor: '#22c55e',
                            backgroundColor: 'rgba(34, 197, 94, 0.1)',
                            fill: true,
                            tension: 0.3
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { callback: v => (v/100000000).toFixed(1) + '억' } } } }
                });
            }

            // 수금 기간 분포 차트
            const daysCtx = document.getElementById('collectionDaysChart');
            if (daysCtx) {
                if (collectionCharts.days) collectionCharts.days.destroy();
                const daysData = collectionData.days_distribution || [];
                collectionCharts.days = new Chart(daysCtx, {
                    type: 'bar',
                    data: {
                        labels: daysData.map(d => d[0]),
                        datasets: [{
                            label: '건수',
                            data: daysData.map(d => d[1]),
                            backgroundColor: ['#22c55e', '#84cc16', '#eab308', '#f97316', '#ef4444']
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
                });
            }

            // 입금 구분별 차트
            const typeCtx = document.getElementById('collectionTypeChart');
            if (typeCtx) {
                if (collectionCharts.type) collectionCharts.type.destroy();
                const typeData = collectionData.by_type || [];
                collectionCharts.type = new Chart(typeCtx, {
                    type: 'doughnut',
                    data: {
                        labels: typeData.map(d => d[0]),
                        datasets: [{
                            data: typeData.map(d => d[1]),
                            backgroundColor: ['#3b82f6', '#22c55e', '#eab308', '#f97316', '#ef4444', '#8b5cf6', '#ec4899']
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }
        }

        function updateUnpaidTable() {
            if (!collectionData) return;
            const tbody = document.querySelector('#unpaidTable tbody');
            const unpaidList = collectionData.unpaid_list || [];
            document.getElementById('unpaidCountBadge').textContent = unpaidList.length + '건';

            tbody.innerHTML = unpaidList.map(item => `
                <tr>
                    <td>${item.company || '-'}</td>
                    <td>${item.date || '-'}</td>
                    <td style="text-align:right; color:#dc2626; font-weight:600;">${formatCurrency(item.amount)}</td>
                    <td style="text-align:center; ${item.days > 60 ? 'color:#dc2626; font-weight:bold;' : ''}">${item.days}일</td>
                    <td>${item.manager || '-'}</td>
                </tr>
            `).join('');
        }

        // 세션 정보 로드'''

    if '// 세션 정보 로드' in content:
        content = content.replace('// 세션 정보 로드', js_code)
        changes_made += 1
        print("✓ JavaScript 함수 추가 완료")
    else:
        print("⚠ 세션 정보 로드 위치를 찾을 수 없습니다")

# 4. updateCollectionTab() 호출 추가
if 'updateCollectionTab();' not in content:
    old_call = 'updateFoodItemTab();'
    new_call = '''updateFoodItemTab();
            updateCollectionTab();'''

    if old_call in content:
        content = content.replace(old_call, new_call, 1)
        changes_made += 1
        print("✓ updateCollectionTab() 호출 추가 완료")
    else:
        print("⚠ updateFoodItemTab() 호출을 찾을 수 없습니다")

# 5. API 엔드포인트 추가
if "@app.route('/api/collection')" not in content:
    api_code = '''

@app.route('/api/collection')
def get_collection_data():
    """수금 현황 API"""
    from datetime import datetime, date
    year = request.args.get('year', '2025')

    # 데이터 로드
    data = load_data(year)

    today = date.today()
    total_sales = 0
    paid_amount = 0
    unpaid_amount = 0
    collection_days = []  # 수금 기간 리스트
    by_manager = {}  # 담당별 수금
    by_month = {}  # 월별 수금
    by_type = {}  # 입금 구분별
    unpaid_list = []  # 미수금 목록

    for row in data:
        sales = row.get('총금액', 0) or 0
        if isinstance(sales, str):
            sales = float(sales.replace(',', '').replace('원', '')) if sales else 0

        total_sales += sales

        manager = str(row.get('영업담당', '') or '').strip() or '미지정'
        payment_status = str(row.get('입금여부', '') or '').strip()
        payment_date_str = str(row.get('입금일', '') or '').strip()
        reception_date_str = str(row.get('접수일자', '') or '').strip()
        payment_type = str(row.get('입금구분', '') or '').strip() or '기타'
        company = str(row.get('업체명', '') or '').strip()

        # 담당별 초기화
        if manager not in by_manager:
            by_manager[manager] = {'total': 0, 'paid': 0, 'unpaid': 0}
        by_manager[manager]['total'] += sales

        # 입금 구분별
        if payment_type not in by_type:
            by_type[payment_type] = 0

        # 입금 여부 확인
        is_paid = payment_status in ['Y', 'y', '완료', '입금', '입금완료', '수금', '수금완료']

        if is_paid and sales > 0:
            paid_amount += sales
            by_manager[manager]['paid'] += sales
            by_type[payment_type] += sales

            # 수금 기간 계산
            try:
                if reception_date_str and payment_date_str:
                    reception_date = datetime.strptime(reception_date_str[:10], '%Y-%m-%d').date()
                    payment_date = datetime.strptime(payment_date_str[:10], '%Y-%m-%d').date()
                    days = (payment_date - reception_date).days
                    if 0 <= days <= 365:  # 합리적인 범위
                        collection_days.append(days)

                    # 월별 수금
                    month = payment_date.month
                    if month not in by_month:
                        by_month[month] = {'paid': 0, 'count': 0}
                    by_month[month]['paid'] += sales
                    by_month[month]['count'] += 1
            except:
                pass
        else:
            unpaid_amount += sales
            by_manager[manager]['unpaid'] += sales

            # 미수금 목록 추가
            if sales > 0:
                elapsed_days = 0
                try:
                    if reception_date_str:
                        reception_date = datetime.strptime(reception_date_str[:10], '%Y-%m-%d').date()
                        elapsed_days = (today - reception_date).days
                except:
                    pass

                unpaid_list.append({
                    'company': company,
                    'date': reception_date_str[:10] if reception_date_str else '-',
                    'amount': sales,
                    'days': elapsed_days,
                    'manager': manager
                })

    # 수금 기간 통계
    avg_days = sum(collection_days) / len(collection_days) if collection_days else 0
    min_days = min(collection_days) if collection_days else 0
    max_days = max(collection_days) if collection_days else 0

    # 수금 기간 분포 (구간별)
    days_distribution = {'0-7일': 0, '8-14일': 0, '15-30일': 0, '31-60일': 0, '60일+': 0}
    for d in collection_days:
        if d <= 7:
            days_distribution['0-7일'] += 1
        elif d <= 14:
            days_distribution['8-14일'] += 1
        elif d <= 30:
            days_distribution['15-30일'] += 1
        elif d <= 60:
            days_distribution['31-60일'] += 1
        else:
            days_distribution['60일+'] += 1

    # 담당별 정렬
    by_manager_sorted = sorted(by_manager.items(), key=lambda x: x[1]['total'], reverse=True)[:15]

    # 미수금 목록 정렬 (금액 높은 순)
    unpaid_list_sorted = sorted(unpaid_list, key=lambda x: x['amount'], reverse=True)[:50]

    # 수금률
    collection_rate = (paid_amount / total_sales * 100) if total_sales > 0 else 0

    return jsonify({
        'year': int(year),
        'total_sales': total_sales,
        'paid_amount': paid_amount,
        'unpaid_amount': unpaid_amount,
        'collection_rate': round(collection_rate, 1),
        'avg_days': round(avg_days, 1),
        'min_days': min_days,
        'max_days': max_days,
        'by_manager': by_manager_sorted,
        'by_month': sorted(by_month.items()),
        'by_type': sorted(by_type.items(), key=lambda x: x[1], reverse=True),
        'days_distribution': list(days_distribution.items()),
        'unpaid_list': unpaid_list_sorted
    })

'''

    # API 엔드포인트 추가 위치 찾기 (food_item/verify 전에)
    if "@app.route('/api/food_item/verify')" in content:
        content = content.replace("@app.route('/api/food_item/verify')", api_code + "@app.route('/api/food_item/verify')")
        changes_made += 1
        print("✓ API 엔드포인트 추가 완료")
    else:
        # 대안: 파일 끝에 추가
        if "if __name__ == '__main__':" in content:
            content = content.replace("if __name__ == '__main__':", api_code + "if __name__ == '__main__':")
            changes_made += 1
            print("✓ API 엔드포인트 추가 완료 (파일 끝)")
        else:
            print("⚠ API 추가 위치를 찾을 수 없습니다")

# 결과 저장
if changes_made > 0:
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("\n" + "=" * 60)
    print(f"✓ 패치 완료! {changes_made}개 변경사항 적용됨")
    print("=" * 60)
    print("\n서버를 재시작해주세요:")
    print("  1. 기존 flask 프로세스 종료")
    print("  2. python flask_dashboard.py 재실행")
else:
    print("\n⚠ 변경사항이 없습니다 (이미 적용됨)")
