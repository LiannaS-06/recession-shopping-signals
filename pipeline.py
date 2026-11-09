import io
import zipfile
import pandas as pd
import requests

NAICS = "North American Industry Classification System (NAICS)"
CATEGORIES = {
    "health": "Health and personal care retailers [456]",
    "clothing": "Clothing and clothing accessories retailers [4581]",
    "cars": "Motor vehicle and parts dealers [441]",
}


def run_pipeline():
    # 1. Fetch the newest StatCan table
    info = requests.get("https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/20100056/en").json()
    z = zipfile.ZipFile(io.BytesIO(requests.get(info["object"]).content))
    full = pd.read_csv(z.open("20100056.csv"), low_memory=False)

    results = []
    for name, label in CATEGORIES.items():
        # 2. Pull 2017+ from the API and glue on the fixed history
        recent = full[(full["GEO"] == "Canada") & (full[NAICS] == label) &
                      (full["Sales"] == "Total retail sales") & (full["Adjustments"] == "Unadjusted")]
        recent = recent[["REF_DATE", "VALUE"]].rename(columns={"REF_DATE": "month", "VALUE": "sales"})
        recent["month"] = pd.to_datetime(recent["month"])
        hist = pd.read_csv("hist_" + name + ".csv", parse_dates=["month"])
        sales = pd.concat([hist, recent]).set_index("month")["sales"]

        # 3. Nowcast the next 2 months with guess C and C2
        last = sales.index.max()
        back = lambda k: sales[last - pd.DateOffset(months=k)]
        results.append({"category": name, "month": last + pd.DateOffset(months=1),
                        "nowcast": sales[last] * back(11) / back(12), "latest_published": last})
        results.append({"category": name, "month": last + pd.DateOffset(months=2),
                        "nowcast": sales[last] * back(10) / back(12), "latest_published": last})

    # 4. Save the results
    out = pd.DataFrame(results)
    out.to_csv("nowcasts.csv", index=False)
    return out


if __name__ == "__main__":
    print(run_pipeline())
