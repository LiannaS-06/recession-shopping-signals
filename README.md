# Recession Shopping Signals

**Can Google searches predict Canadian retail spending before Statistics Canada publishes it?**

📊 **[Live dashboard](https://recession-shopping-signals-a2euappbno94eq4xqfrvtcu.streamlit.app/)** (updates automatically each month)

## The question

Statistics Canada publishes monthly retail sales about 7 weeks after each month ends. Google search data is available almost instantly. Inspired by Choi and Varian's *Predicting the Present with Google Trends*, plus two popular recession theories (the lipstick effect and the Hemline Index), I tested whether search data can "nowcast" Canadian spending on health and personal care, clothing, and cars before the official numbers come out.

## The finding

**A simple seasonal rule beat every search-based model, in all three categories, including through the 2008 recession.**

| Category | Seasonal rule error | Best Google model error |
|---|---|---|
| Health & personal care | 2.66% | 2.77% |
| Clothing | 7.43% | 7.72% |
| Cars | 6.93% | 7.00% |

*Average monthly error, walk-forward tested from 2008 to 2026.*

- Search signals were real but tiny: under 1% per 10-point change in searches
- The clearest signals were car-buying searches ("car loan", "used cars")
- No evidence of the lipstick effect in total health and personal care sales, and the Hemline Index pointed the wrong way
- In 2008, the model had never seen a recession to learn from, so it couldn't react to one
- The only hint of value was in 2009, a turning point, which fits Choi and Varian's finding that search data helps most when trends change

## How it works

**Data**
- Monthly retail sales from Statistics Canada (tables 20-10-0008-01 and 20-10-0056-01), January 2004 to present
- Google Trends (Canada) for 14 search terms and 2 search categories

**Cleaning and splicing**
- StatCan archived its older table in 2023 and reclassified businesses in the new one, so the two disagree (health about 4% apart, clothing about 17%)
- I spliced them into one 22-year series: one ratio at the splice point for health and cars (the gap drifted over time), and one ratio per calendar month for clothing (the gap had a strong seasonal pattern)
- Google changed its data collection in 2011, 2016 and 2022, so I removed those transition months from training. I also removed COVID and its echo (March 2020 to June 2022)

**Baseline**
- "Last month, adjusted by how that month changed last year." This handles both growth and seasonality, and cut errors by more than half compared with simpler guesses

**Model**
- Linear regression (and Ridge regression) predicting how far the baseline would miss, using year-over-year changes in search interest, smoothed over 3 months
- Search terms chosen by reasoning before testing, to avoid fitting to the test results

**Testing**
- Walk-forward validation: for every month from 2008 on, the model trained only on earlier months, then predicted that month. No future data was ever used
- Experiments were planned before running, and all results are reported, including the ones that didn't work

## Automation

`pipeline.py` fetches the newest data from the Statistics Canada Web Data Service, splices it onto the fixed history, and produces nowcasts for the next two months. A GitHub Actions workflow runs it on the 25th of every month and saves the results, which the dashboard reads.

Google Trends files are updated by hand each month, since there's no reliable free API (pytrends is archived and Google's official API is in limited alpha).

## Limitations

- StatCan's "health and personal care" includes pharmacies, so a lipstick effect could exist but be too small to see in the total
- The rescaled pre-2017 data is a best estimate, since the gap between StatCan's tables was still changing in 2017
- Google Trends rescales each download to 0 to 100, so values can shift between downloads

## Files

| File | What it is |
|---|---|
| `pipeline.py` | Fetches data and makes nowcasts |
| `app.py` | The Streamlit dashboard |
| `.github/workflows/monthly-nowcast.yml` | Runs the pipeline monthly |
| `hist_*.csv` | Fixed 2004 to 2016 sales history |
| `nowcasts.csv` | Latest nowcasts (updated automatically) |
| `chart_cars.csv` | Walk-forward results for the dashboard chart |

## Reference

Choi, H., & Varian, H. (2012). Predicting the Present with Google Trends. *Economic Record*, 88, 2 to 9.
