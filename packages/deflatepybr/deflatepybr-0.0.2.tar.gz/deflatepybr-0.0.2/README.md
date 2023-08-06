# Python brazilian currency deflator

A simple python package to deflate historical yearly or monthly values using IPCA (Consumers Broad Price Index).

Throught IPEA Data's API the function gather historical IPCA indexes and then deflate the values passed as a dataframe.

### How to use it:

- You need `pandas` and `requests` packages installed in your environment ( `python -m pip install pandas requests`).
- Install the package (`pip install deflatepybr`)
- Then `import deflator` -> `deflator.deflate(args)` **or** `from deflator import deflate` directly.

The function takes 5 arguments:
- `data_frame`: A `Pandas.DataFrame` with the data;
- `value_column`(str): A column containing the values to deflate;
- `date_column`(str): Column name from `data_frame` with the date range;
- `deflate_year`(int): Year that you wanna deflate the series to;
- `deflate_month`(int),optional: Month to deflate if you're doing monthly operations.

If only `deflate_year` is passed, the functions assumes that `date_column`contains **integer** values (2000,2008, etc). Otherwise the function assumes that `date_column` is **object** type (2000-12, 2008-10, etc).

Use cases can be found in the `example.ipynb` jupyter file available on the project's Github.
