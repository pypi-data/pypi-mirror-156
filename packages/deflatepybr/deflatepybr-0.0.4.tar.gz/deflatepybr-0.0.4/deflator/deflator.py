import pandas as pd
import sys
from datetime import datetime
from deflator.api_call import api_call
from deflator.utils import str_to_float


def deflate(
    data_frame: pd.DataFrame,
    value_column: str,
    date_column,
    deflate_year=None,
    deflate_month=None,
):
    series = ""
    target_date = None
    if not date_column:
        return print(f"The date_column argument must be specified!")
    if not value_column:
        return print(f"You must especify the column to be deflated.")
    if not deflate_year:
        return print(f"At least the deflate_year argument must be specified!")
    if not deflate_month:
        series = "yearly"
        date_format = "%Y"
        target_date = int(
            pd.to_datetime(datetime(deflate_year, 1, 1)).strftime(date_format)
        )
        conversion_type = "int"
    else:
        series = "monthly"
        date_format = "%Y-%m"
        target_date = pd.to_datetime(datetime(deflate_year, deflate_month, 1)).strftime(
            date_format
        )
        conversion_type = "object"

    try:
        data_frame[date_column] = (
            pd.to_datetime(data_frame[date_column])
            .dt.strftime(date_format)
            .astype(conversion_type)
        )
    except Exception as error:
        return print(
            f"Não foi possível converter a coluna {date_column} para um formato de data. Detalhes do erro: \n {error}"
        )

    try:
        data_frame[value_column] = data_frame[value_column].apply(str_to_float)
    except Exception as error:
        return print(f"{error}")

    ipca_values = api_call(series=series)

    ipca_values = ipca_values[["date", "ipca"]]

    ipca_values["date"] = (
        ipca_values["date"].dt.strftime(date_format).astype(conversion_type)
    )
    temp_df = pd.merge(
        left=data_frame,
        right=ipca_values,
        left_on=date_column,
        right_on="date",
        how="left",
    )

    deflator = temp_df.loc[temp_df["date"] == target_date]["ipca"].squeeze()

    temp_df["deflated_value"] = temp_df[value_column] * (
        deflator / temp_df["ipca"].squeeze()
    )

    data_frame["deflated_value"] = temp_df["deflated_value"]
    return data_frame


if __name__ == "__main__":
    deflate()
