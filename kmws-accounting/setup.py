from distutils.core import setup

setup(
    name="kmws-accounting",
    version="0.0",
    author="Mizuochi Keita",
    author_email="keitam913@yahoo.co.jp",
    packages=[
        "kmws_accounting",
        "kmws_accounting.application",
        "kmws_accounting.adapters",
    ],
    package_data={
        "kmws_accounting": [
            "py.typed",
        ],
        "kmws_accounting.adapters": [
            "schema.graphql",
        ],
    },
    install_requires=[
        "ariadne==0.16.0",
        "uvicorn==0.18.3",
    ],
)
