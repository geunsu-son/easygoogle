#!/usr/bin/env python
"""
EasyGoogle 패키지 배포 스크립트

사용법:
    python scripts/deploy.py          # PyPI에 배포
    python scripts/deploy.py --test   # Test PyPI에 배포
"""
import os
import sys
import shutil
import subprocess
import argparse


def run_command(cmd, check=True):
    """명령어 실행"""
    print(f"\n🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0


def clean_build():
    """빌드 디렉토리 정리"""
    print("\n🧹 Cleaning build directories...")
    dirs_to_remove = ['build', 'dist', 'easygoogle.egg-info', 'gs_utils.egg-info']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  ✓ Removed {dir_name}/")


def run_tests():
    """테스트 실행"""
    print("\n🧪 Running tests...")
    if not run_command("pytest", check=False):
        print("\n❌ Tests failed!")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("  ✓ All tests passed!")


def build_package():
    """패키지 빌드"""
    print("\n📦 Building package...")
    if not run_command("python -m build"):
        print("\n❌ Build failed!")
        sys.exit(1)
    print("  ✓ Build completed!")


def upload_package(repository='pypi'):
    """패키지 업로드"""
    repo_name = "Test PyPI" if repository == 'testpypi' else "PyPI"
    print(f"\n🚀 Uploading to {repo_name}...")
    
    cmd = "python -m twine upload"
    if repository == 'testpypi':
        cmd += " --repository testpypi"
    cmd += " dist/*"
    
    if not run_command(cmd):
        print(f"\n❌ Upload to {repo_name} failed!")
        sys.exit(1)
    print(f"  ✓ Successfully uploaded to {repo_name}!")


def get_version():
    """버전 가져오기"""
    version_file = os.path.join('easygoogle', '__version__.py')
    version = {}
    with open(version_file) as f:
        exec(f.read(), version)
    return version['__version__']


def main():
    parser = argparse.ArgumentParser(description='Deploy easygoogle package')
    parser.add_argument('--test', action='store_true', help='Deploy to Test PyPI')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    parser.add_argument('--skip-clean', action='store_true', help='Skip cleaning build directories')
    args = parser.parse_args()
    
    version = get_version()
    repository = 'testpypi' if args.test else 'pypi'
    repo_name = "Test PyPI" if args.test else "PyPI"
    
    print("=" * 60)
    print(f"📦 EasyGoogle Deployment Script")
    print(f"Version: {version}")
    print(f"Target: {repo_name}")
    print("=" * 60)
    
    # 확인
    response = input(f"\nDeploy version {version} to {repo_name}? (y/N): ")
    if response.lower() != 'y':
        print("Deployment cancelled.")
        sys.exit(0)
    
    # 빌드 디렉토리 정리
    if not args.skip_clean:
        clean_build()
    
    # 테스트 실행
    if not args.skip_tests:
        run_tests()
    
    # 빌드
    build_package()
    
    # 업로드
    upload_package(repository)
    
    print("\n" + "=" * 60)
    print("✅ Deployment completed successfully!")
    print("=" * 60)
    
    # 설치 안내
    if repository == 'testpypi':
        print("\n📥 To install from Test PyPI:")
        print("  pip install --index-url https://test.pypi.org/simple/ easygoogle")
    else:
        print("\n📥 To install:")
        print("  pip install easygoogle")
        print("\n🏷️  Don't forget to create a git tag:")
        print(f"  git tag -a v{version} -m 'Release version {version}'")
        print(f"  git push origin v{version}")


if __name__ == '__main__':
    main()
