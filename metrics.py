import pandas as pd


class ComputeMetricsTemplate:

    def __init__(self):
        self.call_type = None

    def filter_on_call_type(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
    
    def compute_premium(self, df: pd.DataFrame) -> pd.DataFrame:
        df["premium"] = (df["bid"] + df["ask"]) / 2
        return df
    
    def filter_on_liquidity(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[df["premium"] > 0]
        return df

    def compute_percent_otm(self, df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        df["pct_otm"] = (df["strike"] - spot_price) / spot_price * 100
        return df
    
    def compute_percent_itm(self, df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        df["pct_itm"] = (spot_price - df["strike"]) / spot_price * 100
        return df
    
    def compute_breakeven(self, df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        raise NotImplementedError
    
    def compute_dte(self, df: pd.DataFrame) -> pd.DataFrame:
        df["dte"] = (pd.to_datetime(df["expiration"]) - pd.Timestamp.today()).dt.days
        return df
    
    def compute_annualized_yield(self, df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        df["annualized_yield"] = (df["premium"] / spot_price) * (365.0 / df["dte"])
        return df
    
    def filter_on_strike_price(self, df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        raise NotImplementedError
    
    def compute(self, df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        df = df.copy()
        df = self.filter_on_call_type(df)
        df = self.compute_premium(df)
        df = self.filter_on_liquidity(df)
        df = self.compute_percent_otm(df, spot_price)
        df = self.compute_percent_itm(df, spot_price)
        df = self.compute_breakeven(df, spot_price)
        df = self.compute_dte(df)
        df = self.compute_annualized_yield(df, spot_price)
        df = self.filter_on_strike_price(df, spot_price)
        return df

class CoveredCallMetrics(ComputeMetricsTemplate):

    def __init__(self):
        super().__init__()
        self.call_type = "call"

    def filter_on_call_type(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df["option_type"] == "call"]
    
    def compute_breakeven(self, df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        df["breakeven"] = spot_price - df["premium"]
        return df
    
    def filter_on_strike_price(self, df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        return df[df["strike"] >= spot_price]

class CashSecuredPutMetrics(ComputeMetricsTemplate):
    
    def __init__(self):
        super().__init__()
        self.call_type = "put"

    def filter_on_call_type(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df["option_type"] == "put"]
    
    def compute_breakeven(self, df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        df["breakeven"] = spot_price + df["premium"]
        return df
    
    def filter_on_strike_price(self, df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        return df[df["strike"] <= spot_price]
    
def compute_covered_call_metrics(df: pd.DataFrame, spot_price: float):
    return CoveredCallMetrics().compute(df, spot_price)

def compute_cash_secured_put_metrics(df: pd.DataFrame, spot_price: float):
    return CashSecuredPutMetrics().compute(df, spot_price)


