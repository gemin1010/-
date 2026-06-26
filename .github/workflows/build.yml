name: Build EXE
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install pyinstaller
      - run: pyinstaller --onefile --noconsole launcher.py
      - uses: actions/upload-artifact@v4
        with:
          name: 자리뽑기
          path: dist/launcher.exe
