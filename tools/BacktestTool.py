import yfinance as yf
import numpy as np
import pandas as pd
from pandas_datareader import data as pdr
from matplotlib import pyplot as plt
from datetime import date
from tools.AbstractTool import AbstractTool
from models.Options import Options


class BacktestTool(AbstractTool):
    """
    This class represents a tool for backtesting purposes.

    """
    yf.pdr_override()

    def __init__(self, initial_balance=1000.0, symbol='AAPL', initial_date="2019-01-01", final_date="2020-01-01"):
        """
        Class constructor.

        @param initial_balance: initial_balance
        @@type initial_balance: float
        @param symbols: symbols that should be used while backtesting
        @@type symbols: list of strings
        @param initial_date: initial date to get data
        @@type initial_date: datetime string in the format "%YYYY-%MM-%DD"
        @param final_date: final date to get data
        @@type final_date: datetime string in the format "%YYYY-%MM-%DD"
        """
        parameters = {
            "Initial balance": initial_balance,
            "Symbol": symbol,
            "Initial date": initial_date,
            "Final date": final_date
        }

        super().__init__(tool_name="Backtest", parameters=parameters)

        self.symbol = symbol
        self.data = None
        self.initial_date = initial_date
        self.final_date = final_date
        self.initial_balance = initial_balance

    def execute_agent(self, agent):
        """
        Runs the backtest tool.

        @param agent: the agent the method should be executed on.
        @@type agent: class Agent
        """
        data = self._get_data()

    def execute_model(self, model, save_log=True, plot_signals=False):
        """
        Runs the backtest tool.

        @param model: the model the method should be executed on.
        @@type agent: class derived from models.AbstractModel class
        """
        print(f'Running backtest on model {model.get_name()}...')

        data = self.get_data()
        model.update(data)
        signals = model.get_signals()

        generated_data = pd.DataFrame(index=signals.index)
        generated_data['Balance'] = (
            (1 + signals['Signal'] * signals['Change'].shift(1)).cumprod()) * self.initial_balance
        generated_data['Profit'] = (
            generated_data['Balance'] - self.initial_balance)
        generated_data['Profit %'] = (
            generated_data['Balance'] / self.initial_balance - 1) * 100
        generated_data['Options'] = signals['Signal']
        generated_data.fillna(0)


        plt.plot(generated_data.index, generated_data['Profit %'])
        plt.ylabel('% Profit')
        plt.xlabel('Date')
        plt.show()

        generated_data.index = generated_data.index.strftime("%Y-%m-%d")

        data = {}
        data['Model used'] = model.get_name()
        data['Initial date'] = self.initial_date
        data['Final date'] = self.final_date
        data['Initial balance (R$)'] = self.initial_balance 
        data['Final balance (R$)'] = generated_data['Balance'][-1]
        data['Final profit (R$)'] = generated_data['Profit'][-1]
        data['Final profit (%)'] = generated_data['Profit %'][-1]
        data['Total buy operations'] = int((generated_data['Options'] == Options.BUY).sum())
        data['Total sell operations'] = int((generated_data['Options'] == Options.SELL).sum())
        data['Total operations'] = data['Total buy operations'] + data['Total sell operations']
        data['History'] = generated_data.to_dict(orient='index')
        
        if plot_signals:
            model.plot()

        if save_log:
            print('Saving log...')
            self.log.log(data)

    def get_data(self):
        """
        Method to get data online using yahoo finance api.

        @return data: data achieved online
        @@@type data: list of dataframes
        """
        if self.initial_date and self.final_date:
            # Get stock data from yahoo
            self.data = pdr.get_data_yahoo(
                self.symbol, start=self.initial_date, end=self.final_date)

            return self.data

        elif not initial_date:
            raise ValueError("Initial date can't be an empty value.")

        else:
            raise ValueError("Final date can't be an empty value.")
    