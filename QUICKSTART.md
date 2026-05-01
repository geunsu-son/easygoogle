# ⚡ gs_utils 빠른 시작 가이드

이 가이드는 `gs_utils` 패키지를 pip으로 설치 가능하게 만들고 배포하는 전체 과정을 설명합니다.

---

## 📦 현재 패키지 상태

✅ **완료된 작업:**
1. ✅ 기본 패키지 구조 (모듈화)
2. ✅ LICENSE (MIT)
3. ✅ setup.py + pyproject.toml
4. ✅ 버전 관리 시스템
5. ✅ requirements.txt
6. ✅ 테스트 환경 (pytest)
7. ✅ 배포 스크립트
8. ✅ GitHub Actions CI/CD
9. ✅ 상세한 문서

---

## 🚀 3단계로 시작하기

### 1️⃣ 로컬에서 테스트

```bash
# 개발 모드로 설치
pip install -e .

# 테스트 실행
pytest

# 사용 테스트
python -c "import gs_utils; print(gs_utils.__version__)"
```

### 2️⃣ PyPI에 배포 (한 번만 설정)

#### A. PyPI 계정 및 토큰 준비
1. [PyPI](https://pypi.org/) 회원가입
2. Account Settings → API tokens → Add API token
3. Token 복사

#### B. 홈 디렉토리에 `.pypirc` 생성
```bash
# Linux/macOS
nano ~/.pypirc

# Windows
notepad %USERPROFILE%\.pypirc
```

내용:
```ini
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-여기에-토큰-붙여넣기
```

#### C. 배포 도구 설치
```bash
pip install build twine
```

### 3️⃣ 배포 실행

```bash
# 간편 스크립트 사용 (권장)
python scripts/deploy.py

# 또는 수동
python -m build
python -m twine upload dist/*
```

완료! 이제 전 세계 누구나 `pip install gs_utils`로 설치 가능합니다! 🎉

---

## 📋 일상 워크플로우

### 새 기능 개발 후 배포

```bash
# 1. 코드 수정
vim gs_utils/my_module.py

# 2. 버전 업데이트
vim gs_utils/__version__.py  # 예: 0.2.0 → 0.2.1

# 3. 테스트
pytest

# 4. Git 커밋
git add .
git commit -m "feat: Add new feature"
git push

# 5. 배포
python scripts/deploy.py

# 6. Git 태그 (선택사항)
git tag -a v0.2.1 -m "Release 0.2.1"
git push origin v0.2.1
```

### 버전 번호 규칙 (Semantic Versioning)

- `0.2.0 → 0.2.1`: 버그 수정 (PATCH)
- `0.2.0 → 0.3.0`: 새 기능 추가 (MINOR)
- `0.2.0 → 1.0.0`: 호환성 없는 변경 (MAJOR)

---

## 🧪 테스트하기

```bash
# 모든 테스트 실행
pytest

# Coverage 포함
pytest --cov=gs_utils

# 특정 테스트만
pytest tests/test_basic.py

# Verbose 모드
pytest -v
```

---

## 🔄 GitHub Actions 설정 (자동화)

### PyPI 자동 배포 설정

1. GitHub Repository → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. Name: `PYPI_API_TOKEN`, Value: PyPI 토큰
4. 저장

이제 Git 태그를 푸시하면 자동으로 PyPI에 배포됩니다:

```bash
git tag v0.2.1
git push origin v0.2.1
```

---

## 📚 주요 파일 설명

| 파일 | 용도 |
|------|------|
| `setup.py` | 패키지 메타데이터 (레거시 방식) |
| `pyproject.toml` | 최신 패키지 설정 (PEP 518) |
| `gs_utils/__version__.py` | 버전 관리 (단일 진실의 원천) |
| `requirements.txt` | 런타임 의존성 |
| `requirements-dev.txt` | 개발 의존성 |
| `pytest.ini` | 테스트 설정 |
| `MANIFEST.in` | 배포에 포함할 파일 지정 |
| `.gitignore` | Git 무시 파일 |
| `LICENSE` | MIT 라이선스 |
| `DEPLOYMENT.md` | 상세 배포 가이드 |

---

## 🎯 다음 단계

### 즉시 가능
- [ ] 로컬 테스트 (`pip install -e .`)
- [ ] 테스트 실행 (`pytest`)
- [ ] PyPI 배포

### 추천 작업
- [ ] 더 많은 테스트 작성
- [ ] 문서화 개선 (docstrings)
- [ ] GitHub Actions Secret 설정
- [ ] README에 배지 추가

### 고급
- [ ] Codecov 연동
- [ ] Read the Docs 문서 호스팅
- [ ] Pre-commit hooks 설정

---

## 🆘 문제 해결

### 빌드 오류
```bash
rm -rf build dist *.egg-info
pip install --upgrade build twine
python -m build
```

### 테스트 실패
```bash
pip install -e .
pytest -v
```

### 업로드 오류 (버전 중복)
- PyPI는 같은 버전을 재업로드할 수 없습니다
- `gs_utils/__version__.py`에서 버전 증가

---

## 💡 팁

1. **Test PyPI로 먼저 테스트**
   ```bash
   python scripts/deploy.py --test
   ```

2. **로컬 개발 모드 사용**
   ```bash
   pip install -e .
   ```
   코드 수정이 즉시 반영됩니다!

3. **가상환경 사용**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

---

## 📞 추가 도움말

- 상세 배포 가이드: `DEPLOYMENT.md`
- 개발 히스토리: `DEVELOPMENT_HISTORY.md`
- 사용 예제: `README.md`

---

**작성일**: 2025-01-01  
**작성자**: geunsu-son
