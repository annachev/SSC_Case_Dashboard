# Philips Supplier Sustainability - Threshold Decision Dashboard

An interactive Streamlit dashboard for MBA students to explore trade-offs between cost, risk, and fairness when choosing a sustainability assessment threshold.

## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Local Installation

1. Clone or download this repository

2. Navigate to the project directory:
   ```bash
   cd philips-threshold-dashboard
   ```

3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

6. Open your browser to `http://localhost:8501`

## Deployment to Streamlit Cloud

1. Push this repository to GitHub

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Click "New app"

4. Connect your GitHub account and select this repository

5. Set the main file path to `app.py`

6. Click "Deploy"

Your app will be available at `https://[your-app-name].streamlit.app`

## Project Context

This dashboard accompanies an MBA case study about Philips' supplier sustainability assessment program. Sarah Chen, VP of Sustainable Supply Chain, must decide what probability threshold to use for flagging suppliers for sustainability review.

**The core dilemma:**
- A **lower threshold** (e.g., 0.50) flags more suppliers, catching more problems but costing more
- A **higher threshold** (e.g., 0.70) flags fewer suppliers, saving money but missing more risks

Students use this dashboard to explore how different thresholds affect:
- Cost (annual review budget)
- Risk (false negatives - missed problematic suppliers)
- Fairness (geographic disparity in flagging rates)
- Stakeholder alignment (CFO vs. CSO vs. Supplier Relations)

## File Structure

```
philips-threshold-dashboard/
├── app.py                      # Main Streamlit application
├── data/
│   ├── __init__.py
│   └── exhibits.py             # Hardcoded case data from exhibits
├── utils/
│   ├── __init__.py
│   ├── calculations.py         # Metric calculations & interpolation
│   └── visualizations.py       # Plotly chart functions
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Philips branding configuration
└── README.md                   # This file
```

### File Descriptions

- **app.py**: Main entry point. Contains the Streamlit UI layout, page structure, and orchestrates all dashboard components.

- **data/exhibits.py**: Contains all hardcoded data from the case exhibits including threshold metrics, geographic fairness data, and sample sizes.

- **utils/calculations.py**: Business logic for metric calculations, including linear interpolation for non-standard thresholds and stakeholder score formulas.

- **utils/visualizations.py**: Plotly chart generation functions for the cost-risk scatter plot and geographic fairness bar chart.

- **.streamlit/config.toml**: Streamlit configuration including Philips brand colors (dark blue #0E1C36, light blue #00629B).

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.31.0 | Web application framework |
| plotly | 5.18.0 | Interactive chart visualizations |
| pandas | 2.1.4 | Data manipulation (minimal use) |
| numpy | 1.26.3 | Numerical calculations |

## Features

### 1. Threshold Selector
- Slider from 0.45 to 0.75 with 0.01 step size
- Quick-select buttons for CFO (0.50), Balanced (0.60), and CSO (0.70) preferences
- Warning message for interpolated (non-standard) thresholds

### 2. Key Metrics Cards
- Suppliers Flagged (count and percentage)
- Annual Cost ($M)
- False Positives (good suppliers incorrectly flagged)
- False Negatives (problematic suppliers missed)

### 3. Cost vs. Risk Chart
- Scatter plot showing trade-off frontier
- All standard thresholds plotted
- Selected threshold highlighted

### 4. Geographic Fairness Chart
- Horizontal bar chart by region (China, India, Other)
- Shows flagging rates at different thresholds
- Sample size warnings for small groups

### 5. Stakeholder Scorecard
- Scores (0-10) for CFO, CSO, Supplier Relations, and Fairness perspectives
- Color-coded progress bars
- Overall balance score
- Tip suggesting optimal balanced threshold

### 6. Discussion Questions
- Expandable section with case discussion prompts

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'data'"**
- Make sure you're running from the project root directory
- Run `streamlit run app.py` (not `python app.py`)

**Charts not displaying**
- Clear browser cache and refresh
- Check browser console for JavaScript errors
- Ensure Plotly is properly installed

**Slider not responding**
- This can happen with browser extensions blocking JavaScript
- Try a different browser or incognito mode

**Colors look wrong**
- Clear Streamlit cache: `streamlit cache clear`
- Delete `.streamlit/cache` folder if it exists

### Performance Issues

If the dashboard is slow:
1. Ensure you're running Python 3.10+
2. Check that all dependencies are the correct versions
3. Close other browser tabs to free up memory

## Customization

### Changing Colors
Edit `.streamlit/config.toml` to modify the color scheme:
```toml
[theme]
primaryColor = "#00629B"      # Accent color
backgroundColor = "#FFFFFF"    # Main background
secondaryBackgroundColor = "#F0F0F0"  # Card backgrounds
textColor = "#0E1C36"         # Main text color
```

### Modifying Data
Edit `data/exhibits.py` to change the underlying case data. All data is stored in Python dictionaries and can be easily modified.

### Adding New Thresholds
Add new entries to the `THRESHOLDS` dictionary in `data/exhibits.py`. The interpolation logic will automatically handle values between standard thresholds.

## License

This dashboard is provided for educational purposes as part of an MBA case study. All data is fictional and based on case exhibits.
