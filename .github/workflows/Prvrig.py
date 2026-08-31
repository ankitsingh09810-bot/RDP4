name: Run Insta Bot

on:
  workflow_dispatch:

jobs:
  build:
  runs-on: ubuntu-latest

  steps:
  - name: Checkout Repository
    uses: actions/checkout@v4

  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: '3.10'

  - name: Install Dependencies
    run: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt

  - name: Run Bot
    env:
      BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
      ADMIN_ID: ${{ secrets.ADMIN_ID }}
    run: |
      python prvrig.py
      
