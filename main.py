import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
from decimal import Decimal
import pandas as pd

class ModernTradingCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Risk Calculator")
        self.root.configure(bg='#000000')
        self.root.geometry('330x480')
        self.root.resizable(True, True)
        self.setup_styles()
        self.main_frame = ttk.Frame(root, style='Card.TFrame', padding="10")
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.acc_leverage = tk.StringVar(value="100")
        self.lot_size = tk.StringVar(value="0.01")
        self.acc_currency = tk.StringVar(value="USD")
        self.acc_balance = tk.StringVar(value="100")
        self.acc_equity = tk.StringVar(value="100")
        self.ticker = tk.StringVar(value="EUR/USD")
        self.create_header()
        self.create_input_fields()
        self.create_calculate_button()
        self.create_results_area()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Card.TFrame', background='#000000', borderwidth=1, relief='solid')
        style.configure('Header.TLabel', font=('Courier', 14, 'bold'), foreground='#00ff00', background='#000000', padding=5)
        style.configure('Modern.TLabel', font=('Courier', 9), foreground='#00ff00', background='#000000')
        style.configure('Modern.TEntry', fieldbackground='#001100', foreground='#00ff00', borderwidth=1, relief='solid')
        style.configure('Calculate.TButton', font=('Courier', 10, 'bold'), background='#00ff00', foreground='#000000', padding=5)
        style.configure('Section.TLabel', font=('Courier', 11, 'bold'), foreground='#00ff00', background='#000000', padding=(0, 5, 0, 2))

    def create_header(self):
        header = ttk.Label(self.main_frame, text="Trading Risk Calculator", style='Header.TLabel')
        header.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))

    def create_input_fields(self):
        fields = [
            ("Account Balance:", self.acc_balance),
            ("Account Equity:", self.acc_equity),
            ("Account Leverage:", self.acc_leverage),
            ("Account Currency:", self.acc_currency),
            ("Lot Size:", self.lot_size),
            ("Ticker Symbol:", self.ticker)
        ]
        
        for idx, (label, var) in enumerate(fields):
            ttk.Label(self.main_frame, text=label, style='Modern.TLabel').grid(row=idx+1, column=0, sticky='w', pady=2)
            entry = ttk.Entry(self.main_frame, textvariable=var, style='Modern.TEntry', width=25)
            entry.grid(row=idx+1, column=1, sticky='ew', padx=(5, 0), pady=2)

    def create_calculate_button(self):
        calculate_btn = ttk.Button(self.main_frame, text="Calculate Risk", style='Calculate.TButton', command=self.calculate)
        calculate_btn.grid(row=7, column=0, columnspan=2, pady=10, sticky='ew')

    def create_results_area(self):
        self.result_text = tk.Text(self.main_frame, height=12, width=40, font=('Courier', 9),
                                 wrap=tk.WORD, borderwidth=1, relief='solid', padx=5, pady=5)
        self.result_text.grid(row=8, column=0, columnspan=2, sticky='ew', pady=(2, 0))
        self.result_text.configure(bg='#001100', fg='#00ff00', insertbackground='#00ff00')
        self.result_text.tag_configure('header', font=('Courier', 10, 'bold'), foreground='#00ff00')
        self.result_text.tag_configure('warning', font=('Courier', 9, 'bold'), foreground='#ff0000')

    def get_ticker_info(self, symbol):
        if '/' in symbol:
            symbol = symbol.replace("/", "") + "=X"
        try:
            data = yf.Ticker(symbol)
            price = data.history(period="1d")['Close'][0]
            return price
        except Exception as e:
            return None

    def calculate_forex_money_required(self, lot_size, pair_value, acc_currency, pair_symbol):
        acc_currency = self.acc_currency.get()
        money_required_in_pair_currency = lot_size * 100000 * pair_value
        if acc_currency==pair_symbol[:3] or acc_currency==pair_symbol[-3:]:
            return money_required_in_pair_currency
        exchange_rate_with_acc_currency = self.get_ticker_info(f"{pair_symbol[:3]}/{acc_currency}")
        return money_required_in_pair_currency * exchange_rate_with_acc_currency

    def calculate_stock_money_required(self, shares, price):
        return shares * price

    def calculate_projections(self, initial_equity, position_size, leverage):
        scenarios = {
            "5% Loss": -0.05,
            "10% Loss": -0.10,
            "20% Loss": -0.20,
            "5% Gain": 0.05,
            "10% Gain": 0.10,
            "20% Gain": 0.20
        }
        results = {}
        for scenario, pct_change in scenarios.items():
            pnl = position_size * pct_change
            new_equity = initial_equity + pnl
            results[scenario] = new_equity
        return results

    def calculate(self):
        try:
            self.result_text.delete(1.0, tk.END)
            leverage = float(self.acc_leverage.get())
            lot_size = float(self.lot_size.get())
            acc_currency = self.acc_currency.get()
            balance = float(self.acc_balance.get())
            equity = float(self.acc_equity.get())
            ticker_symbol = self.ticker.get().upper()
            
            current_price = self.get_ticker_info(ticker_symbol)
            if current_price is None:
                return
            
            if "/" in ticker_symbol:
                money_required = self.calculate_forex_money_required(lot_size, current_price, self.acc_currency, ticker_symbol)
            else:
                shares = lot_size * 100
                money_required = self.calculate_stock_money_required(shares, current_price)
            
            margin_required = money_required / leverage
            projections = self.calculate_projections(equity, money_required, leverage)
            
            self.result_text.insert(tk.END, "CALCULATION RESULTS\n", 'header')
            self.result_text.insert(tk.END, f"Balance: {balance:,.2f} {acc_currency}\n")
            self.result_text.insert(tk.END, f"Equity: {equity:,.2f} {acc_currency}\n")
            self.result_text.insert(tk.END, f"Margin Req: {margin_required:,.2f} {acc_currency}\n")
            self.result_text.insert(tk.END, f"Free Margin: {equity-margin_required:,.2f} {acc_currency}\n")
            self.result_text.insert(tk.END, f"Price ({ticker_symbol}): {current_price:.4f}\n\n")
            
            self.result_text.insert(tk.END, "RISK PROJECTIONS\n", 'header')
            for scenario, new_equity in projections.items():
                self.result_text.insert(tk.END, f"{scenario}: {new_equity:,.2f}\n")
            
            if margin_required > equity:
                self.result_text.insert(tk.END, "\n! MARGIN EXCEEDS EQUITY !", 'warning')
            if margin_required > balance * 0.5:
                self.result_text.insert(tk.END, "\n! POSITION > 50% BALANCE !", 'warning')
                
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")

def main():
    root = tk.Tk()
    app = ModernTradingCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()