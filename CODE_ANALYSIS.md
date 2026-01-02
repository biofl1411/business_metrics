# 경영지표 분석기 (Business Metrics Analyzer) 전체 코드 분석

> 작성일: 2026-01-02
> 서버 정보: 공인 IP 14.7.14.31 / 내부 IP 192.168.0.96 / 포트 6001

---

## 프로젝트 구조

```
/home/user/business_metrics/
├── main.py                  # 진입점 (GUI/CLI 모드)
├── dashboard.py             # Streamlit 대시보드 (391줄)
├── flask_dashboard.py       # Flask 웹 대시보드 (2829줄) ⭐ 메인
├── requirements.txt         # 의존성 패키지
├── .gitignore
├── config/
│   ├── __init__.py
│   └── settings.py          # 설정 및 매핑 정보 (107줄)
├── modules/
│   ├── __init__.py
│   ├── data_loader.py       # 엑셀 데이터 로더 (181줄)
│   ├── data_processor.py    # 데이터 전처리 (273줄)
│   ├── metrics_calculator.py # 지표 계산 (412줄)
│   ├── report_generator.py  # 보고서 생성 (305줄)
│   └── target_manager.py    # 목표 관리 (235줄)
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # PyQt5 메인 윈도우 (636줄)
│   └── dashboard_widgets.py # PyQt5 위젯 컴포넌트 (349줄)
└── data/
    ├── 2024/                # 2024년 엑셀 데이터
    ├── 2025/                # 2025년 엑셀 데이터
    └── targets/             # 목표 데이터
```

---

## 핵심 파일 상세 분석

### 1. flask_dashboard.py (2829줄) - 메인 웹 대시보드

**서버 설정:**
- IP: `0.0.0.0` (모든 인터페이스)
- 포트: `6001`
- 공인 IP: `14.7.14.31`, 내부 IP: `192.168.0.96`

**주요 기능:**

| 탭 | 기능 |
|---|---|
| 👤 개인별 | 영업담당별 매출/건수/비중 차트/테이블 |
| 🏢 팀별 | 지사/센터별 매출 분석 |
| 📅 월별 | 월별 매출 추이 라인 차트 |
| 🏭 업체별 | TOP 20 업체, 고효율 업체, 대량 업체 |
| 📍 지역별 | 시/도/군/구별 매출 분석 |
| 🎯 목적별 | 검사목적별 분석 + 담당자/지역 필터 |
| 🧪 유형 | 검체유형별 분석 |
| ⚠️ 부적합 | 부적합항목 통계 |

**핵심 함수:**

```python
load_excel_data(year)      # openpyxl로 엑셀 로드 (1시간 캐시)
extract_region(address)    # 주소에서 시/도/군/구 추출
process_data(data, filter) # 다차원 집계 처리
filter_data_by_date()      # 날짜 범위 필터링
```

**API 엔드포인트:**

| 경로 | 설명 |
|---|---|
| `/` | 메인 대시보드 HTML |
| `/api/data` | 필터링된 데이터 JSON |
| `/api/columns` | 엑셀 컬럼명 조회 |
| `/api/cache/refresh` | 캐시 초기화 |

**process_data() 반환 데이터 구조:**

```python
{
    'by_manager': [(담당자, {sales, count}), ...],
    'by_branch': [(지사, {sales, count, managers}), ...],
    'by_month': [(월, {sales, count}), ...],
    'by_client': [(거래처, {sales, count, avg}), ...],
    'by_purpose': [(검사목적, {sales, count}), ...],
    'by_defect': [(부적합항목, {count}), ...],
    'by_region': [(지역, {sales, count, sido, sigungu}), ...],
    'by_sample_type': [(검체유형, {sales, count}), ...],
    'by_purpose_month': {목적: {월: {sales, count, by_manager}}},
    'by_sample_type_month': {유형: {월: {sales, count, by_manager, by_purpose}}},
    'manager_top_clients': {담당자: [(거래처, {sales, count}), ...]},
    'high_efficiency': [(거래처, {sales, count, avg}), ...],  # 고효율
    'high_volume': [(거래처, {sales, count, avg}), ...],      # 대량
    'region_top_managers': {지역: [{name, sales, count}]},
    'manager_regions': {담당자: [{region, sales, count}]},
    'purpose_managers': {목적: [{name, sales, count}]},
    'purpose_regions': {목적: [{region, sales, count}]},
    'sample_type_managers': {유형: [{name, sales, count, by_purpose}]},
    'sample_type_purposes': {유형: [{name, sales, count}]},
    'purposes': [검사목적 목록],
    'sample_types': [검체유형 목록],
    'total_sales': 총매출,
    'total_count': 총건수
}
```

---

### 2. config/settings.py (107줄) - 설정

**영업담당 → 지사/센터 매핑:**

```python
MANAGER_TO_BRANCH = {
    # 충청지사
    "장동욱": "충청지사",
    "지병훈": "충청지사",
    "박은태": "충청지사",
    # 경북지사
    "도준구": "경북지사",
    # 전북지사
    "이강현": "전북지사",
    # 경기지사
    "엄은정": "경기지사",
    "정유경": "경기지사",
    # 서울지사
    "이성복": "서울지사",
    # 서울센터
    "조봉현": "서울센터",
    "오세중": "서울센터",
    "장동주": "서울센터",
    "오석현": "서울센터",
    # 경북센터
    "엄상흠": "경북센터",
}
```

**엑셀 컬럼 매핑:**

```python
COLUMN_MAPPING = {
    "date": ["접수일자", "날짜", "일자"],
    "sales_amount": ["수수료", "공급가액", "매출액", "금액"],
    "tax_amount": ["세액"],
    "manager": ["영업담당", "담당자"],
    "center": ["영업팀", "지부명", "센터", "부서"],
    "client": ["의뢰업체명", "거래처", "업체명"],
    "test_purpose": ["검사목적", "목적"],
    "test_count": ["항목개수", "검사건수", "건수"],
    "status": ["상태"],
    "test_field": ["시험분야"],
    "product_name": ["제품/시료명", "제품명", "시료명"],
    "receipt_no": ["접수번호"],
    "completion_date": ["완료예정일"],
    "payment_status": ["입금여부", "입금구분"],
    "payment_amount": ["입금액"],
    "outstanding": ["업체총미수금", "잔액"],
}
```

**KPI 임계값 설정:**

```python
METRICS_CONFIG = {
    "target_achievement_threshold": {
        "excellent": 120,  # 120% 이상 → 우수
        "good": 100,       # 100% 이상 → 달성
        "warning": 80,     # 80% 이상 → 주의
        "danger": 0,       # 80% 미만 → 미달
    },
}
```

---

### 3. modules/data_loader.py (181줄) - 데이터 로더

**클래스: DataLoader**

```python
class DataLoader:
    def __init__(self, column_mapping=None):
        """컬럼 매핑 설정"""

    def load_excel(self, file_path, sheet_name=None) -> pd.DataFrame:
        """
        엑셀/CSV 파일 로드
        - .xlsx, .xlsm, .xlsb: openpyxl 엔진
        - .xls: xlrd 엔진
        - .csv: utf-8-sig 인코딩
        """

    def load_multiple_files(self, file_paths) -> pd.DataFrame:
        """여러 파일을 로드하여 하나로 병합"""

    def auto_detect_columns(self, df) -> Dict[str, str]:
        """컬럼 자동 감지 (매핑 테이블 기반)"""

    def standardize_columns(self, df, column_map=None) -> pd.DataFrame:
        """컬럼명을 표준화"""

    def get_file_info(self, file_path) -> Dict:
        """파일 정보 조회 (이름, 크기, 시트 목록)"""
```

---

### 4. modules/data_processor.py (273줄) - 데이터 전처리

**클래스: DataProcessor**

```python
class DataProcessor:
    def process(self, df) -> pd.DataFrame:
        """
        전체 전처리 파이프라인:
        1. clean_data() - 빈 행/중복 제거
        2. process_dates() - 날짜 파싱
        3. add_time_columns() - year/month/quarter/weekday 추가
        4. clean_numeric_columns() - 숫자 변환 (쉼표, 원화 제거)
        5. clean_category_columns() - 카테고리 정리
        6. add_branch_column() - 영업담당→지사 매핑
        """

    def clean_data(self, df) -> pd.DataFrame:
        """빈 행 제거, 문자열 공백 제거, 중복 제거"""

    def process_dates(self, df, date_columns=None) -> pd.DataFrame:
        """날짜 컬럼 자동 탐지 및 변환"""

    def add_time_columns(self, df, date_column='date') -> pd.DataFrame:
        """
        추가되는 컬럼:
        - year, month, quarter
        - year_month (예: "2025-01")
        - year_quarter (예: "2025-Q1")
        - weekday, day_of_week
        """

    def add_branch_column(self, df, manager_column='영업담당') -> pd.DataFrame:
        """영업담당 → 지사센터 컬럼 추가"""

    def filter_date_range(self, df, start_date, end_date) -> pd.DataFrame:
        """날짜 범위 필터링"""

    def get_summary(self, df) -> Dict:
        """데이터 요약 (행수, 컬럼, 날짜범위)"""
```

---

### 5. modules/metrics_calculator.py (412줄) - 지표 계산

**클래스: MetricsCalculator**

```python
class MetricsCalculator:
    def __init__(self, df: pd.DataFrame):
        """전처리된 DataFrame 입력"""

    def calculate_all_metrics(self, targets=None) -> Dict:
        """
        모든 지표 계산:
        - summary: 요약 카드용
        - financial: 월별/분기별/연도별 매출
        - sales_by_manager: 담당자별
        - sales_by_center: 센터별
        - sales_by_purpose: 검사목적별
        - monthly_trend: 월별 추이
        - quarterly_summary: 분기별 요약
        - yoy_comparison: 전년 대비
        - operational: 운영 지표
        - kpi: 목표 달성률
        """

    def get_summary_metrics(self) -> Dict:
        """
        상단 요약 카드:
        - total_sales: 총 매출액
        - total_cost: 총 비용
        - total_profit: 총 이익
        - profit_margin: 이익률 (%)
        - avg_sales_per_transaction: 평균 거래금액
        - transaction_count: 거래 건수
        - period: 데이터 기간
        """

    def calculate_by_dimension(self, dimension) -> pd.DataFrame:
        """
        차원별 집계
        - dimension: 'manager', 'center', 'test_purpose', 'client'
        - 반환: 매출액, 평균단가, 건수, 비중(%)
        """

    def calculate_monthly_trend(self) -> pd.DataFrame:
        """월별 추이 (전월대비 증감 포함)"""

    def calculate_yoy_comparison(self) -> pd.DataFrame:
        """전년 대비 비교 (피벗 테이블)"""

    def calculate_kpi(self, targets) -> Dict:
        """
        KPI 계산:
        - sales_achievement: 매출 달성률
        - profit_achievement: 이익 달성률
        - overall_status: 우수/달성/주의/미달
        """

    def get_top_clients(self, n=10) -> pd.DataFrame:
        """상위 거래처"""

    def get_declining_items(self, threshold=-10) -> pd.DataFrame:
        """감소 항목 하이라이트"""
```

---

### 6. modules/report_generator.py (305줄) - 보고서 생성

**클래스: ReportGenerator**

```python
class ReportGenerator:
    def __init__(self, output_dir=None):
        """출력 디렉토리 설정 (기본: reports/)"""

    def generate_excel_report(self, metrics, filename=None) -> Path:
        """
        Excel 보고서 생성 (다중 시트):
        - 요약
        - 월별추이
        - 분기별
        - 담당자별
        - 센터별
        - 검사목적별
        - 전년대비
        - KPI
        """

    def generate_pdf_report(self, metrics, charts=None, filename=None) -> Path:
        """
        PDF 보고서 생성 (reportlab):
        - 요약 테이블
        - KPI 달성 현황
        - 차트 이미지 삽입
        """

    def _format_currency(self, value) -> str:
        """통화 형식 (억원/만원/원)"""
```

---

### 7. modules/target_manager.py (235줄) - 목표 관리

**클래스: TargetManager**

```python
class TargetManager:
    def __init__(self, targets_dir=None):
        """목표 파일 디렉토리 (기본: data/targets/)"""

    def load_targets(self, year=2025) -> pd.DataFrame:
        """연간 목표 로드 (CSV 또는 Excel)"""

    def get_monthly_target(self, year, month, category='총계') -> float:
        """
        월별 목표 조회
        - category: 총계, 식품/축산, 잔류물질, 신규사업
        - 반환: 천원 단위
        """

    def get_yearly_target(self, year, category='총계') -> float:
        """연간 목표 조회"""

    def calculate_achievement(self, actual, target) -> Dict:
        """
        달성률 계산:
        - rate: 달성률 (%)
        - gap: 목표 대비 차이
        - status: 우수/달성/주의/미달/목표없음
        """

    def compare_with_actual(self, actual_df, year, month=None) -> pd.DataFrame:
        """목표 대비 실적 비교"""
```

---

### 8. ui/main_window.py (636줄) - PyQt5 GUI

**클래스: MainWindow**

```python
class MainWindow(QMainWindow):
    def __init__(self):
        """
        탭 구성:
        1. 대시보드: 요약 카드 + 차트 + 테이블
        2. 상세 분석: 분석 유형 선택 + 상세 차트/테이블
        3. 설정: 목표 설정 + KPI 게이지
        """

    def create_toolbar(self, layout):
        """
        상단 툴바:
        - 엑셀 불러오기 버튼
        - 새로고침 버튼
        - Excel/PDF 보고서 버튼
        """

    def create_dashboard_tab(self) -> QWidget:
        """
        대시보드 탭:
        - 요약 카드 4개 (총매출, 총이익, 이익률, 건수)
        - 월별 매출 차트 + 센터별 비중 차트
        - 담당자별 테이블 + 전년대비 테이블
        """

    def load_excel_file(self):
        """파일 다이얼로그로 엑셀 선택 → 스레드 로딩"""

    def calculate_and_update(self):
        """지표 계산 → UI 업데이트"""

    def export_excel_report(self):
        """Excel 보고서 내보내기"""

    def export_pdf_report(self):
        """PDF 보고서 내보내기"""
```

**클래스: DataLoadThread**

```python
class DataLoadThread(QThread):
    """백그라운드 데이터 로딩 스레드"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
```

---

### 9. ui/dashboard_widgets.py (349줄) - PyQt5 위젯

**클래스: SummaryCard**

```python
class SummaryCard(QFrame):
    """
    요약 카드 위젯:
    - title: 제목 (예: "총 매출액")
    - value: 값 (예: "15억")
    - subtitle: 부제목 (예: "+10% 전년대비")
    - color: 테마 색상
    """
    def update_value(self, value, subtitle="")
    def set_status_color(self, status)  # good/warning/danger/normal
```

**클래스: ChartWidget**

```python
class ChartWidget(QWidget):
    """
    Matplotlib 차트 위젯:
    - 한글 폰트 설정 (Malgun Gothic)
    """
    def plot_bar(self, data, title)           # 수직 막대
    def plot_line(self, data, title)          # 선 그래프
    def plot_pie(self, data, title)           # 파이 차트
    def plot_horizontal_bar(self, data, title) # 수평 막대
    def save_chart(self, filepath)            # 이미지 저장
```

**클래스: DataTableWidget**

```python
class DataTableWidget(QTableWidget):
    """
    데이터 테이블 위젯:
    - 교차 색상 행
    - 음수 값 빨간색 강조
    """
    def load_dataframe(self, df, highlight_negative=False)
```

**클래스: KPIGaugeWidget**

```python
class KPIGaugeWidget(QWidget):
    """
    KPI 게이지 위젯:
    - 달성률 표시
    - 상태별 색상 (우수/달성/주의/미달)
    """
    def set_value(self, value, target)
```

---

### 10. dashboard.py (391줄) - Streamlit 대시보드

```python
# Streamlit 기반 대체 대시보드
# Plotly 차트 사용

@st.cache_data
def load_data(year) -> pd.DataFrame:
    """연도별 데이터 로드 (캐시)"""

@st.cache_data
def load_targets(year) -> pd.DataFrame:
    """목표 데이터 로드"""

def main():
    """
    사이드바: 연도/월/지사 필터
    탭 구성:
    1. 개인별 실적
    2. 팀별 실적
    3. 월별 추이
    4. 상세 분석
    """
```

---

### 11. main.py (163줄) - 진입점

```python
def run_gui():
    """PyQt5 GUI 모드 실행"""

def run_cli(input_file, output_dir='reports'):
    """
    CLI 모드 실행:
    1. 데이터 로드
    2. 데이터 전처리
    3. 지표 계산
    4. 보고서 생성 (Excel/PDF)
    """

def create_sample_data():
    """테스트용 샘플 데이터 생성"""

def main():
    """
    인자 파싱:
    - --cli input.xlsx: CLI 모드
    - --output reports: 출력 디렉토리
    - --sample: 샘플 데이터 생성
    - (기본): GUI 모드
    """
```

---

## 실행 방법

### Flask 웹 대시보드 (주 사용)

```bash
cd /home/biofl/business_metrics/business_metrics
python flask_dashboard.py
```

접속: http://14.7.14.31:6001 또는 http://192.168.0.96:6001

### PyQt5 GUI

```bash
python main.py
```

### Streamlit 대시보드

```bash
streamlit run dashboard.py
```

### CLI 모드

```bash
python main.py --cli data/2025/sample.xlsx --output reports
```

---

## 데이터 흐름

```
┌─────────────────────────────────────────────────────────────┐
│  엑셀 파일 (data/2024/*.xlsx, data/2025/*.xlsx)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  DataLoader (openpyxl 로드, 다중 파일 병합)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  DataProcessor (전처리)                                      │
│  - 날짜 파싱 (year/month/quarter)                           │
│  - 영업담당 → 지사/센터 매핑                                 │
│  - 숫자 변환, 중복 제거                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  MetricsCalculator (지표 계산)                               │
│  - 월별/분기별/연도별 집계                                   │
│  - 담당자별/센터별/목적별 분석                               │
│  - 전년대비, KPI 달성률                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  시각화 (Flask / Streamlit / PyQt5)                         │
│  - Chart.js / Plotly / Matplotlib                           │
│  - 대시보드 UI                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ReportGenerator (보고서 출력)                               │
│  - Excel 다중 시트                                           │
│  - PDF (reportlab)                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 주요 분석 항목

| 분류 | 분석 항목 |
|-----|---------|
| 매출 분석 | 총 매출, 월별 추이, 전년대비 증감률 |
| 인력 분석 | 영업담당별 실적, 지사/센터별 실적, 인당 매출 |
| 업체 분석 | TOP 매출 업체, 고효율 업체(높은 단가), 대량 거래처 |
| 지역 분석 | 시/도별 매출, 시/군/구별 매출, 지역별 담당자 |
| 목적 분석 | 검사목적별 매출 비중, 목적별 월별 추이 |
| 유형 분석 | 검체유형별 매출, 유형별 담당자/목적 |
| 품질 분석 | 부적합항목 통계, 월별 추이 |
| KPI | 목표 달성률 (우수/달성/주의/미달) |

---

## 의존성 패키지 (requirements.txt)

```
# GUI
PyQt5>=5.15.0

# Data Processing
pandas>=1.5.0
openpyxl>=3.0.0
xlrd>=2.0.0

# Visualization
matplotlib>=3.5.0
seaborn>=0.12.0

# Report Generation
reportlab>=3.6.0
Pillow>=9.0.0

# Database
SQLAlchemy>=2.0.0

# Web Dashboard
streamlit>=1.20.0
plotly>=5.10.0
```

---

## 참고 사항

1. **캐시**: Flask 대시보드는 1시간 데이터 캐시 사용 (`DATA_CACHE`, `CACHE_TIME`)
2. **한글 폰트**: `Malgun Gothic` (맑은 고딕) 사용
3. **통화 표시**: 1억 이상 → "X.X억", 1만 이상 → "X만", 그 외 → "X,XXX"
4. **주소 파싱**: 정규식으로 시/도, 시/군/구 자동 추출
5. **서버 경로**: `/home/biofl/business_metrics/business_metrics`
