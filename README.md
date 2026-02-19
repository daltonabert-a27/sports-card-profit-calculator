# Sports Card Profit Calculator & Deal Analyzer

A desktop application for sports card single resellers to calculate profit, analyze deals, compare eBay sold prices, and track ROI.

## Features

- **Profit Calculator** - Calculate net profit factoring in eBay fees (13.25% FVF), shipping, grading costs, and Illinois sales tax
- **Deal Analyzer** - Compare offers against your cost basis to see NOI and net profit % per card
- **eBay Sold Comps** - Search active eBay listings and manually log sold prices for comparison
- **Break-even Analysis** - Determine when grading (PSA, BGS, SGC, CGC) becomes profitable vs selling raw
- **ROI Tracking** - Log purchases and sales, track cumulative portfolio ROI
- **CSV Export** - Export any dataset for spreadsheet analysis

## Setup

```bash
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python main.py
```

## Fee Structure (2025-2026)

| Component | Rate |
|---|---|
| eBay Final Value Fee (Trading Cards) | 13.25% on total (item + shipping) |
| eBay Per-Order Fee | $0.30 (orders <= $10) / $0.40 (orders > $10) |
| International Fee | Additional 1.65% |
| eBay Standard Envelope (1oz) | ~$0.56 |
| USPS Ground Advantage (4oz commercial) | ~$4.63 |

All rates are configurable in the Settings tab.
