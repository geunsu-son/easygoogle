# 🚀 gs_utils 배포 가이드

이 문서는 `gs_utils` 패키지를 PyPI에 배포하는 방법을 설명합니다.

---

## 📋 사전 준비

### 1. PyPI 계정 생성
- [PyPI](https://pypi.org/)에서 계정 생성
- [Test PyPI](https://test.pypi.org/)에서도 테스트 계정 생성 (선택사항)

### 2. API Token 생성
1. PyPI 로그인
2. Account Settings → API tokens
3. "Add API token" 클릭
4. Scope: "Entire account" 선택
5. Token 복사 및 안전하게 보관

### 3. `.pypirc` 파일 생성
홈 디렉토리에 `.pypirc` 파일 생성:

```bash
# Linux/macOS
nano ~/.pypirc

# Windows
notepad %USERPROFILE%\.pypirc
```

내용:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

**보안 주의**: `.pypirc` 파일은 절대 Git에 커밋하지 마세요!

---

## 🔧 배포 준비

### 1. 개발 의존성 설치
```bash
pip install -r requirements-dev.txt
```

또는 개별 설치:
```bash
pip install build twine pytest pytest-cov
```

### 2. 테스트 실행
```bash
# 모든 테스트 실행
pytest

# Coverage 리포트 포함
pytest --cov=gs_utils --cov-report=html
```

### 3. 버전 확인 및 업데이트
`gs_utils/__version__.py` 파일에서 버전 확인:
```python
__version__ = '0.2.0'
```

**버전 관리 규칙 (Semantic Versioning):**
- **MAJOR.MINOR.PATCH** (예: 1.2.3)
- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 하위 호환성 있는 기능 추가
- **PATCH**: 하위 호환성 있는 버그 수정

---

## 📦 빌드 및 배포

### 방법 1: 간편 스크립트 사용 (권장)

#### Test PyPI에 배포 (테스트용)
```bash
python scripts/deploy.py --test
```

#### 실제 PyPI에 배포
```bash
python scripts/deploy.py
```

### 방법 2: 수동 배포

#### 1단계: 빌드
```bash
# 기존 빌드 파일 정리
rm -rf build/ dist/ *.egg-info

# 패키지 빌드
python -m build
```

빌드 후 `dist/` 폴더에 다음 파일들이 생성됩니다:
- `gs_utils-0.2.0.tar.gz` (소스 배포)
- `gs_utils-0.2.0-py3-none-any.whl` (휠 배포)

#### 2단계: Test PyPI에 업로드 (선택사항)
```bash
python -m twine upload --repository testpypi dist/*
```

테스트 설치:
```bash
pip install --index-url https://test.pypi.org/simple/ gs_utils
```

#### 3단계: PyPI에 업로드
```bash
python -m twine upload dist/*
```

#### 4단계: 설치 확인
```bash
# 새 가상환경 생성
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# 설치
pip install gs_utils

# 테스트
python -c "import gs_utils; print(gs_utils.__version__)"
```

---

## 🔄 배포 체크리스트

배포 전 확인사항:

- [ ] 모든 테스트 통과 (`pytest`)
- [ ] 버전 번호 업데이트 (`gs_utils/__version__.py`)
- [ ] `README.md` 업데이트 (새로운 기능 문서화)
- [ ] `DEVELOPMENT_HISTORY.md` 업데이트
- [ ] Git 커밋 및 푸시
- [ ] Git 태그 생성 (`git tag v0.2.0`)
- [ ] Git 태그 푸시 (`git push origin v0.2.0`)
- [ ] 빌드 파일 정리
- [ ] Test PyPI에 업로드 및 테스트 (선택사항)
- [ ] PyPI에 업로드
- [ ] 설치 확인

---

## 🏷️ Git 태그 관리

### 태그 생성
```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### 태그 목록 확인
```bash
git tag
```

### 태그 삭제 (필요시)
```bash
# 로컬 태그 삭제
git tag -d v0.2.0

# 원격 태그 삭제
git push origin :refs/tags/v0.2.0
```

---

## 🔧 문제 해결

### 1. 빌드 오류
```bash
# 캐시 정리
pip cache purge

# 의존성 재설치
pip install -r requirements-dev.txt --force-reinstall
```

### 2. 업로드 오류 (이미 존재하는 버전)
- PyPI는 동일한 버전을 재업로드할 수 없습니다
- 버전 번호를 증가시켜야 합니다
- Test PyPI를 사용하여 먼저 테스트하세요

### 3. 인증 오류
- `.pypirc` 파일의 토큰이 정확한지 확인
- 토큰 앞에 `pypi-` 접두사가 있는지 확인
- 토큰이 만료되지 않았는지 확인

---

## 📚 참고 자료

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Documentation](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)
- [Twine Documentation](https://twine.readthedocs.io/)

---

## 🎯 자동화 (CI/CD)

GitHub Actions를 통한 자동 배포는 `.github/workflows/publish.yml` 파일을 참고하세요.

**자동 배포 트리거:**
- Git 태그 푸시 시 자동으로 PyPI에 배포
- 예: `git tag v0.2.0 && git push origin v0.2.0`

---

**마지막 업데이트**: 2025-01-01  
**작성자**: geunsu-son
