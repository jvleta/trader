# Options Trading Learning Tool - Client App

A React TypeScript application built with Vite for learning options trading. This client app provides an intuitive interface to select stock symbols and view relevant market data.

## Features

- **Stock Symbol Selection**: Choose from popular stocks like AAPL, QQQ, NVIDIA, Microsoft, Google, Tesla, SPY, and AMD
- **Real-time Data Table**: View key stock information including:
  - Current price
  - Price change and percentage change
  - Trading volume
  - Market capitalization
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, professional interface suitable for trading applications

## Getting Started

### Prerequisites

- Node.js 20.19+ or 22.12+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/
│   └── OptionsTrader.tsx    # Main trading interface component
├── App.tsx                  # Root application component
├── App.css                  # Application styles
└── main.tsx                 # Application entry point
```

## Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and development server
- **CSS3** - Styling

## Data Source

Currently uses mock data for demonstration purposes. In a production environment, this would be connected to:
- Real-time market data APIs (Alpha Vantage, Yahoo Finance, etc.)
- Options data providers
- Backend services for user portfolio management

## Technical Details

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:
- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Contributing

This is part of a larger options trading learning tool project. See the main repository for contribution guidelines.

## License

This project is for educational purposes.
