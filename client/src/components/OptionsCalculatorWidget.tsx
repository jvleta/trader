import { useState } from 'react';
import { useOptionsCalculator } from '../hooks/useOptionsCalculator';

interface OptionsCalculatorProps {
  stockPrice: number;
  stockSymbol: string;
}

export function OptionsCalculatorWidget({ stockPrice, stockSymbol }: OptionsCalculatorProps) {
  const [strike, setStrike] = useState(stockPrice);
  const [expiry, setExpiry] = useState(30); // days
  const [volatility, setVolatility] = useState(25); // percentage
  const [riskFreeRate, setRiskFreeRate] = useState(5); // percentage
  
  const { 
    ready, 
    loading, 
    error, 
    calculateBlackScholes 
  } = useOptionsCalculator();

  const timeToExpiry = expiry / 365; // Convert days to years
  const vol = volatility / 100; // Convert percentage to decimal
  const rate = riskFreeRate / 100; // Convert percentage to decimal

  const result = ready ? calculateBlackScholes(
    stockPrice,
    strike,
    timeToExpiry,
    rate,
    vol
  ) : null;

  return (
    <div className="options-calculator">
      <h3>Options Calculator - {stockSymbol}</h3>
      
      {loading && <p className="loading">Loading WebAssembly calculator...</p>}
      {error && <p className="error">{error}</p>}
      
      <div className="calculator-inputs">
        <div className="input-group">
          <label>Current Stock Price:</label>
          <span className="stock-price">${stockPrice.toFixed(2)}</span>
        </div>
        
        <div className="input-group">
          <label htmlFor="strike">Strike Price ($):</label>
          <input
            id="strike"
            type="number"
            value={strike}
            onChange={(e) => setStrike(Number(e.target.value))}
            step="0.50"
            min="0"
          />
        </div>
        
        <div className="input-group">
          <label htmlFor="expiry">Days to Expiry:</label>
          <input
            id="expiry"
            type="number"
            value={expiry}
            onChange={(e) => setExpiry(Number(e.target.value))}
            min="1"
            max="1000"
          />
        </div>
        
        <div className="input-group">
          <label htmlFor="volatility">Implied Volatility (%):</label>
          <input
            id="volatility"
            type="number"
            value={volatility}
            onChange={(e) => setVolatility(Number(e.target.value))}
            step="0.1"
            min="0.1"
            max="200"
          />
        </div>
        
        <div className="input-group">
          <label htmlFor="rate">Risk-Free Rate (%):</label>
          <input
            id="rate"
            type="number"
            value={riskFreeRate}
            onChange={(e) => setRiskFreeRate(Number(e.target.value))}
            step="0.01"
            min="0"
            max="20"
          />
        </div>
      </div>

      {result && (
        <div className="calculation-results">
          <h4>Option Prices & Greeks</h4>
          
          <div className="results-grid">
            <div className="result-section">
              <h5>Option Prices</h5>
              <div className="result-item">
                <span>Call Price:</span>
                <span className="value">${result.call_price.toFixed(4)}</span>
              </div>
              <div className="result-item">
                <span>Put Price:</span>
                <span className="value">${result.put_price.toFixed(4)}</span>
              </div>
            </div>
            
            <div className="result-section">
              <h5>Greeks</h5>
              <div className="result-item">
                <span>Delta:</span>
                <span className="value">{result.delta.toFixed(4)}</span>
              </div>
              <div className="result-item">
                <span>Gamma:</span>
                <span className="value">{result.gamma.toFixed(6)}</span>
              </div>
              <div className="result-item">
                <span>Theta:</span>
                <span className="value">{result.theta.toFixed(4)}</span>
              </div>
              <div className="result-item">
                <span>Vega:</span>
                <span className="value">{result.vega.toFixed(4)}</span>
              </div>
              <div className="result-item">
                <span>Rho:</span>
                <span className="value">{result.rho.toFixed(4)}</span>
              </div>
            </div>
          </div>
          
          <div className="calculation-info">
            <small>
              {ready ? '⚡ Calculated using WebAssembly' : '📊 Calculated using JavaScript fallback'}
              {' • '}
              Time to expiry: {timeToExpiry.toFixed(4)} years
            </small>
          </div>
        </div>
      )}
    </div>
  );
}
