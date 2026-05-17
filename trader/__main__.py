import argparse
from . import screen
from .plots import plot_payoff

parser = argparse.ArgumentParser(prog="python -m trader", description="Options screening and payoff analysis.")
subparsers = parser.add_subparsers(dest="command", required=True)

screen_parser = subparsers.add_parser("screen", help="Screen top option contracts.")
screen_parser.add_argument("symbol", help="Underlying stock symbol.")
screen_parser.add_argument("--strategy", choices=["cc", "csp"], default="csp")
screen_parser.add_argument("--top-n", type=int, default=20, help="Rows to display (default: 20).")

plot_parser = subparsers.add_parser("plot", help="Plot payoff diagrams.")
plot_parser.add_argument("symbol", help="Underlying stock symbol.")
plot_parser.add_argument("--strategy", choices=["cc", "csp"], default="csp")
plot_parser.add_argument("--strike", type=float, default=None, help="Plot a specific strike price.")
plot_parser.add_argument("--top-n", type=int, default=5, help="Contracts to plot (default: 5).")

args = parser.parse_args()

if args.command == "screen":
    screen(args.symbol, strategy=args.strategy, top_n=args.top_n)
elif args.command == "plot":
    plot_payoff(args.symbol, strategy=args.strategy, strike=args.strike, top_n=args.top_n)
