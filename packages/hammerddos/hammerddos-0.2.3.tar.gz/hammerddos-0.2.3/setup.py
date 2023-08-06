from distutils.core import setup

setup(
    name="hammerddos",
    py_modules=["ddos1"],
    entry_points={"console_scripts": ["slowloris=slowloris:main"]},
    version="0.2.3",
    description="Low bandwidth DoS tool. Slowloris rewrite in Python.",
    author="Nahid Alam",
    author_email="nahidalam1603@gmail.com",
    url="https://github.com/gkbrk/slowloris",
    keywords=["dos", "http", "hammer"],
    license="MIT",
)
