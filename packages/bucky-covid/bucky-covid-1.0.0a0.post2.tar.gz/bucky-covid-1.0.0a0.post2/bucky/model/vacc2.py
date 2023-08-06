import pandas as pd

from ..numerical_libs import sync_numerical_libs, xp
from ..util.loess import loess
from cupyx.scipy import signal # TODO add to xp?

from IPython import embed
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

@sync_numerical_libs
def gamma_pdf(x, shape, scale):
    scale = xp.array(scale, dtype=float)
    shape = xp.array(shape, dtype=float)
    return 1.0 / (xp.special.gamma(shape) * scale ** shape) * x ** (shape - 1) * xp.exp(-x / scale)


@sync_numerical_libs
def read_vac(adm_mapping):

    df = pd.read_csv('data/raw/vaccine_timeseries/vacc-timeseries.csv')

    df["date"] = pd.to_datetime(df.Date)

    adm1_abbr_map = adm_mapping.mapping('abbr','id', level=1)
    df['adm1'] = df.Location.map(adm1_abbr_map)
    # Found unknown states df.loc[df['adm1'].isna()].LongName

    df = df.loc[~df['adm1'].isna()]
    df['adm1'] = df['adm1'].astype(int)

    df = df.set_index(['adm1', 'date'])


    #df = df.fillna(0)


    columns_to_keep = ['Series_Complete_Yes', 'additional_doses', 'Second_Booster']
    age_columns = ('Series_Complete', 'Additional_Doses', 'Second_Booster')
    age_groups = ('65Plus', '18Plus', '12Plus', '5Plus', '65plus')

    for col in age_columns:
        for age in age_groups:
            col_name = f"{col}_{age}"
            columns_to_keep.append(col_name)

    col_mask = df.columns.isin(columns_to_keep)
    df = df[df.columns[col_mask]]

    new_col_names = ('vaccinated', 'boosted', 'double_boosted')
    new_age_groups = ("0-4", "5-11", "12-17", "18-64", "65+")

    new_df = pd.DataFrame(index=df.index, columns=pd.MultiIndex.from_product([new_col_names, new_age_groups], names=['status', 'age']))#.fillna(0)

    # 65+
    new_df["vaccinated", "65+"] = df['Series_Complete_65Plus']
    new_df["boosted", "65+"] = df['Additional_Doses_65Plus']
    new_df["double_boosted", "65+"] = df['Second_Booster_65plus']

    # 18-64
    new_df["vaccinated", "18-64"] = df['Series_Complete_18Plus'] - df['Series_Complete_65Plus']
    new_df["boosted", "18-64"] = df['Additional_Doses_18Plus'] - df['Additional_Doses_65Plus']
    new_df["double_boosted", "18-64"] = df['Second_Booster'] - df['Second_Booster_65plus']

    # 12-17
    new_df["vaccinated", "12-17"] = df['Series_Complete_12Plus'] - df['Series_Complete_18Plus']
    new_df["boosted", "12-17"] = df['Additional_Doses_12Plus'] - df['Additional_Doses_18Plus']

    # 5-11
    new_df["vaccinated", "5-11"] = df['Series_Complete_5Plus'] - df['Series_Complete_12Plus']

    # 0-4
    new_df["vaccinated", "0-4"] = df['Series_Complete_Yes'] - df['Series_Complete_5Plus']


    #first_date = new_df.index.get_level_values(1).min()
    #new_df = new_df.mask(new_df.ffill().isnull(), 0)
    #embed()
    #new_df.loc[new_df.index.get_level_values(1) == first_date] = 0

    # TODO we should set the 0 date based on when it was authorized for each age/status then fillna 0's before that...

    # interp missing values
    new_df=new_df.unstack(0)
    new_df = new_df.interpolate(limit_direction='forward',limit_area='inside',axis=0)
    # 0 out the remaining cols (like boosters for kids)
    new_df = new_df.fillna(0)

    # clip negatives
    new_df = new_df.clip(lower=0)

    new_df = new_df.sort_index(axis=1)

    # make age an index
    #new_df = new_df.stack()
    stacked_df = new_df.T #unstack().stack([0,1])
    stacked_ts = xp.array(stacked_df.values)
    smoothed_ts = loess(stacked_ts)
    smoothed_ts = xp.clip(smoothed_ts, a_min=0, a_max=None)

    vac_rate = xp.gradient(smoothed_ts,edge_order=2, axis=1)

    mean_wane_time = 5*30.5
    waned_reduction = 1 #.5 # range: .4-.6
    waning_t_pdf = gamma_pdf(xp.arange(int(2*mean_wane_time)), 20.0, mean_wane_time / 20.0)
    waned_rate=signal.fftconvolve(vac_rate, waning_t_pdf[None,...], axes=1)
    waned = xp.cumsum(waned_rate, axis=1)
    
    waned = waned[:, :smoothed_ts.shape[1]]
    immune = smoothed_ts - waned_reduction*waned

    reshape_size = tuple([len(x) for x in stacked_df.index.levels])
    a=xp.reshape(immune, reshape_size + (-1,))

    embed()

    plt.plot(xp.to_cpu(xp.sum(a, axis=[0,2]).T), label=new_df.columns.get_level_values(1).unique())
    plt.legend()
    plt.show()

    embed()
