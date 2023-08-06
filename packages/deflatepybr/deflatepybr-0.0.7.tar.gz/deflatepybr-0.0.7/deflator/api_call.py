import requests
import pandas as pd
import sys


def api_call(series: str) -> pd.DataFrame:
    """
    A function that return historical values for Brazil's IPCA (Broad Consumers Price Index) in a Pandas.DataFrame format.

    Params:
        series -> specifies the type of values wanted.
            if monthly values are desided, then series='monthly'
            otherwise series='yearly'
    """
    base_url = "http://www.ipeadata.gov.br/api/odata4/Metadados"
    series_dict = {"yearly": "('PRECOS_IPCAG')", "monthly": "('PRECOS12_IPCAG12')"}
    series_type = ""
    if series == "yearly":
        series_type = series_dict["yearly"]
    elif series == "monthly":
        series_type = series_dict["monthly"]
    else:
        print("Incorrect value. Series arguments must be either 'yearly' or 'monthly'.")
        sys.exit(1)
    complete_url = f"{base_url}{series_type}" + "/Valores"
    data = requests.get(complete_url)
    if data.status_code == requests.codes.ok:
        data = data.json()
        if "value" in data:
            try:
                data = pd.DataFrame(data["value"])
                data = data[["SERCODIGO", "VALDATA", "VALVALOR"]]
                data = data.rename(
                    {"SERCODIGO": "series", "VALDATA": "date", "VALVALOR": "ipca"},
                    axis=1,
                )
                data["date"] = pd.to_datetime(
                    data["date"].apply(pd.to_datetime), utc=True, format="%Y-%m-%d"
                )
                return data
            except Exception:
                return None


if __name__ == "__main__":
    api_call()
