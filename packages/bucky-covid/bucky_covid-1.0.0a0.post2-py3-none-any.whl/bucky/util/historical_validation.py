import pandas as pd
import glob
from pathlib import Path
from collections import defaultdict
import tqdm

from .scoring import WIS
from ..numerical_libs import sync_numerical_libs, xp

from IPython import embed

@sync_numerical_libs
def evalu():

    truth_df = pd.read_csv('/data/bucky/covid19-forecast-hub/data-truth/truth-Incident Hospitalizations.csv')
    truth_df['date'] = pd.to_datetime(truth_df.date)
    truth_df['location'] = truth_df['location'].astype(str)
    #truth_df = truth_df.groupby([pd.Grouper(key="date", freq="W-Sat"), pd.Grouper(key='location')]).sum()
    truth_df= truth_df.set_index(['date','location'])

    total_wis = defaultdict(dict)
    for file in tqdm.tqdm(glob.glob('/data/bucky/covid19-forecast-hub/data-processed/*/2022-*.csv')):
        model_name = Path(file).name[11:][:-4]

        df = pd.read_csv(file)
        df = df[df.target.str.contains('inc hosp')]
        if df.empty: continue

        #from IPython import embed
        #embed()

        # drop past 4 weeks
        valid_targets = ("1 wk ahead inc case", "2 wk ahead inc case", "3 wk ahead inc case", "4 wk ahead inc case")
        valid_targets = ("4 wk ahead inc case",)
        valid_targets = [f'{i} day ahead inc hosp' for i in range(28)]
        df = df.loc[df.target.isin(valid_targets)]

        #embed()
        # drop points
        df = df.loc[df.type == 'quantile']

        df['target_end_date'] = pd.to_datetime(df['target_end_date'])
        df['location'] = df['location'].astype(str)

        #embed()
        forecast_date = str(df.target_end_date.min() - pd.Timedelta('5d')).split(' ')[0]

        total_wis[model_name][forecast_date] = 0.
        n_loc = 0.
        for group_index, group_df in df.groupby(['target_end_date', 'location']):
            location = group_index[1]
            if location == "US": continue
            #if int(location) < 999: continue
            try:
                truth = xp.atleast_1d(xp.array(truth_df.loc[group_index].value.item()))
                #print(truth)
            except:
                #embed()
                continue #embed()
            q = xp.array(group_df['quantile'].to_numpy()).T
            x_q = xp.atleast_2d(xp.array(group_df['value'].to_numpy())).T
            #embed()
            try:
                wis = WIS(truth, q.T, x_q)
            except:
                continue
            total_wis[model_name][forecast_date] += wis.item()
            n_loc += 1
        if n_loc == 0:
            del total_wis[model_name][forecast_date]
        else:
            total_wis[model_name][forecast_date] /= n_loc

            print(model_name, forecast_date, total_wis[model_name][forecast_date])

    wis_df = pd.DataFrame.from_dict(total_wis)


    embed()

    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    rank_df = wis_df.dropna(axis=1,how='all').rank(axis=1).T
    rank_df.T.plot()
    plt.show()
    embed()

