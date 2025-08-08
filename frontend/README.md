# NYC Transport Optimizer - Frontend

React frontend for comparing NYC transportation options.

## Folder Structure Explanation

```
src/
├── components/          # Reusable UI components
│   ├── TripInput/      # Origin/destination input form
│   ├── ResultsCard/    # Individual transport option cards
│   ├── PriceComparison/# Price comparison display
│   └── Loading/        # Loading states
├── pages/              # Route-level page components
│   ├── Home.js         # Main search page
│   └── Results.js      # Results comparison page
├── services/           # API communication
│   ├── api.js          # Backend API calls
│   ├── transport.js    # Transport comparison logic
│   └── deeplinks.js    # App deep linking logic
├── utils/              # Helper functions
│   ├── formatters.js   # Price/time formatting
│   ├── constants.js    # App constants
│   └── validators.js   # Input validation
├── hooks/              # Custom React hooks
│   ├── useRoutes.js    # Route fetching hook
│   └── usePricing.js   # Live pricing hook
├── context/            # React context providers
│   └── AppContext.js   # Global app state
└── App.js              # Main app component
```

## Setup

1. Copy `.env.example` to `.env`
2. Add your API keys
3. Run `npm install`
4. Run `npm start`