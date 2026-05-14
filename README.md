## Crypto Trading Platform

A simulated cryptocurrency and precious metals trading platform built with Python. Features a client-server architecture with socket communication, a modern GUI built with CustomTkinter, real-time price scraping, and persistent data storage with SQLite.

### Features

- **Account Management** - Create an account, log in, deposit and withdraw funds.
- **Live Market Data** - Real-time cryptocurrency prices scraped from CoinGecko and metal prices from Metal Investments, with cached fallback data if fetching fails.
- **Trading** - Buy and sell cryptocurrencies (Bitcoin, Ethereum, etc.) and precious metals (Gold, Silver) based on live prices.
- **Portfolio Tracking** - View current holdings with quantities and total values.
- **Transaction History** - Timestamped log of all buys and sells.
- **Data Visualisation** - Matplotlib-generated price trend graphs displayed within the GUI.
- **Graceful Shutdown** - Server exits cleanly on `KeyboardInterrupt`.

### Tech Stack

- **Language:** Python 3.x
- **GUI:** Tkinter + CustomTkinter
- **Database:** SQLite3
- **Networking:** Socket programming (client-server)
- **Web Scraping:** BeautifulSoup + Requests
- **Visualisation:** Matplotlib
- **Concurrency:** Threading (periodic price updates every 60s)

### Project Structure

```
Crypto_Trading_Platform/
├── server.py          # Backend — handles auth, trades, DB, and price fetching
├── client.py          # Frontend — GUI, user interaction, sends requests to server
└── crypto.db          # SQLite database (accounts, portfolio, transactions, assets, metals)
```

### Installation & Setup

1. Clone the repository or download and unzip the project folder.

```bash
git clone https://github.com/sea-limonium/crypto-trading-platform.git
cd crypto-trading-platform
```

2. Install the required dependencies.

```bash
pip install customtkinter matplotlib beautifulsoup4 requests
```

> `tkinter`, `sqlite3`, `socket`, `pickle`, `threading`, `datetime`, and `random` are part of Python's standard library and don't need to be installed separately.

3. Start the server first (keep this terminal open).

```bash
python server.py
```

You should see the server listening for connections.

4. In a **separate terminal**, launch the client.

```bash
python client.py
```

The GUI login window will appear. Create an account or log in to start trading.

### Stopping the Application

- **Client:** Simply close the GUI window.
- **Server:** Press `Ctrl + C` in the server terminal. The graceful shutdown handler will close the socket cleanly (exit code 0).

---

Built as a solo coursework project for CST1510 — Programming for Data Communications and Networks at Middlesex University (Autumn 2024).
