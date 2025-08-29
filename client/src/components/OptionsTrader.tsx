import { useState } from 'react';
import { OptionsCalculatorWidget } from './OptionsCalculatorWidget';

interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: string;
}

const STOCK_SYMBOLS = [
  { symbol: 'AAPL', name: 'Apple Inc.' },
  { symbol: 'QQQ', name: 'Invesco QQQ Trust' },
  { symbol: 'NVDA', name: 'NVIDIA Corporation' },
  { symbol: 'MSFT', name: 'Microsoft Corporation' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.' },
  { symbol: 'TSLA', name: 'Tesla, Inc.' },
  { symbol: 'SPY', name: 'SPDR S&P 500 ETF Trust' },
  { symbol: 'AMD', name: 'Advanced Micro Devices' },
];

// Mock data - in a real app, this would come from an API
const mockStockData: { [key: string]: Stock } = {
  AAPL: {
    symbol: 'AAPL',
    name: 'Apple Inc.',
    price: 191.45,
    change: 2.31,
    changePercent: 1.22,
    volume: 45234567,
    marketCap: '$2.95T'
  },
  QQQ: {
    symbol: 'QQQ',
    name: 'Invesco QQQ Trust',
    price: 478.23,
    change: -3.47,
    changePercent: -0.72,
    volume: 23456789,
    marketCap: '$208.5B'
  },
  NVDA: {
    symbol: 'NVDA',
    name: 'NVIDIA Corporation',
    price: 875.32,
    change: 12.85,
    changePercent: 1.49,
    volume: 34567890,
    marketCap: '$2.16T'
  },
  MSFT: {
    symbol: 'MSFT',
    name: 'Microsoft Corporation',
    price: 423.89,
    change: 5.67,
    changePercent: 1.36,
    volume: 18765432,
    marketCap: '$3.15T'
  },
  GOOGL: {
    symbol: 'GOOGL',
    name: 'Alphabet Inc.',
    price: 167.43,
    change: -1.23,
    changePercent: -0.73,
    volume: 21098765,
    marketCap: '$2.06T'
  },
  TSLA: {
    symbol: 'TSLA',
    name: 'Tesla, Inc.',
    price: 248.67,
    change: 8.91,
    changePercent: 3.72,
    volume: 67890123,
    marketCap: '$793.4B'
  },
  SPY: {
    symbol: 'SPY',
    name: 'SPDR S&P 500 ETF Trust',
    price: 579.12,
    change: 3.45,
    changePercent: 0.60,
    volume: 56789012,
    marketCap: '$537.2B'
  },
  AMD: {
    symbol: 'AMD',
    name: 'Advanced Micro Devices',
    price: 123.45,
    change: -2.34,
    changePercent: -1.86,
    volume: 43210987,
    marketCap: '$199.8B'
  }
};

interface StockSelectorProps {
  selectedStocks: string[];
  onStockToggle: (symbol: string) => void;
}

export function StockSelector({ selectedStocks, onStockToggle }: StockSelectorProps) {
  return (
    <div className="stock-selector">
      <h2>Select Stocks to Track</h2>
      <div className="stock-grid">
        {STOCK_SYMBOLS.map(({ symbol, name }) => (
          <label key={symbol} className="stock-option">
            <input
              type="checkbox"
              checked={selectedStocks.includes(symbol)}
              onChange={() => onStockToggle(symbol)}
            />
            <span className="stock-symbol">{symbol}</span>
            <span className="stock-name">{name}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

interface StockTableProps {
  selectedStocks: string[];
  onCalculateOptions?: (symbol: string) => void;
}

export function StockTable({ selectedStocks, onCalculateOptions }: StockTableProps) {
  const stockData = selectedStocks.map(symbol => mockStockData[symbol]).filter(Boolean);

  if (stockData.length === 0) {
    return (
      <div className="stock-table-container">
        <h2>Stock Data</h2>
        <p>Select stocks above to view their data</p>
      </div>
    );
  }

  return (
    <div className="stock-table-container">
      <h2>Stock Data</h2>
      <table className="stock-table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Name</th>
            <th>Price</th>
            <th>Change</th>
            <th>Change %</th>
            <th>Volume</th>
            <th>Market Cap</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {stockData.map((stock) => (
            <tr key={stock.symbol}>
              <td className="symbol">{stock.symbol}</td>
              <td className="name">{stock.name}</td>
              <td className="price">${stock.price.toFixed(2)}</td>
              <td className={`change ${stock.change >= 0 ? 'positive' : 'negative'}`}>
                {stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}
              </td>
              <td className={`change-percent ${stock.changePercent >= 0 ? 'positive' : 'negative'}`}>
                {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
              </td>
              <td className="volume">{stock.volume.toLocaleString()}</td>
              <td className="market-cap">{stock.marketCap}</td>
              <td className="actions">
                {onCalculateOptions && (
                  <button 
                    className="calculate-btn"
                    onClick={() => onCalculateOptions(stock.symbol)}
                  >
                    Calculate Options
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function OptionsTrader() {
  const [selectedStocks, setSelectedStocks] = useState<string[]>(['AAPL', 'QQQ']);
  const [calculatorStock, setCalculatorStock] = useState<string | null>(null);

  const handleStockToggle = (symbol: string) => {
    setSelectedStocks(prev => 
      prev.includes(symbol)
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    );
  };

  const handleCalculateOptions = (symbol: string) => {
    setCalculatorStock(symbol);
  };

  return (
    <div className="options-trader">
      <h1>Options Trading Learning Tool</h1>
      
      <StockSelector 
        selectedStocks={selectedStocks}
        onStockToggle={handleStockToggle}
      />
      
      <StockTable 
        selectedStocks={selectedStocks} 
        onCalculateOptions={handleCalculateOptions}
      />
      
      {calculatorStock && mockStockData[calculatorStock] && (
        <OptionsCalculatorWidget
          stockPrice={mockStockData[calculatorStock].price}
          stockSymbol={calculatorStock}
        />
      )}
    </div>
  );
}
