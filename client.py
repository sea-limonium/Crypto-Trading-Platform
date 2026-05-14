#### Crypto Investment Platform for Beginners ####
      #### Anastasia Kajalic -- M00982467 ####

import customtkinter as ctk
from tkinter import messagebox
import socket
import pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

#customtkinter themes
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

#global variables, used later when destroying widgets
sidebar = None
main_frame = None

#connect to the server
def connect_to_server():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 5000))
        return client_socket
    except Exception as e:
        show_error_box(root,"Error", f"Unable to connect to server: {e} :(")
        return None

#checking to see if the server is connected
def send_request(client_socket, request):
    try:
        client_socket.send(pickle.dumps(request))
        data = client_socket.recv(4096)
        if not data:  #debug
            raise ValueError("No response received from the server.")
        response = pickle.loads(data)
        return response
    except Exception as e:
        print(f"Error during request: {e}")
        return {"status": "error", "message": str(e)}


#clear and load new pages
def show_page(page_function):
    for widget in main_frame.winfo_children():
        widget.destroy()
    page_function()

#crypto_updates functionality
def fetch_crypto_prices():
    #fetch live prices
    client_socket = connect_to_server()
    if not client_socket:
        return {}
    try:
        request = {"command": "FETCH_CRYPTOS"}
        response = send_request(client_socket, request)
        client_socket.close()
        print("Server response:", response)  #debug
        if response and response.get("status") == "success":
            #convert list of crypto into dictionary
            return {item["name"].lower(): item["price"] for item in response.get("assets", [])}
        else:
            return {}
    except Exception as e:
        print(f"Error fetching crypto prices: {e}")
        return {}

#fetch metal prices from server
def fetch_metal_prices():
    client_socket = connect_to_server()
    if not client_socket:
        return {}
    try:
        request = {"command": "FETCH_METALS"}
        response = send_request(client_socket, request)
        client_socket.close()
        print("Server response (metals):", response)  # Debug
        if response and response.get("status") == "success":
            #convert list of metals into dictionary
            return {item["name"].lower(): float(item["price"].replace(",", "")) for item in response.get("metals", [])}
        else:
            return {}
    except Exception as e:
        print(f"Error fetching metal prices: {e}")
        return {}

#custom window for buying and selling
class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Sale", prompt="Enter a value:", callback=None):
        super().__init__(parent)

        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.callback = callback  #handle result

        #prompt
        self.label = ctk.CTkLabel(
            self, text=prompt, font=("Poppins", 14), text_color="#D3D3D3"
        )
        self.label.pack(pady=(20, 10))

        #enter amount text
        self.entry = ctk.CTkEntry(
            self, placeholder_text="Enter amount"
        )
        self.entry.pack(pady=(0, 20), padx=20, fill="x")

        #buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(0, 10))
        button_width = 100

        ctk.CTkButton(
            button_frame,
            text="OK",
            command=self.on_ok,
            fg_color="#00D1B2",
            hover_color="#00A596",
            text_color="black",
            width=button_width
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            fg_color="#00D1B2",
            hover_color="#00A596",
            text_color="black",
            width=button_width
        ).pack(side="right", padx=10)

    def on_ok(self):
        if self.callback:
            self.callback(self.entry.get())
        self.destroy()

    def on_cancel(self):
        self.destroy()

#custom no-input info box
#for success
def show_info_box(parent, title="Info", message=""):
    info_window = ctk.CTkToplevel(parent)
    info_window.title(title)
    info_window.configure(fg_color="#1A1A1A")

    width = 350
    height = 175
    info_window.geometry(f"{width}x{height}")

    #prevent parent window from being active
    info_window.grab_set()

    #title
    ctk.CTkLabel(
        info_window,
        text=title,
        font=("Poppins", 20, "bold"),
        text_color="#00D1B2"
    ).pack(pady=(20, 10))

    #message
    ctk.CTkLabel(
        info_window,
        text=message,
        font=("Poppins", 14),
        text_color="#D3D3D3",
        wraplength=width - 50,
        justify="center"
    ).pack(pady=(0, 20))

    #button
    ctk.CTkButton(
        info_window,
        text="OK",
        command=info_window.destroy,
        fg_color="#00D1B2",
        text_color="black",
        hover_color="#00A596",
        width=100
    ).pack(pady=10)

    #center window to users resolution
    x = (info_window.winfo_screenwidth() // 2) - (width // 2)
    y = (info_window.winfo_screenheight() // 2) - (height // 2)
    info_window.geometry(f"{width}x{height}+{x}+{y}")

#for error
def show_error_box(parent, title="Error", message=""):
    error_window = ctk.CTkToplevel(parent)
    error_window.title(title)
    error_window.configure(fg_color="#1A1A1A")

    width = 350
    height = 175
    error_window.geometry(f"{width}x{height}")

    #prevent parent window from being active
    error_window.grab_set()

    #title
    ctk.CTkLabel(
        error_window,
        text=title,
        font=("Poppins", 20, "bold"),
        text_color="#FF4B4B"  # Red for error
    ).pack(pady=(20, 10))

    #message
    ctk.CTkLabel(
        error_window,
        text=message,
        font=("Poppins", 14),
        text_color="#D3D3D3",
        wraplength=width - 50,
        justify="center"
    ).pack(pady=(0, 20))

    #button
    ctk.CTkButton(
        error_window,
        text="OK",
        command=error_window.destroy,
        fg_color="#FF4B4B",
        text_color="white",
        hover_color="#FF6666",
        width=100
    ).pack(pady=10)

    #center window based on user resolution
    x = (error_window.winfo_screenwidth() // 2) - (width // 2)
    y = (error_window.winfo_screenheight() // 2) - (height // 2)
    error_window.geometry(f"{width}x{height}+{x}+{y}")

#generate graph
def plot_graph(prices, line_color="#00D1B2", gradient_color="#007F73"):
    fig, ax = plt.subplots(figsize=(3.5, 2), dpi=100)
    fig.patch.set_alpha(0)
    ax.set_facecolor((0, 0, 0, 0))

    #main line
    ax.plot(prices, color=line_color, linewidth=1.5, zorder=3)  # Updated with dynamic color

    #gradient
    ax.fill_between(range(len(prices)), prices, color=gradient_color, alpha=0.2, zorder=2)  # Updated with dynamic color

    #grid
    min_price, max_price = int(min(prices)), int(max(prices)) + 1
    for y in range(min_price, max_price, max(1, (max_price - min_price) // 5)):
        ax.axhline(y=y, color="gray", linestyle="--", linewidth=0.6, alpha=0.6, zorder=1)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")

    return fig

#fetche live data
#update the crypto dashboard
def update_crypto_cards(crypto_frame):
    crypto_data = fetch_crypto_prices()
    print(crypto_data)

    #clear previous cards
    for widget in crypto_frame.winfo_children():
        widget.destroy()

    row, column = 0, 0
    for name, details in crypto_data.items():
        price = details.get("price", 0.0)
        change = details.get("change", 0.0)
        last_updated = details.get("last_updated", "Unknown")
        prices = details.get("history", [price + random.uniform(-2, 2) for _ in range(10)])

        #auto cards
        card = ctk.CTkFrame(crypto_frame, fg_color="#222222", corner_radius=10, width=240, height=290)
        card.grid(row=row, column=column, padx=12, pady=15, sticky="nsew")

        #card content
        ctk.CTkLabel(
            card, text=name, font=("Poppins", 22, "bold"), text_color="#D3D3D3"
        ).grid(row=0, column=0, padx=(15, 0), pady=5, sticky="w")

        ctk.CTkLabel(
            card, text=f"Price: ${price:,.2f}", font=("Poppins", 12), text_color="#A9A9A9"
        ).grid(row=1, column=0, pady=5, padx=(15, 15), columnspan=2, sticky="n")

        ctk.CTkLabel(
            card, text=f"{change:+.2f}%", font=("Poppins", 19, "bold"),
            text_color="#00D1B2" if change > 0 else "#FF4B4B" #auto updates teal for positive %, red for negative % change
        ).grid(row=0, column=1, padx=(0, 15), pady=5, sticky="ne")

        #graph
        fig = plot_graph(prices, line_color="#00D1B2", gradient_color="#007F73")
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        canvas_widget.config(bg="#222222", highlightthickness=0)
        plt.close(fig)

        #buy/sell buttons
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            button_frame, text="Buy", width=100, fg_color="#00D1B2",
            hover_color="#00A596", text_color="black",
            command=lambda name=name: buy_asset(name)
        ).grid(row=0, column=0, padx=5, sticky="e")

        ctk.CTkButton(
            button_frame, text="Sell", width=100, fg_color="#00D1B2",
            hover_color="#00A596", text_color="black",
            command=lambda name=name: sell_asset(name)
        ).grid(row=0, column=1, padx=5, sticky="w")

        #last updated timestamp
        ctk.CTkLabel(
            card, text=f"Last Updated: {last_updated}", font=("Poppins", 10),
            text_color="#A9A9A9"
        ).grid(row=5, column=0, columnspan=2, pady=(5, 0), padx=10, sticky="s")

        #auto grid cards
        column += 1
        if column > 3:  #max of 4 cards per row
            column = 0
            row += 1

    #refresh page every 30 seconds
    crypto_frame.after(30000, update_crypto_cards, crypto_frame)


#update metal cards dynamically
def update_metal_cards(metal_frame):
    metal_data = fetch_metal_prices()

    #clear previous cards
    for widget in metal_frame.winfo_children():
        widget.destroy()

    row, column = 0, 0
    for name, details in metal_data.items():
        #extract values from db
        current_price = float(details.get("price", "0").replace(",", ""))
        price_change = float(details.get("change", "0").replace(",", ""))
        percentage_change = float(details.get("percentage", "0").replace(",", ""))

        #mock price for graph
        prices = [current_price - (i * price_change / 10) for i in range(10)]

        #card
        card = ctk.CTkFrame(metal_frame, fg_color="#222222", corner_radius=10, width=240, height=350)
        card.grid(row=row, column=column, padx=12, pady=15, sticky="nsew")

        #card content
        ctk.CTkLabel(
            card, text=name, font=("Poppins", 22, "bold"), text_color="#D3D3D3"
        ).grid(row=0, column=0, padx=(15, 0), pady=5, sticky="w")

        ctk.CTkLabel(
            card, text=f"Price: ${current_price:,.2f}", font=("Poppins", 12), text_color="#A9A9A9"
        ).grid(row=1, column=0, pady=(5, 0), padx=(15, 15), columnspan=2, sticky="n")

        ctk.CTkLabel(
            card, text=f"Change: {price_change:+,.2f}", font=("Poppins", 12), text_color="#A9A9A9"
        ).grid(row=2, column=0, pady=(0, 5), padx=(15, 15), columnspan=2, sticky="n")

        ctk.CTkLabel(
            card,
            text=f"{percentage_change:+.2f}%",
            font=("Poppins", 19, "bold"),
            text_color="#00D1B2" if percentage_change > 0 else "#FF4B4B"
        ).grid(row=0, column=1, padx=(0, 15), pady=5, sticky="ne")

        #graph
        fig = plot_graph(prices, line_color="#00D1B2", gradient_color="#007F73")
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        canvas_widget.config(bg="#222222", highlightthickness=0)
        plt.close(fig)

        #buy/sell buttons
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            button_frame, text="Buy", width=100, fg_color="#00D1B2",
            hover_color="#00A596", text_color="black",
            command=lambda name=name: buy_metal(name)
        ).grid(row=0, column=0, padx=5, sticky="e")

        ctk.CTkButton(
            button_frame, text="Sell", width=100, fg_color="#00D1B2",
            hover_color="#00A596", text_color="black",
            command=lambda name=name: sell_metal(name)
        ).grid(row=0, column=1, padx=5, sticky="w")

        #auto grid cards
        column += 1
        if column > 3:  #max 4 cards per row
            column = 0
            row += 1

    #refresh page every 30 seconds
    metal_frame.after(30000, update_metal_cards, metal_frame)

#buy crypto
def buy_asset(asset_name):
    def handle_buy_input(quantity):
        try:
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            client_socket = connect_to_server()
            if not client_socket:
                return

            #buy request
            request = {"command": "BUY", "username": current_user, "asset_name": asset_name, "quantity": quantity}
            response = send_request(client_socket, request)
            client_socket.close()

            #server response
            if response and response.get("status") == "success":
                show_info_box(root, "Purchase complete!", f"Purchased {quantity} of {asset_name}.")
            else:
                show_error_box(root, "Purchase error!", message=response.get("message"))

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    #modern window popup for buying, called back to the custom window made
    dialog = CustomInputDialog(root, title="Purchase!", prompt=f"Enter amount of {asset_name} to buy:",
                               callback=handle_buy_input)
    dialog.grab_set()

#sell crypto
def sell_asset(asset_name):
    def handle_sell_input(quantity):
        try:
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError("Amount must be greater than zero.")

            client_socket = connect_to_server()
            if not client_socket:
                return

            #sell request
            request = {"command": "SELL", "username": current_user, "asset_name": asset_name, "quantity": quantity}
            response = send_request(client_socket, request)
            client_socket.close()

            #server response
            if response and response.get("status") == "success":
                show_info_box(root,"Sale complete!", f"Sold {quantity} of {asset_name}.")
            else:
                show_error_box(root,"Sale error!", message=response.get("message"))
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    #window display for selling
    dialog = CustomInputDialog(root, title="Sell!", prompt=f"Enter number of {asset_name} to sell:",
                               callback=handle_sell_input)
    dialog.grab_set()

#buy metal
def buy_metal(metal_name):
    def handle_buy_input(quantity):
        try:
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            client_socket = connect_to_server()
            if not client_socket:
                return

            #buy metal request
            request = {"command": "BUY_METAL", "username": current_user, "metal_name": metal_name, "quantity": quantity}
            response = send_request(client_socket, request)
            client_socket.close()

            #server response
            if response and response.get("status") == "success":
                show_info_box(root,"Purchase complete!", f"Purchased {quantity} of {metal_name}.")
            else:
                show_error_box(root,"Purchase error!", message=response.get("message"))
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    #custom buying metal pop up
    dialog = CustomInputDialog(root, title="Buy Metal", prompt=f"Enter quantity of {metal_name} to buy:", callback=handle_buy_input)
    dialog.grab_set()

#sell metal
def sell_metal(metal_name):
    def handle_sell_input(quantity):
        try:
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            client_socket = connect_to_server()
            if not client_socket:
                return

            #sell metal request
            request = {"command": "SELL_METAL", "username": current_user, "metal_name": metal_name, "quantity": quantity}
            response = send_request(client_socket, request)
            client_socket.close()

            #server response
            if response and response.get("status") == "success":
                show_info_box(root,"Sale complete!", f"Sold {quantity} of {metal_name}.")
            else:
                show_error_box(root,"Sale error!", message=response.get("message"))
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    #custom selling metal popup
    dialog = CustomInputDialog(root, title="Sell Metal", prompt=f"Enter quantity of {metal_name} to sell:", callback=handle_sell_input)
    dialog.grab_set()

#transaction history functionality
def fetch_transaction_history():
    client_socket = connect_to_server()
    if not client_socket:
        return []
    try:
        request = {"command": "GET_TRANSACTIONS", "username": current_user}
        response = send_request(client_socket, request)
        client_socket.close()

        if response and response.get("status") == "success":
            return response.get("transactions", [])
        else:
            show_error_box(root,"Error", response.get("message", "Somehow failed to fetch transaction history.. :("))
            return []
    except Exception as e:
        print(f"Error fetching transaction history: {e}")
        return []

#portfolio functionality
def fetch_portfolio():
    client_socket = connect_to_server()
    if not client_socket:
        return {}
    try:
        request = {"command": "GET_PORTFOLIO", "username": current_user}
        response = send_request(client_socket, request)
        client_socket.close()

        if response and response.get("status") == "success":
            return response.get("portfolio", {})
        else:
            messagebox.showerror("Error", response.get("message", "Somehow failed to fetch portfolio!?"))
            return {}
    except Exception as e:
        print(f"Error fetching portfolio: {e}")
        return {}


### Pages ###

#home page
def show_home_page():
    ctk.CTkLabel(main_frame, text="Home Page", font=("Poppins", 24)).pack(pady=20)
    ctk.CTkLabel(main_frame, text="Welcome to the Crypto Platform!\nSelect one of the menus on the sidebar...!", font=("Poppins", 18)).pack(pady=10)

#wallet page
def show_wallet_page():
    #clear frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    ctk.CTkLabel(
        main_frame,
        text="Wallet",
        font=("Poppins", 24, "bold"),
        text_color="#00D1B2",
        anchor="w"
    ).pack(pady=20, padx=20, anchor="w")

    #balance
    balance_card = ctk.CTkFrame(main_frame, fg_color="#1A1A1A", corner_radius=15, width=300, height=120)
    balance_card.pack(pady=20, padx=20, anchor="w", fill="x")

    ctk.CTkLabel(
        balance_card,
        text="Total Balance",
        font=("Poppins", 14, "bold"),
        text_color="#D3D3D3"
    ).pack(anchor="w", pady=(15, 5), padx=15)

    #dynamic fetching
    balance_label = ctk.CTkLabel(
        balance_card,
        text="Fetching balance...",
        font=("Poppins", 26, "bold"),
        text_color="#00D1B2"
    )
    balance_label.pack(anchor="w", padx=15)

    #update balance, fetched from server
    def update_balance_display():
        client_socket = connect_to_server()
        if not client_socket:
            balance_label.configure(text="Error fetching balance")
            return
        request = {"command": "GET_BALANCE", "username": current_user}
        response = send_request(client_socket, request)
        client_socket.close()

        if response and response.get("status") == "success":
            balance = response.get("balance", 0.0)
            balance_label.configure(text=f"${balance:,.2f}")
        else:
            balance_label.configure(text="Error fetching balance")

    update_balance_display()

    action_card = ctk.CTkFrame(main_frame, fg_color="#1A1A1A", corner_radius=15, width=600)
    action_card.pack(pady=20, padx=20, anchor="w", fill="x")

    #deposit
    deposit_frame = ctk.CTkFrame(action_card, fg_color="transparent")
    deposit_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    ctk.CTkLabel(
        deposit_frame,
        text="Deposit",
        font=("Poppins", 16, "bold"),
        text_color="#D3D3D3"
    ).grid(row=0, column=0, pady=(10, 5), sticky="w")

    deposit_entry = ctk.CTkEntry(
        deposit_frame,
        placeholder_text="Enter amount",
        fg_color="#222222",
        corner_radius=10
    )
    deposit_entry.grid(row=1, column=0, pady=10, sticky="ew")

    ctk.CTkButton(
        deposit_frame,
        text="Deposit",
        command=lambda: deposit_funds(deposit_entry.get()),  #call deposit function
        fg_color="#00D1B2",
        text_color="black",
        hover_color="#00A596"
    ).grid(row=2, column=0, pady=(10, 5), sticky="ew")

    #withdraw
    withdraw_frame = ctk.CTkFrame(action_card, fg_color="transparent")
    withdraw_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    ctk.CTkLabel(
        withdraw_frame,
        text="Withdraw",
        font=("Poppins", 16, "bold"),
        text_color="#D3D3D3"
    ).grid(row=0, column=0, pady=(10, 5), sticky="w")

    withdraw_entry = ctk.CTkEntry(
        withdraw_frame,
        placeholder_text="Enter amount",
        fg_color="#222222",
        corner_radius=10
    )
    withdraw_entry.grid(row=1, column=0, pady=10, sticky="ew")

    ctk.CTkButton(
        withdraw_frame,
        text="Withdraw",
        command=lambda: withdraw_funds(withdraw_entry.get()),  #call withdraw function
        fg_color="#00D1B2",
        text_color="black",
        hover_color="#00A596"
    ).grid(row=2, column=0, pady=(10, 5), sticky="ew")

    action_card.grid_columnconfigure(0, weight=1)
    action_card.grid_columnconfigure(1, weight=1)

    #deposit funds function
    def deposit_funds(amount):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
            client_socket = connect_to_server()
            if not client_socket:
                return
            request = {"command": "DEPOSIT", "username": current_user, "amount": amount}
            response = send_request(client_socket, request)
            client_socket.close()

            if response.get("status") == "success":
                show_info_box(root,"Success", f"${amount:.2f} deposited into your wallet!")
                update_balance_display()
            else:
                show_error_box(root,"Error", response.get("message", "Failed to deposit funds?"))
        except ValueError:
            show_error_box(root,"Error", "Please enter a valid amount.")

    #withdraw funds function
    def withdraw_funds(amount):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
            client_socket = connect_to_server()
            if not client_socket:
                return
            request = {"command": "WITHDRAW", "username": current_user, "amount": amount}
            response = send_request(client_socket, request)
            client_socket.close()

            if response.get("status") == "success":
                show_info_box(root,"Success", f"${amount:.2f} withdrawn from your wallet!")
                update_balance_display()
            else:
                show_error_box(root,"Error", response.get("message", "Failed to withdraw funds?"))
        except ValueError:
            show_error_box(root,"Error", "Please enter a valid amount.")

#transaction history page
def show_transaction_history_page():
    #clear the frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    ctk.CTkLabel(
        main_frame,
        text="Transaction History",
        font=("Poppins", 24, "bold"),
        text_color="#00D1B2",
        anchor="w"
    ).pack(pady=20, padx=20, anchor="w")

    #scroll bar
    scroll_frame = ctk.CTkScrollableFrame(
        main_frame,
        fg_color="#1A1A1A",
        width=1200,
        height=500,
        scrollbar_button_color="#707070",
        scrollbar_button_hover_color="#909090",
    )
    scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

    #fetch transactions from server
    transactions = []
    try:
        client_socket = connect_to_server()
        if client_socket:
            request = {"command": "GET_TRANSACTIONS", "username": current_user}
            response = send_request(client_socket, request)
            client_socket.close()

            if response.get("status") == "success":
                transactions = response.get("transactions", [])
            else:
                #debug
                ctk.CTkLabel(
                    scroll_frame,
                    text=response.get("message", "Failed to fetch transactions. Aw :("),
                    font=("Poppins", 16),
                    text_color="#FF4B4B"
                ).pack(pady=20)
                return
        else:
            #connection error msg
            ctk.CTkLabel(
                scroll_frame,
                text="Failed to connect to the server.",
                font=("Poppins", 16),
                text_color="#FF4B4B"
            ).pack(pady=20)
            return
    except Exception as e:
        #unexpected errors
        ctk.CTkLabel(
            scroll_frame,
            text=f"Error: {e}",
            font=("Poppins", 16),
            text_color="#FF4B4B"
        ).pack(pady=20)
        return

    #if no transaction is found
    if not transactions:
        ctk.CTkLabel(
            scroll_frame,
            text="No transactions found.",
            font=("Poppins", 16),
            text_color="#D3D3D3"
        ).pack(pady=20)
        return

    column_headers = ["Asset", "Quantity", "Action", "Total", "Timestamp"]
    column_alignments = ["w", "center", "center", "e", "e"]

    header_frame = ctk.CTkFrame(scroll_frame, fg_color="#141414")
    header_frame.grid(row=0, column=0, sticky="nsew")
    for idx, header in enumerate(column_headers):
        ctk.CTkLabel(
            header_frame,
            text=header,
            font=("Poppins", 14, "bold"),
            text_color="#00D1B2",
            anchor=column_alignments[idx],
        ).grid(row=0, column=idx, padx=15, pady=10, sticky="ew")

    for i in range(len(column_headers)):
        header_frame.grid_columnconfigure(i, weight=1)

    #transaction rows
    for i, transaction in enumerate(transactions):
        asset_name, quantity, action, total, timestamp = transaction

        row_color = "#1A1A1A" if i % 2 == 0 else "#222222"
        transaction_frame = ctk.CTkFrame(scroll_frame, fg_color=row_color)
        transaction_frame.grid(row=i + 1, column=0, sticky="nsew")

        for col_idx, value in enumerate([asset_name, f"{quantity:.2f}", action.title(), f"${total:.2f}", timestamp]):
            text_color = (
                "#D3D3D3" if col_idx != 2 else ("#00D1B2" if action.lower() == "buy" else "#FF4B4B")
            )
            anchor = column_alignments[col_idx]

            ctk.CTkLabel(
                transaction_frame,
                text=value,
                font=("Poppins", 12),
                text_color=text_color,
                anchor=anchor,
            ).grid(row=0, column=col_idx, padx=15, pady=10, sticky="ew")

        for j in range(len(column_headers)):
            transaction_frame.grid_columnconfigure(j, weight=1)

    for i in range(len(column_headers)):
        scroll_frame.grid_columnconfigure(i, weight=1)


#crypto page
def show_crypto_page():
    ctk.CTkLabel(
        main_frame, text="Crypto Investments", font=("Poppins", 24, "bold"), text_color="#00D1B2"
    ).pack(pady=20, padx=20, anchor="w")

    #scroll bar
    scrollable_frame = ctk.CTkScrollableFrame(
        main_frame,
        fg_color="#1A1A1A",
        scrollbar_button_color="#707070",
        scrollbar_button_hover_color="#909090",
    )
    scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

    update_crypto_cards(scrollable_frame)  #dynamically adding cards without manual input

#metals page
def show_metals_page():
    ctk.CTkLabel(
        main_frame, text="Metal Investments", font=("Poppins", 24, "bold"), text_color="#00D1B2"
    ).pack(pady=20, padx=20, anchor="w")

    #scroll bar
    scrollable_frame = ctk.CTkScrollableFrame(
        main_frame,
        fg_color="#1A1A1A",
        scrollbar_button_color="#707070",
        scrollbar_button_hover_color="#909090",
    )
    scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

    update_metal_cards(scrollable_frame) #dynamically adding cards without manual input

#portfolio page
def show_portfolio_page():
    #clear frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    ctk.CTkLabel(
        main_frame,
        text="Portfolio",
        font=("Poppins", 24, "bold"),
        text_color="#00D1B2",
        anchor="w"
    ).pack(pady=20, padx=20, anchor="w")

    #general frame
    portfolio_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    portfolio_frame.pack(fill="both", expand=True, padx=20, pady=20)

    #frame to hold crypto holdings
    crypto_frame = ctk.CTkScrollableFrame(
        portfolio_frame,
        fg_color="#1A1A1A",
        scrollbar_button_color="#707070",
        scrollbar_button_hover_color="#909090",
        width=600,
        height=500
    )
    crypto_frame.grid(row=0, column=0, padx=(0, 15), sticky="nsew")

    #frame to hold metal holdings
    metals_frame = ctk.CTkScrollableFrame(
        portfolio_frame,
        fg_color="#1A1A1A",
        scrollbar_button_color="#707070",
        scrollbar_button_hover_color="#909090",
        width=600,
        height=500
    )
    metals_frame.grid(row=0, column=1, padx=(15, 0), sticky="nsew")

    #create table helper function
    def create_table(frame, headers, data):
        header_frame = ctk.CTkFrame(frame, fg_color="#141414")
        header_frame.grid(row=0, column=0, sticky="ew")
        for idx, header in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Poppins", 14, "bold"),
                text_color="#00D1B2",
                anchor="center"
            ).grid(row=0, column=idx, padx=15, pady=10, sticky="ew")

        for i in range(len(headers)):
            header_frame.grid_columnconfigure(i, weight=1)

        #dynamically create rows from data
        for i, row in enumerate(data):
            row_color = "#1A1A1A" if i % 2 == 0 else "#222222"
            row_frame = ctk.CTkFrame(frame, fg_color=row_color)
            row_frame.grid(row=i + 1, column=0, sticky="ew")

            for col_idx, value in enumerate(row):
                ctk.CTkLabel(
                    row_frame,
                    text=value,
                    font=("Poppins", 12),
                    text_color="#D3D3D3",
                    anchor="center"
                ).grid(row=0, column=col_idx, padx=15, pady=10, sticky="ew")

            for j in range(len(headers)):
                row_frame.grid_columnconfigure(j, weight=1)

    # portfolio data fetching from server
    def load_portfolio_data():
        client_socket = connect_to_server()
        if not client_socket:
            return {}, {}

        request = {"command": "GET_PORTFOLIO", "username": current_user}
        response = send_request(client_socket, request)
        client_socket.close()

        if response.get("status") == "success":
            return response.get("crypto_holdings", {}), response.get("metal_holdings", {})
        else:
            show_error_box(root,"Error", response.get("message", "Failed to fetch portfolio data?! How?"))
            return {}, {}

    #load crypto and metal data into tables
    def load_crypto_holdings(crypto_holdings):
        crypto_headers = ["Crypto", "Quantity", "Value"]
        crypto_data = [
            [asset, qty, f"${qty * crypto_prices.get(asset.lower(), 0):,.2f}"]
            for asset, qty in crypto_holdings.items()
        ]
        create_table(crypto_frame, crypto_headers, crypto_data)

    #metal holdings data for portfolio
    def load_metals_holdings(metal_holdings):
        metals_headers = ["Metal", "Quantity", "Value"]
        metals_data = [
            [metal, qty, f"${qty * metal_prices.get(metal.lower(), 0):,.2f}"]
            for metal, qty in metal_holdings.items()
        ]
        create_table(metals_frame, metals_headers, metals_data)

    #fetch portfolio and live prices
    crypto_holdings, metal_holdings = load_portfolio_data()
    crypto_prices = fetch_crypto_prices()
    metal_prices = fetch_metal_prices()

    #dynamically adding cards without manual input
    load_crypto_holdings(crypto_holdings)
    load_metals_holdings(metal_holdings)

    portfolio_frame.grid_columnconfigure(0, weight=1)
    portfolio_frame.grid_columnconfigure(1, weight=1)

#sidebar dashboard
def show_dashboard():
    global sidebar, main_frame  #the global variables i said we would use later
    root.state("zoomed")

    #clear all widgets in root except sidebar
    for widget in root.winfo_children():
        if widget != sidebar:
            widget.destroy()

    #recreate the sidebar if it doesn't exist
    if sidebar is None or not sidebar.winfo_exists():
        sidebar = ctk.CTkFrame(root, width=200, fg_color="#141414", corner_radius=15)
        sidebar.pack(side="left", fill="y", padx=5)

        ctk.CTkLabel(
            sidebar, text="Dashboard", font=("Poppins", 20, "bold"), text_color="#00D1B2"
        ).pack(pady=20)

        #buttons
        sidebar_buttons = [
            ("Home", show_home_page),
            ("Portfolio", show_portfolio_page),
            ("Wallet", show_wallet_page),
            ("Transaction History", show_transaction_history_page),
            ("Crypto Investments", show_crypto_page),
            ("Metals", show_metals_page),
        ]

        for text, page in sidebar_buttons:
            ctk.CTkButton(
                sidebar,
                text=text,
                command=lambda page=page: show_page(page),
                fg_color="#1A1A1A",
                hover_color="#00A596",
                text_color="#D3D3D3",
                font=("Poppins", 14),
            ).pack(fill="x", pady=5, padx=10)

        #logout button
        ctk.CTkButton(
            sidebar,
            text="Logout",
            command=show_login_screen,
            fg_color="#FF4B4B",
            hover_color="#FF6666",
            text_color="white",
            font=("Poppins", 14),
        ).pack(side="bottom", pady=20)

    #recreate the main content frame (because it was destroyed)
    if main_frame:
        main_frame.destroy()
    main_frame = ctk.CTkFrame(root, fg_color="#1A1A1A")
    main_frame.pack(side="right", fill="both", expand=True)

    show_home_page()

#login gui
def show_login_screen():
    global sidebar, main_frame  #the global variables from before, again

    #destroy all widgets in root, including the sidebar
    for widget in root.winfo_children():
        widget.destroy()

    #reset sidebar to None to ensure it gets recreated when logging back in
    sidebar = None #basically what we did at the beginning of the code

    #recreate main_frame
    main_frame = ctk.CTkFrame(root, fg_color="#121212")
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(
        main_frame,
        text="Welcome Back",
        font=("Poppins", 24, "bold"),
        text_color="#00D1B2",
    ).pack(pady=(50, 10))

    ctk.CTkLabel(
        main_frame,
        text="Log in to continue",
        font=("Poppins", 14),
        text_color="#D3D3D3",
    ).pack(pady=(0, 30))

    #input section
    input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    input_frame.pack(pady=10)

    #username
    ctk.CTkLabel(
        input_frame,
        text="Username",
        font=("Poppins", 12),
        text_color="#D3D3D3",
    ).grid(row=0, column=0, pady=(10, 5), sticky="w")

    username_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="Enter your username",
        fg_color="#222222",
        text_color="#D3D3D3",
        corner_radius=10,
        width=300,
    )
    username_entry.grid(row=1, column=0, pady=(0, 15))

    #password
    ctk.CTkLabel(
        input_frame,
        text="Password",
        font=("Poppins", 12),
        text_color="#D3D3D3",
    ).grid(row=2, column=0, pady=(10, 5), sticky="w")

    password_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="Enter your password",
        fg_color="#222222",
        text_color="#D3D3D3",
        show="*",
        corner_radius=10,
        width=300,
    )
    password_entry.grid(row=3, column=0, pady=(0, 15))

    #login button
    ctk.CTkButton(
        main_frame,
        text="Login",
        command=lambda: login_action(username_entry.get(), password_entry.get()),
        fg_color="#00D1B2",
        text_color="black",
        hover_color="#00A596",
        width=300,
        corner_radius=10,
    ).pack(pady=(10, 20))

    #switch to signup
    ctk.CTkLabel(
        main_frame,
        text="Don't have an account?",
        font=("Poppins", 12),
        text_color="#D3D3D3",
    ).pack()

    ctk.CTkButton(
        main_frame,
        text="Sign Up",
        command=show_signup_screen,
        fg_color="transparent",
        text_color="#00D1B2",
        hover_color="#121212",
        font=("Poppins", 12, "bold"),
    ).pack(pady=(5, 10))

#signup gui
def show_signup_screen():
    global main_frame

    #clear any existing widgets in main_frame
    for widget in root.winfo_children():
        widget.destroy()

    #recreate main_frame
    main_frame = ctk.CTkFrame(root, fg_color="#121212")
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(
        main_frame,
        text="Create an Account",
        font=("Poppins", 24, "bold"),
        text_color="#00D1B2",
    ).pack(pady=(50, 10))

    ctk.CTkLabel(
        main_frame,
        text="Sign up to get started",
        font=("Poppins", 14),
        text_color="#D3D3D3",
    ).pack(pady=(0, 30))

    #input section
    input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    input_frame.pack(pady=10)

    #username
    ctk.CTkLabel(
        input_frame,
        text="Username",
        font=("Poppins", 12),
        text_color="#D3D3D3",
    ).grid(row=0, column=0, pady=(10, 5), sticky="w")

    username_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="Enter your username",
        fg_color="#222222",
        text_color="#D3D3D3",
        corner_radius=10,
        width=300,
    )
    username_entry.grid(row=1, column=0, pady=(0, 15))

    #password input
    ctk.CTkLabel(
        input_frame,
        text="Password",
        font=("Poppins", 12),
        text_color="#D3D3D3",
    ).grid(row=2, column=0, pady=(10, 5), sticky="w")

    password_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="Enter your password",
        fg_color="#222222",
        text_color="#D3D3D3",
        show="*",
        corner_radius=10,
        width=300,
    )
    password_entry.grid(row=3, column=0, pady=(0, 15))

    #confirm password
    ctk.CTkLabel(
        input_frame,
        text="Confirm Password",
        font=("Poppins", 12),
        text_color="#D3D3D3",
    ).grid(row=4, column=0, pady=(10, 5), sticky="w")

    confirm_password_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="Confirm your password",
        fg_color="#222222",
        text_color="#D3D3D3",
        show="*",
        corner_radius=10,
        width=300,
    )
    confirm_password_entry.grid(row=5, column=0, pady=(0, 15))

    #signup button
    ctk.CTkButton(
        main_frame,
        text="Sign Up",
        command=lambda: signup_action(username_entry.get(), password_entry.get(), confirm_password_entry.get()),
        fg_color="#00D1B2",
        text_color="black",
        hover_color="#00A596",
        width=300,
        corner_radius=10,
    ).pack(pady=(10, 20))

    #switch to login
    ctk.CTkLabel(
        main_frame,
        text="Already have an account?",
        font=("Poppins", 12),
        text_color="#D3D3D3",
    ).pack()

    ctk.CTkButton(
        main_frame,
        text="Login",
        command=show_login_screen,
        fg_color="transparent",
        text_color="#00D1B2",
        hover_color="#121212",
        font=("Poppins", 12, "bold"),
    ).pack(pady=(5, 10))

#login functionality
def login_action(username, password):
    if not username or not password:
        show_error_box(root,"Error", "Please fill in all fields!")
        return

    client_socket = connect_to_server()
    request = {"command": "LOGIN", "username": username, "password": password}
    response = send_request(client_socket, request)
    client_socket.close()

    if response.get("status") == "success":
        global current_user
        current_user = username
        show_dashboard()
    else:
        show_error_box(root,"Error", response.get("message", "Login failed?!"))

#sign up functionality
def signup_action(username, password, confirm_password):
    if not username or not password or not confirm_password:
        show_error_box(root,"Error", "Please fill in all fields!")
        return

    if password != confirm_password:
        show_error_box(root,"Error", "Passwords don't match.\nTry again!")
        return

    client_socket = connect_to_server()
    if not client_socket:
        show_error_box(root,"Error", "Unable to connect to the server... :(")
        return

    request = {"command": "CREATE_ACCOUNT", "username": username, "password": password}
    response = send_request(client_socket, request)
    client_socket.close()

    if response.get("status") == "success":
        show_info_box(root,"Success", "Account created.\nWelcome!")
        show_login_screen()
    else:
        show_error_box(root,"Error", response.get("message", "Oops... Signup failed?"))

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("800x625")
    root.title("Crypto Investment Platform")

    main_frame = ctk.CTkFrame(root, fg_color="#1A1A1A")
    main_frame.pack(fill="both", expand=True)

    show_login_screen()
    root.mainloop()
