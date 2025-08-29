import { useState, useEffect, useCallback } from 'react';

// Define the types directly in this file to avoid import issues
interface OptionResult {
  call_price: number;
  put_price: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
}

interface Position {
  quantity: number;
  strike: number;
  expiry: number;
  is_call: boolean;
  market_price: number;
}

interface PortfolioGreeks {
  total_delta: number;
  total_gamma: number;
  total_theta: number;
  total_vega: number;
  total_rho: number;
  portfolio_value: number;
}

interface OptionsModule {
  BlackScholesCalculator: {
    calculate(spot: number, strike: number, timeToExpiry: number, riskFreeRate: number, volatility: number): OptionResult;
  };
  ImpliedVolatilityCalculator: {
    calculate(spot: number, strike: number, timeToExpiry: number, riskFreeRate: number, marketPrice: number, isCall?: boolean): number;
  };
  PortfolioAnalyzer: {
    analyze(spotPrice: number, riskFreeRate: number, positions: Position[]): PortfolioGreeks;
  };
  MonteCarloEngine: {
    simulate_asian_option(S0: number, K: number, T: number, r: number, sigma: number, numPaths: number, numSteps: number, isCall?: boolean): number;
  };
}

// Hook to load and use the WebAssembly options calculator
export function useOptionsCalculator() {
  const [module, setModule] = useState<OptionsModule | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadModule = async () => {
      try {
        // For now, skip WebAssembly loading and go straight to JavaScript fallback
        // This ensures the calculator works while we debug the WASM integration
        console.log('Using JavaScript fallback for options calculations');
        setError('Using JavaScript implementation (WebAssembly integration in progress)');
        setLoading(false);
      } catch (err) {
        console.warn('WebAssembly module not available, using JavaScript fallback:', err);
        setError('WebAssembly not available. Using JavaScript fallback.');
        setLoading(false);
      }
    };

    loadModule();
  }, []);

  // Black-Scholes calculation with fallback
  const calculateBlackScholes = useCallback((
    spot: number,
    strike: number,
    timeToExpiry: number,
    riskFreeRate: number,
    volatility: number
  ): OptionResult | null => {
    if (!module) {
      // Fallback JavaScript implementation (simplified)
      return calculateBlackScholesJS(spot, strike, timeToExpiry, riskFreeRate, volatility);
    }

    try {
      return module.BlackScholesCalculator.calculate(
        spot, strike, timeToExpiry, riskFreeRate, volatility
      );
    } catch (err) {
      console.error('WebAssembly calculation failed:', err);
      return calculateBlackScholesJS(spot, strike, timeToExpiry, riskFreeRate, volatility);
    }
  }, [module]);

  // Implied volatility calculation
  const calculateImpliedVolatility = useCallback((
    spot: number,
    strike: number,
    timeToExpiry: number,
    riskFreeRate: number,
    marketPrice: number,
    isCall: boolean = true
  ): number | null => {
    if (!module) return null;

    try {
      return module.ImpliedVolatilityCalculator.calculate(
        spot, strike, timeToExpiry, riskFreeRate, marketPrice, isCall
      );
    } catch (err) {
      console.error('Implied volatility calculation failed:', err);
      return null;
    }
  }, [module]);

  // Portfolio analysis
  const analyzePortfolio = useCallback((
    spotPrice: number,
    riskFreeRate: number,
    positions: Position[]
  ): PortfolioGreeks | null => {
    if (!module) return null;

    try {
      return module.PortfolioAnalyzer.analyze(spotPrice, riskFreeRate, positions);
    } catch (err) {
      console.error('Portfolio analysis failed:', err);
      return null;
    }
  }, [module]);

  // Monte Carlo simulation
  const simulateAsianOption = useCallback((
    S0: number,
    K: number,
    T: number,
    r: number,
    sigma: number,
    numPaths: number = 100000,
    numSteps: number = 252,
    isCall: boolean = true
  ): number | null => {
    if (!module) return null;

    try {
      return module.MonteCarloEngine.simulate_asian_option(
        S0, K, T, r, sigma, numPaths, numSteps, isCall
      );
    } catch (err) {
      console.error('Monte Carlo simulation failed:', err);
      return null;
    }
  }, [module]);

  return {
    ready: !loading, // Always ready since we use JavaScript fallback
    loading,
    error,
    calculateBlackScholes,
    calculateImpliedVolatility,
    analyzePortfolio,
    simulateAsianOption,
  };
}

// Fallback JavaScript Black-Scholes implementation
function calculateBlackScholesJS(
  S: number,
  K: number,
  T: number,
  r: number,
  sigma: number
): OptionResult {
  // Standard normal CDF approximation
  const normCDF = (x: number): number => {
    return 0.5 * (1 + erf(x / Math.sqrt(2)));
  };

  // Error function approximation
  const erf = (x: number): number => {
    const a1 =  0.254829592;
    const a2 = -0.284496736;
    const a3 =  1.421413741;
    const a4 = -1.453152027;
    const a5 =  1.061405429;
    const p  =  0.3275911;

    const sign = x >= 0 ? 1 : -1;
    x = Math.abs(x);

    const t = 1.0 / (1.0 + p * x);
    const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);

    return sign * y;
  };

  // Standard normal PDF
  const normPDF = (x: number): number => {
    return (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * x * x);
  };

  const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T));
  const d2 = d1 - sigma * Math.sqrt(T);

  const callPrice = S * normCDF(d1) - K * Math.exp(-r * T) * normCDF(d2);
  const putPrice = K * Math.exp(-r * T) * normCDF(-d2) - S * normCDF(-d1);

  // Greeks
  const delta = normCDF(d1);
  const gamma = normPDF(d1) / (S * sigma * Math.sqrt(T));
  const theta = -(S * normPDF(d1) * sigma) / (2 * Math.sqrt(T)) - r * K * Math.exp(-r * T) * normCDF(d2);
  const vega = S * normPDF(d1) * Math.sqrt(T);
  const rho = K * T * Math.exp(-r * T) * normCDF(d2);

  return {
    call_price: callPrice,
    put_price: putPrice,
    delta,
    gamma,
    theta,
    vega,
    rho,
  };
}
