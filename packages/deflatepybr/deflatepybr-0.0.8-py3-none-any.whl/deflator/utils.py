def str_to_float(x):
    if type(x) == float:
        return x
    return float(x.replace(".", "x").replace(",", ".").replace("x", ""))


if __name__ == "__main__":
    str_to_float()
