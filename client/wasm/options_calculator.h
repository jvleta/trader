#pragma once

#include <vector>

// Standard normal cumulative distribution function
double norm_cdf(double x);

// Standard normal probability density function
double norm_pdf(double x);

class BlackScholesCalculator {
 public:
  struct OptionResult {
    double call_price;
    double put_price;
    double delta;
    double gamma;
    double theta;
    double vega;
    double rho;
  };

  static OptionResult calculate(double S, double K, double T, double r, double sigma);
};

class ImpliedVolatilityCalculator {
 public:
  static double calculate(double S, double K, double T, double r, double market_price,
                          bool is_call = true);
};

class PortfolioAnalyzer {
 public:
  struct Position {
    double quantity;
    double strike;
    double expiry;
    bool is_call;
    double market_price;
  };

  struct PortfolioGreeks {
    double total_delta;
    double total_gamma;
    double total_theta;
    double total_vega;
    double total_rho;
    double portfolio_value;
  };

  static PortfolioGreeks analyze(double spot_price, double risk_free_rate,
                                 const std::vector<Position>& positions);
};

// Monte Carlo simulation for exotic options
class MonteCarloEngine {
 public:
  static double simulate_asian_option(double S0, double K, double T, double r, double sigma,
                                      int num_paths, int num_steps, bool is_call = true);
};
