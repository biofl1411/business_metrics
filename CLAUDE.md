# Business Metrics Analyzer - 프로젝트 컨텍스트

## 프로젝트 개요
음식 검사 기관의 경영 데이터를 분석하고 시각화하는 종합 분석 시스템.
엑셀 파일에서 영업 데이터를 불러와 경영지표를 계산하고, 대시보드로 시각화하며, 보고서를 생성함.

## 기술 스택
- **백엔드**: Flask, SQLAlchemy 2.0+, SQLite
- **데이터 처리**: Pandas, NumPy
- **프론트엔드**: JavaScript, Chart.js
- **GUI**: PyQt5, Matplotlib
- **AI**: Google Gemini API, Claude API
- **보고서**: openpyxl, ReportLab (PDF)

---

## 서버 구성

| 서버 | 경로 | 포트 | 용도 |
|------|------|------|------|
| 클로드 서버 | `/home/user/business_metrics/` | - | 개발/수정 |
| 운영 서버 (본 사이트) | `/home/biofl/business_metrics/` | 6001 | 실제 서비스 |
| 운영 서버 (데모) | `/home/biofl/business_metrics_demo/` | 6005 | 테스트 |

### 운영 서버 정보
- **호스트명**: bioflsever
- **사용자**: biofl
- **내부 IP**: 192.168.0.96
- **외부 IP**: 14.7.14.31

### 접속 URL
- **본 사이트**: http://192.168.0.96:6001
- **데모 사이트**: http://192.168.0.96:6005

---

## 개발 워크플로우

```
1. 클로드 서버에서 코드 수정
       ↓
2. Git 커밋 & 푸시 (세션 브랜치로 푸시됨)
       ↓
3. GitHub에서 PR 생성 → main 병합 (또는 운영서버에서 직접 병합)
       ↓
4. 운영 서버 - 데모에 먼저 적용:
   cd ~/business_metrics_demo && git pull origin main
       ↓
5. 데모 사이트(6005)에서 테스트
       ↓
6. 문제 없으면 본 사이트에 적용:
   cd ~/business_metrics && git pull origin main
       ↓
7. 서버 재시작 (필요시)
```

---

## 주요 디렉토리 구조

```
business_metrics/
├── flask_dashboard.py      # 메인 웹앱 (26,500줄+, 모든 API/라우트 포함)
├── main.py                 # CLI/GUI 진입점
├── config/settings.py      # 핵심 설정 (컬럼매핑, 담당자매핑, KPI임계값)
├── modules/
│   ├── data_loader.py      # 엑셀 파일 로드
│   ├── data_processor.py   # 데이터 전처리
│   ├── metrics_calculator.py # 경영지표 계산
│   ├── report_generator.py # Excel/PDF 보고서 생성
│   └── target_manager.py   # 목표 관리
├── ui/                     # PyQt5 GUI 컴포넌트
└── data/
    ├── users.db            # 사용자/권한 DB
    ├── business_data.db    # 데이터 캐시 DB (~1.1GB)
    ├── targets/            # 연간 목표 CSV
    ├── 2024/, 2025/        # 연도별 메인 엑셀 데이터
    └── food_item/2024/, food_item/2025/  # 음식항목 엑셀 데이터
```

---

## 데이터베이스 구조 (SQLite)

- **users.db**: users, teams, goals, permissions, team_members, 각종 로그 테이블
- **business_data.db**: excel_data, food_item_data, file_metadata, token_usage

---

## 주요 API 엔드포인트

- `/api/data` - 연도별 데이터 조회
- `/api/food_item` - 음식 항목별 검사 데이터
- `/api/admin/*` - 어드민 기능 (사용자, 팀, 목표, 권한)
- `/api/purposes` - 동적 검사목적 목록
- `/api/upload-db` - SQLite DB 파일 업로드 (Colab에서 변환된 DB)

---

## 핵심 설정 파일

`config/settings.py`:
- **COLUMN_MAPPING**: 엑셀 컬럼명 → 표준명 매핑
- **MANAGER_TO_BRANCH**: 영업담당 → 지사/센터 매핑
- **METRICS_CONFIG**: KPI 임계값 (우수:120%, 달성:100%, 주의:80%)

---

## 주의사항

1. **flask_dashboard.py**가 26,500줄+ 대규모 단일 파일임 (Blueprint 분리 안됨)
2. 컬럼명은 **COLUMN_MAPPING**에 정의된 것만 인식됨
3. **이중 DB 구조**: users.db(권한) / business_data.db(데이터캐시)
4. 프로덕션 배포 시 Gunicorn 등 WSGI 서버 필요
5. AI API 사용 시 토큰 비용 자동 추적됨 (token_usage 테이블)
6. 한글 폰트 필요 (Malgun Gothic)
7. **이전 버전으로 돌아가지 않기** - 항상 데모에서 먼저 테스트
8. **클로드 서버는 운영 서버에 직접 접근 불가** - git push 후 사용자가 pull 필요

---

## 운영 서버 명령어 모음

```bash
# Git 업데이트 (항상 main 브랜치 사용)
cd ~/business_metrics && git pull origin main
cd ~/business_metrics_demo && git pull origin main

# 본 사이트 재시작
cd ~/business_metrics
pkill -f "business_metrics/flask_dashboard.py"
nohup python flask_dashboard.py > nohup.out 2>&1 &

# 데모 사이트 재시작
cd ~/business_metrics_demo
pkill -f "business_metrics_demo/flask_dashboard.py"
nohup python flask_dashboard.py > nohup_demo.out 2>&1 &

# 프로세스 확인
ps aux | grep flask_dashboard

# 포트 확인
netstat -tlnp | grep -E "6001|6005"
```

---

## 데이터 변환 (Colab → 서버)

Colab에서 엑셀 데이터를 SQLite로 변환 후 서버에 업로드하는 방식 사용:

1. Colab에서 `data/2024/`, `data/2025/`, `data/food_item/` 폴더에 엑셀 업로드
2. 서버 실행 → 자동으로 SQLite 변환 (`business_data.db`)
3. 변환된 DB를 서버 대시보드의 `/api/upload-db`로 업로드
4. 또는 `upload_db_to_server(db_path, 'production')` 함수 사용

### SQLite 테이블
- **excel_data**: 메인 매출 데이터 (data/2024/*.xlsx, data/2025/*.xlsx)
- **food_item_data**: 음식항목 데이터 (data/food_item/2024/*.xlsx 등)
- **file_metadata**: 파일 변환 메타데이터 (mtime 추적)
