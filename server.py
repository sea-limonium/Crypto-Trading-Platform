#### Crypto Investment Platform for Beginners ####
      #### Anastasia Kajalic -- M00982467 ####

from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import socket
import pickle
import requests
import threading
import time

#connect to database
def get_connection():
    return sqlite3.connect('crypto.db')

#fetch cryptocurrency prices
def fetch_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price" #coingecko api, with parameters below
    params = {
        "ids": "bitcoin,ethereum,ripple,tether,solana,binancecoin,dogecoin,cardano,usd-coin,tron",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }

    try:
        #fetching live data
        response = requests.get(url, params=params)
        if response.status_code == 200: #checks for error code
            return response.json()
        elif response.status_code == 429:  #rate limit exceeded
            print("Rate limit exceeded. Retrying in 60 seconds...")
            time.sleep(60)
            return fetch_crypto_prices()  #recursive retry
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return fetch_cached_crypto_prices()  #fallback to cached data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching live data: {e}. Falling back to cached data...")
        return fetch_cached_crypto_prices()  #fallback to cached data

#for cached prices in case of fallback
def fetch_cached_crypto_prices():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        #retrieve cached data from the assets table
        cursor.execute("""
            SELECT name, current_price, price_change, last_updated 
            FROM assets
        """)
        rows = cursor.fetchall()
        cached_data = {
            row[0].lower(): {
                "usd": row[1],
                "usd_24h_change": row[2],
                "last_updated": row[3]
            } for row in rows
        }
        return cached_data
    finally:
        cursor.close()
        conn.close()

#fetch metal prices
def fetch_metal_prices():
    url = "https://metalinvestments.com"
    try:
        #fetch live metal prices from metalinvestments
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        #scraped data from the site
        table_body = soup.select_one("#reftable > div > table > tbody")
        if not table_body:
            raise ValueError("Table body not found. Verify the selector.")

        rows = table_body.find_all("tr")
        if not rows:
            raise ValueError("No rows found in the table.") #check terminal for errors

        #collecting information from specific tables
        metals = []
        for row in rows:
            cols = [td.text.strip() for td in row.find_all("td")]
            if len(cols) >= 4:
                metals.append({
                    "name": cols[0],
                    "price": cols[1],
                    "change": cols[2],
                    "percentage": cols[3]
                })

        return metals
    except Exception as e:
        print(f"Error fetching metal prices: {e}")
        return None

#cache metal prices from db incase of network failure
def fetch_cached_metal_prices():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT name, price, change, percentage
            FROM metals
        """)
        rows = cursor.fetchall()
        return [
            {"name": row[0], "price": row[1], "change": row[2], "percentage": row[3]}
            for row in rows
        ] if rows else None
    finally:
        cursor.close()
        conn.close()

#handle fetching cryptos
def handle_fetch_cryptos():
    live_data = fetch_crypto_prices()
    assets = []

    conn = get_connection()
    cursor = conn.cursor()

    try:
        #fetch last updated from assets
        cursor.execute("SELECT name, last_updated FROM assets")
        last_updated_data = {row[0].lower(): row[1] for row in cursor.fetchall()}

        for coin_id, details in live_data.items():
            price = details.get("usd", 0.0)
            change = details.get("usd_24h_change", 0.0)
            last_updated = last_updated_data.get(coin_id.lower(), "Unknown")  #this is mostly for later use, in GUI, to display updated data

            assets.append({
                "name": coin_id.title(),
                "price": price,
                "change": change,
                "last_updated": last_updated,
            })
    except Exception as e:
        print(f"Error in handle_fetch_cryptos: {e}")
    finally:
        cursor.close()
        conn.close()

    return {"status": "success", "assets": assets}

#fetch live metal prices
def handle_fetch_metals():
    live_data = fetch_metal_prices()
    if live_data:
        update_metals_table(live_data)  #save live data to db
        return {"status": "success", "metals": live_data}

    #fallback to cache data
    cached_data = fetch_cached_metal_prices()
    if cached_data:
        return {"status": "success", "metals": cached_data}

    return {"status": "error", "message": "Unable to fetch live or cached metal prices."}

#update database with %change
def update_assets_table():
    data = fetch_crypto_prices()
    if not data:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        for coin, details in data.items():
            price = details['usd']
            change = details.get('usd_24h_change', 0.0)  #default to 0.0 if not provided. particularly for % in GUI
            cursor.execute("""
                INSERT INTO assets (name, current_price, price_change, last_updated)
                VALUES (?, ?, ?, datetime('now'))
                ON CONFLICT(name) DO UPDATE SET 
                current_price = excluded.current_price,
                price_change = excluded.price_change,
                last_updated = excluded.last_updated
            """, (coin.title(), price, change))
        conn.commit()
        print(f"Assets table updated at {datetime.now()}")
    finally:
        cursor.close()
        conn.close()

#update metals data with new, updated data
def update_metals_table(metals_data):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for metal in metals_data:
            cursor.execute("""
                INSERT INTO metals (name, price, change, percentage)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                price = excluded.price,
                change = excluded.change,
                percentage = excluded.percentage
            """, (metal["name"], metal["price"], metal["change"], metal["percentage"]))
        conn.commit()
        print(f"Metals table updated at {datetime.now()}")
    finally:
        cursor.close()
        conn.close()


#periodic updates with 60s intervals to update the prices
def start_periodic_updates(interval=60):
    while True:
        try:
            print(f"Fetching and updating prices at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
            update_assets_table()
        except Exception as e:
            print(f"Error during periodic update: {e}")
        time.sleep(interval)

#account class
class Account:
    def __init__(self, username, password=None, balance=0.0):
        self.username = username
        self.password = password
        self.balance = balance

    def load_from_db(self):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT username, balance FROM accounts WHERE username = ?", (self.username,))
            account = cursor.fetchone()
            if account:
                self.username, self.balance = account[0], account[1]
                return self
            else:
                raise ValueError("Account not found")
        finally:
            cursor.close()
            conn.close()

    #deposit funds
    def deposit(self, amount):
        self.balance += amount
        self.update_balance_in_db()

    #withdraw funds
    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.update_balance_in_db()
        else:
            raise ValueError("Insufficient balance")

    #update balance in database
    def update_balance_in_db(self):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE accounts SET balance = ? WHERE username = ?", (self.balance, self.username))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

#portfolio class
class Portfolio:
    def __init__(self, username):
        self.username = username
        self.assets = self.load_assets()

    #loda user holdings in portfolio
    def load_assets(self):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT asset_name, quantity FROM portfolio WHERE username = ?", (self.username,))
            return {row[0]: row[1] for row in cursor.fetchall()}
        finally:
            cursor.close()
            conn.close()

    #add/update crypto holdings in portfolio
    def add_asset(self, asset_name, quantity):
        if asset_name in self.assets:
            self.assets[asset_name] += quantity
        else:
            self.assets[asset_name] = quantity
        self.update_portfolio_in_db(asset_name, self.assets[asset_name])

    #update portfolio in database
    def update_portfolio_in_db(self, asset_name, quantity):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            if quantity > 0:
                cursor.execute("""
                    INSERT INTO portfolio (username, asset_name, quantity)
                    VALUES (?, ?, ?)
                    ON CONFLICT(username, asset_name) DO UPDATE SET quantity = ?
                """, (self.username, asset_name, quantity, quantity))
            else:
                cursor.execute("DELETE FROM portfolio WHERE username = ? AND asset_name = ?", (self.username, asset_name))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    #return all user holdings
    def view_holdings(self):
        return self.assets

    #return only crypto holdings
    def view_crypto_holdings(self):
        crypto_list = self.get_crypto_list()
        return {asset: qty for asset, qty in self.assets.items() if asset.lower() in crypto_list}

    #return only metal holdings
    def view_metal_holdings(self):
        metal_list = self.get_metal_list()
        return {asset: qty for asset, qty in self.assets.items() if asset.lower() in metal_list}

    #fetch crypto list from database
    #could be static
    def get_crypto_list(self):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM assets")
            return {row[0].lower() for row in cursor.fetchall()}
        finally:
            cursor.close()
            conn.close()

    #fetch metal list from database
    def get_metal_list(self):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM metals")
            return {row[0].lower() for row in cursor.fetchall()}
        finally:
            cursor.close()
            conn.close()

#for logging in, validating username and password
def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password, balance FROM accounts WHERE username = ?", (username,))
        account = cursor.fetchone()
        if account:
            stored_password, balance = account
            if stored_password == password:
                return {"status": "success", "balance": balance}
            else:
                return {"status": "error", "message": "Incorrect password."}
        else:
            return {"status": "error", "message": "Username not found."}
    finally:
        cursor.close()
        conn.close()

#to log transactions
def save_transaction(username, asset_name, quantity, action):
    print(f"Saving transaction: {username}, {asset_name}, {quantity}, {action}")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        #fetching current price
        cursor.execute("""
            SELECT current_price FROM assets WHERE name = ?
            UNION SELECT price FROM metals WHERE name = ?
        """, (asset_name, asset_name))
        price = cursor.fetchone()
        if not price:
            raise ValueError("Asset does not exist in the database.. what?")

        #converting price to float to avoid errors
        price = price[0]
        if isinstance(price, str):
            price = float(price.replace(",", ""))  #handle commas in string prices

        total = price * quantity

        #add transaction into db
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO transactions (username, asset_name, quantity, action, total, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, asset_name, quantity, action, total, timestamp))
        conn.commit()
        print(f"Transaction saved: {username} {action} {quantity} {asset_name} for ${total:.2f}")
    finally:
        cursor.close()
        conn.close()

#for user to create an account
def create_account(username, password, initial_deposit):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        #check to see if user exists
        cursor.execute("SELECT username FROM accounts WHERE username = ?", (username,))
        if cursor.fetchone():
            raise ValueError("Sorry! Username already exists!\nPlease choose a different username :(")

        #insert the new account into accounts table
        cursor.execute("""
            INSERT INTO accounts (username, password, balance)
            VALUES (?, ?, ?)
        """, (username, password, initial_deposit))
        conn.commit()
        print(f"Account created successfully for {username}. Initial balance: ${initial_deposit:.2f}")
    finally:
        cursor.close()
        conn.close()

#trading functionality (ie. buy/sell)
def process_trade(username, asset_name, quantity, action, is_metal=False):
    print(f"Processing trade: {action} {quantity} of {asset_name} by {username}")
    account = Account(username).load_from_db()
    portfolio = Portfolio(username)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        #check to see if it's the correct table n column
        table = "metals" if is_metal else "assets"
        column = "price" if is_metal else "current_price"

        #fetching the current price of crypto/metal
        cursor.execute(f"SELECT {column} FROM {table} WHERE name = ?", (asset_name,))
        asset_price = cursor.fetchone()
        if not asset_price:
            return {"status": "error", "message": f"{asset_name} does not exist in {table}"}

        #ensure asset_price is a float and handle commas in the string (causes errors in metal db without!)
        try:
            asset_price = float(str(asset_price[0]).replace(",", ""))  #line to remove commas and convert to float
        except ValueError:
            return {"status": "error", "message": f"Invalid price format for {asset_name} in {table}"}

        total_cost = asset_price * quantity

        if action == "buy":
            #check if user has sufficient balance
            if account.balance >= total_cost:
                account.withdraw(total_cost)
                portfolio.add_asset(asset_name, quantity)
                save_transaction(username, asset_name, quantity, action)
                return {"status": "success", "balance": account.balance, "portfolio": portfolio.view_holdings()}
            else:
                return {"status": "error", "message": "Insufficient balance."}
        elif action == "sell":
            #check if user has enough holdings to sell
            holdings = portfolio.view_holdings()
            if holdings.get(asset_name, 0) >= quantity:
                portfolio.add_asset(asset_name, -quantity)
                account.deposit(total_cost)
                save_transaction(username, asset_name, quantity, action)
                return {"status": "success", "balance": account.balance, "portfolio": portfolio.view_holdings()}
            else:
                return {"status": "error", "message": "You don't have enough to sell!"}
        else:
            return {"status": "error", "message": f"Invalid action: {action}"}
    except Exception as e:
        print(f"Unexpected error processing trade: {e}")
        return {"status": "error", "message": "Uh oh -- something unexpected happened!"}
    finally:
        cursor.close()
        conn.close()


#commands to send to the client
def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                print("Client disconnected.")
                break
            request = pickle.loads(data)
            print(f"Received request: {request}")

            command = request.get("command")
            username = request.get("username")
            response = {}

            #login command
            if command == "LOGIN":
                password = request.get("password")
                response = login_user(username, password)

            #create account command
            elif command == "CREATE_ACCOUNT":
                password = request.get("password")
                initial_deposit = request.get("initial_deposit", 0.0)
                try:
                    create_account(username, password, initial_deposit)
                    response = {"status": "success", "message": f"Account created for {username}!"}
                except ValueError as e:
                    response = {"status": "error", "message": str(e)}

            #fetch cryptos
            elif command == "FETCH_CRYPTOS":
                try:
                    response = handle_fetch_cryptos()
                except Exception as e:
                    response = {"status": "error", "message": str(e)}

            #fetch metal investments
            elif command == "FETCH_METALS":
                response = handle_fetch_metals()

            #load account and retrieve balance
            elif command == "GET_BALANCE":
                try:
                    account = Account(username).load_from_db()
                    response = {"status": "success", "balance": account.balance}
                except ValueError as e:
                    response = {"status": "error", "message": str(e)}

            #deposit
            elif command == "DEPOSIT":
                amount = request.get("amount", 0.0)
                try:
                    account = Account(username).load_from_db()
                    account.deposit(amount)
                    response = {"status": "success", "message": f"Deposited ${amount:.2f}"}
                except ValueError as e:
                    response = {"status": "error", "message": str(e)}

            #withdraw
            elif command == "WITHDRAW":
                amount = request.get("amount", 0.0)
                try:
                    account = Account(username).load_from_db()
                    account.withdraw(amount)
                    response = {"status": "success", "message": f"Withdrew ${amount:.2f}"}
                except ValueError as e:
                    response = {"status": "error", "message": str(e)}

            #buy crypto
            elif command == "BUY":
                username = request.get("username")
                asset_name = request.get("asset_name")
                quantity = request.get("quantity", 0.0)
                print(f"Processing BUY command for {username}: {quantity} of {asset_name}")

                result = process_trade(username, asset_name, quantity, "buy")
                response = result

            #sell crypto
            elif command == "SELL":
                username = request.get("username")
                asset_name = request.get("asset_name")
                quantity = request.get("quantity", 0.0)
                print(f"Processing SELL command for {username}: {quantity} of {asset_name}")

                result = process_trade(username, asset_name, quantity, "sell")
                response = result

            #buy metal
            elif command == "BUY_METAL":
                username = request.get("username")
                metal_name = request.get("metal_name")
                quantity = request.get("quantity", 0.0)
                print(f"Processing BUY_METAL command for {username}: {quantity} of {metal_name}")
                response = process_trade(username, metal_name, quantity, "buy", is_metal=True)

            #sell metal
            elif command == "SELL_METAL":
                username = request.get("username")
                metal_name = request.get("metal_name")
                quantity = request.get("quantity", 0.0)
                print(f"Processing SELL_METAL command for {username}: {quantity} of {metal_name}")
                response = process_trade(username, metal_name, quantity, "sell", is_metal=True)

            #transaction history
            elif command == "GET_TRANSACTIONS":
                try:
                    conn = get_connection()
                    cursor = conn.cursor()

                    #fetch transactions
                    cursor.execute("""
                        SELECT asset_name, quantity, action, total, timestamp
                        FROM transactions
                        WHERE username = ?
                        ORDER BY timestamp DESC
                    """, (username,))
                    transactions = cursor.fetchall()

                    response = {"status": "success", "transactions": transactions}
                except Exception as e:
                    response = {"status": "error", "message": str(e)}
                finally:
                    cursor.close()
                    conn.close()


            #portfolio command
            elif command == "GET_PORTFOLIO":
                try:
                    portfolio = Portfolio(username)
                    crypto_holdings = portfolio.view_crypto_holdings()
                    metal_holdings = portfolio.view_metal_holdings()
                    response = {
                        "status": "success",
                        "crypto_holdings": crypto_holdings,
                        "metal_holdings": metal_holdings
                    }
                except Exception as e:
                    response = {"status": "error", "message": str(e)}

            client_socket.send(pickle.dumps(response))

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

server_running = True

def main():
    global server_running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(5)
    print("Listening!")

    #start periodic updates in a separate thread
    update_thread = threading.Thread(target=start_periodic_updates, daemon=True)
    update_thread.start()

    try:
        while server_running:
            server_socket.settimeout(1)  #non-blocking accept with timeout (return 0 please)
            try:
                client_socket, addr = server_socket.accept()
                print(f"Connection established with {addr}")
                threading.Thread(target=handle_client, args=(client_socket,)).start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nshutting down server gracefully so i dont get an exit code -1...")
        server_running = False
    finally:
        server_socket.close()
        print("server socket is closed!! we celebrate for an EXIT CODE 0 YEAAAAH!")

if __name__ == "__main__":
    main()
