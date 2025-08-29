#include <emscripten/bind.h>
#include <cmath>
#include <vector>
#include <algorithm>

// Standard normal cumulative distribution function
double norm_cdf(double x) {
    return 0.5 * std::erfc(-x * M_SQRT1_2);
}

// Standard normal probability density function
double norm_pdf(double x) {
    return (1.0 / std::sqrt(2.0 * M_PI)) * std::exp(-0.5 * x * x);
}

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
    
    static OptionResult calculate(double S, double K, double T, double r, double sigma) {
        OptionResult result;
        
        // Calculate d1 and d2
        double d1 = (std::log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * std::sqrt(T));
        double d2 = d1 - sigma * std::sqrt(T);
        
        // Calculate option prices
        result.call_price = S * norm_cdf(d1) - K * std::exp(-r * T) * norm_cdf(d2);
        result.put_price = K * std::exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1);
        
        // Calculate Greeks
        result.delta = norm_cdf(d1);  // Call delta (put delta = delta - 1)
        result.gamma = norm_pdf(d1) / (S * sigma * std::sqrt(T));
        result.theta = -(S * norm_pdf(d1) * sigma) / (2 * std::sqrt(T)) - r * K * std::exp(-r * T) * norm_cdf(d2);
        result.vega = S * norm_pdf(d1) * std::sqrt(T);
        result.rho = K * T * std::exp(-r * T) * norm_cdf(d2);
        
        return result;
    }
};

class ImpliedVolatilityCalculator {
public:
    static double calculate(double S, double K, double T, double r, double market_price, bool is_call = true) {
        double vol_low = 0.01;
        double vol_high = 5.0;
        double vol_mid;
        double price_mid;
        double tolerance = 1e-6;
        int max_iterations = 100;
        
        for (int i = 0; i < max_iterations; ++i) {
            vol_mid = (vol_low + vol_high) / 2.0;
            
            auto result = BlackScholesCalculator::calculate(S, K, T, r, vol_mid);
            price_mid = is_call ? result.call_price : result.put_price;
            
            if (std::abs(price_mid - market_price) < tolerance) {
                return vol_mid;
            }
            
            if (price_mid < market_price) {
                vol_low = vol_mid;
            } else {
                vol_high = vol_mid;
            }
        }
        
        return vol_mid;
    }
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
                                 const std::vector<Position>& positions) {
        PortfolioGreeks portfolio;
        portfolio.total_delta = 0.0;
        portfolio.total_gamma = 0.0;
        portfolio.total_theta = 0.0;
        portfolio.total_vega = 0.0;
        portfolio.total_rho = 0.0;
        portfolio.portfolio_value = 0.0;
        
        for (const auto& pos : positions) {
            // Calculate implied volatility from market price
            double iv = ImpliedVolatilityCalculator::calculate(
                spot_price, pos.strike, pos.expiry, risk_free_rate, 
                pos.market_price, pos.is_call
            );
            
            // Calculate option metrics
            auto result = BlackScholesCalculator::calculate(
                spot_price, pos.strike, pos.expiry, risk_free_rate, iv
            );
            
            // Adjust for put options
            double delta = pos.is_call ? result.delta : result.delta - 1.0;
            double theta = pos.is_call ? result.theta : result.theta + risk_free_rate * pos.strike * std::exp(-risk_free_rate * pos.expiry);
            
            // Accumulate portfolio Greeks
            portfolio.total_delta += pos.quantity * delta;
            portfolio.total_gamma += pos.quantity * result.gamma;
            portfolio.total_theta += pos.quantity * theta;
            portfolio.total_vega += pos.quantity * result.vega;
            portfolio.total_rho += pos.quantity * result.rho;
            portfolio.portfolio_value += pos.quantity * pos.market_price;
        }
        
        return portfolio;
    }
};

// Monte Carlo simulation for exotic options
class MonteCarloEngine {
public:
    static double simulate_asian_option(double S0, double K, double T, double r, double sigma, 
                                      int num_paths, int num_steps, bool is_call = true) {
        double dt = T / num_steps;
        double drift = (r - 0.5 * sigma * sigma) * dt;
        double vol_sqrt_dt = sigma * std::sqrt(dt);
        double payoff_sum = 0.0;
        
        // Simple linear congruential generator for random numbers
        unsigned int seed = 12345;
        
        for (int path = 0; path < num_paths; ++path) {
            double S = S0;
            double sum_prices = 0.0;
            
            for (int step = 0; step < num_steps; ++step) {
                // Generate pseudo-random normal variable (Box-Muller transform)
                seed = seed * 1664525 + 1013904223;
                double u1 = (seed & 0x7FFFFFFF) / double(0x7FFFFFFF);
                seed = seed * 1664525 + 1013904223;
                double u2 = (seed & 0x7FFFFFFF) / double(0x7FFFFFFF);
                
                double z = std::sqrt(-2.0 * std::log(u1)) * std::cos(2.0 * M_PI * u2);
                
                S *= std::exp(drift + vol_sqrt_dt * z);
                sum_prices += S;
            }
            
            double avg_price = sum_prices / num_steps;
            double payoff = is_call ? std::max(avg_price - K, 0.0) : std::max(K - avg_price, 0.0);
            payoff_sum += payoff;
        }
        
        return std::exp(-r * T) * (payoff_sum / num_paths);
    }
};

// Emscripten bindings
EMSCRIPTEN_BINDINGS(options_module) {
    emscripten::value_object<BlackScholesCalculator::OptionResult>("OptionResult")
        .field("call_price", &BlackScholesCalculator::OptionResult::call_price)
        .field("put_price", &BlackScholesCalculator::OptionResult::put_price)
        .field("delta", &BlackScholesCalculator::OptionResult::delta)
        .field("gamma", &BlackScholesCalculator::OptionResult::gamma)
        .field("theta", &BlackScholesCalculator::OptionResult::theta)
        .field("vega", &BlackScholesCalculator::OptionResult::vega)
        .field("rho", &BlackScholesCalculator::OptionResult::rho);
    
    emscripten::value_object<PortfolioAnalyzer::Position>("Position")
        .field("quantity", &PortfolioAnalyzer::Position::quantity)
        .field("strike", &PortfolioAnalyzer::Position::strike)
        .field("expiry", &PortfolioAnalyzer::Position::expiry)
        .field("is_call", &PortfolioAnalyzer::Position::is_call)
        .field("market_price", &PortfolioAnalyzer::Position::market_price);
    
    emscripten::value_object<PortfolioAnalyzer::PortfolioGreeks>("PortfolioGreeks")
        .field("total_delta", &PortfolioAnalyzer::PortfolioGreeks::total_delta)
        .field("total_gamma", &PortfolioAnalyzer::PortfolioGreeks::total_gamma)
        .field("total_theta", &PortfolioAnalyzer::PortfolioGreeks::total_theta)
        .field("total_vega", &PortfolioAnalyzer::PortfolioGreeks::total_vega)
        .field("total_rho", &PortfolioAnalyzer::PortfolioGreeks::total_rho)
        .field("portfolio_value", &PortfolioAnalyzer::PortfolioGreeks::portfolio_value);
    
    emscripten::register_vector<PortfolioAnalyzer::Position>("PositionVector");
    
    emscripten::class_<BlackScholesCalculator>("BlackScholesCalculator")
        .class_function("calculate", &BlackScholesCalculator::calculate);
    
    emscripten::class_<ImpliedVolatilityCalculator>("ImpliedVolatilityCalculator")
        .class_function("calculate", &ImpliedVolatilityCalculator::calculate);
    
    emscripten::class_<PortfolioAnalyzer>("PortfolioAnalyzer")
        .class_function("analyze", &PortfolioAnalyzer::analyze);
    
    emscripten::class_<MonteCarloEngine>("MonteCarloEngine")
        .class_function("simulate_asian_option", &MonteCarloEngine::simulate_asian_option);
}
