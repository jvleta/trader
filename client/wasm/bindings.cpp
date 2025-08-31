#include <emscripten/bind.h>

#include "options_calculator.h"

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
