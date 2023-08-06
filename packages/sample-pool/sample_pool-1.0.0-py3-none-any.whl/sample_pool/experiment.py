import pandas as pd


class Experiment:
    def __init__(self, df: pd.DataFrame, sample_list: list[str]):
        self.df = df
        self.sample_list = sample_list

    def calculate_sum(self, minimum_good_samples=10):
        df = self.df.copy()
        sample_number = len(self.sample_list)
        max_nan_number = sample_number - minimum_good_samples
        df_filter_nan = df[self.sample_list].dropna(thresh=max_nan_number)
        for i, r in df_filter_nan.iterrows():
            average = r.mean(skipna=True)
            for c in r.index:
                df_filter_nan.at[i, c] = r[c]/average
        sum_new_df = df_filter_nan.sum(axis=0)
        return sum_new_df

    def get_aliquot_size(self, based_on_sample="", minimum_good_samples=10):
        s = self.calculate_sum(minimum_good_samples)
        if based_on_sample == "":
            based_on_sample = s[s == s.min()].index[0]
        res = {}
        for i in s.index:
            res[i] = s[based_on_sample] / s[i]
        return res
