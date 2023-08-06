import setuptools

with open("README.md", "r") as fh:
    desc = fh.read()
    
setuptools.setup(
    name="kspam_filtering", # Replace with your own username
    version="0.0.8",
    author="UgwayK",
    author_email="nuang0530@naver.com",
    description="ㅅr과티비 같은 변형성 광고문구를 찾기 위해 만든 프로젝트 입니다",
    long_description=desc,
    long_description_content_type="text/markdown",
    url="https://blog.naver.com/nuang0530",
    packages=setuptools.find_packages(),
    python_requires='>=3.6'
)

# 버전 관리
# 0.0.1 : 모듈 2개 완성
# 0.0.2 - 0.0.3 : 버그 픽스