from ..numerical_libs import sync_numerical_libs, xp, xp_sparse
from .spline_smooth import lin_reg, ridge
from .array_utils import rolling_window
from .power_transforms import YeoJohnson

def gaussian_kernel(x, tau):
    x_outer_diff = x[:,:, None] - x[:, None, :]
    x_normed_outer_diff = x_outer_diff / xp.max(x_outer_diff, axis=(1,2), keepdims=True)
    numer = xp.einsum('ijk,ikj->ijk', x_normed_outer_diff,x_normed_outer_diff)
    w = xp.exp(numer/(2* tau* tau))
    return w

def tricubic_kernel(x, f=1./8.):
    x_outer_diff = x[:,:, None] - x[:, None, :]
    x_normed_outer_diff = x_outer_diff / xp.max(f*x_outer_diff, axis=(1,2), keepdims=True)
    w = (1. - xp.abs(x_normed_outer_diff)**3)**3
    return xp.clip(w, a_min=0., a_max=None)

@sync_numerical_libs
def loess(y, x=None, tau=.05, iters=1, degree=2, q=None, data_w=None):

    if x is None:
        x = xp.arange(0, y.shape[1], dtype=float)
        x = xp.tile(x, (y.shape[0], 1))

    y_min = xp.min(y, axis=1, keepdims=True)
    y_max = xp.max(y, axis=1, keepdims=True)
    y_range = y_max - y_min + 1e-8
    y_norm = (y - y_min) / y_range

    #w = tricubic_kernel(x)

    if q is not None:
        h = [xp.sort(xp.abs(x - x[:,i][:,None]),axis=1)[:,q] for i in range(x.shape[1])]
        h = xp.stack(h).T
        #from IPython import embed
        #embed()
        # TODO double check this h term, should it be h[...,None,:]?
        w = xp.clip(xp.abs((x[:,:, None] - x[:, None, :]) / h[...,None]), a_min=0.0, a_max=1.0)
        w = (1. - w**3)**3
    else:
        w = gaussian_kernel(x, tau)

    from IPython import embed
    #embed()

    if data_w is not None:
        iters=1
        delta=data_w
    else:
        delta = xp.ones_like(y)

    out = xp.empty_like(y)

    for _ in range(iters):

        # TODO we can get rid of the for loop with a reshape into the batch dim...
        for i in range(y.shape[1]):
            out[:,i] = lin_reg(y_norm,x, w=delta*w[:,i], alp=.6, degree=degree)[:,i]

        res = y- out
        stddev = xp.quantile(xp.abs(res), axis=1, q=0.682)
        res_star = res / (6.0 * xp.median(xp.abs(res), axis=1, keepdims=True) + 1.e-8)
        clean_resid =res_star
        #clean_resid = xp.clip(res / (6.0 * stddev[:, None] + 1e-8), -1.0, 1.0)
        robust_weights = xp.clip(1.0 - clean_resid**2.0, 0.0, 1.0) ** 2.0
        delta = robust_weights

    out = out * y_range + y_min
    if xp.any(xp.isnan(out)).item():
        embed()
    '''
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt

    from IPython import embed
    embed()

    for i in range(y.shape[0]):
        #plt.plot(xp.to_cpu(y[i]))
        #plt.plot(xp.to_cpu(out[i]))
        plt.plot(xp.to_cpu((y[i]-out[i])/y[i]))
        plt.show()
    '''
    return out

def low_pass_filter(arr, np, nl):
    # TODO nl should default to the smallest odd int > seasonality
    from IPython import embed
    #embed()
    ret = xp.mean(rolling_window(arr, np, axis=1),axis=-1)
    ret = xp.mean(rolling_window(ret, np, axis=1),axis=-1)
    ret = xp.mean(rolling_window(ret, 3, axis=1),axis=-1) # TODO once we extend the array this needs pad=False
    ret = loess(ret, degree=1, iters=1, q=nl)
    if xp.any(xp.isnan(ret)).item():
        embed()
    return ret

@sync_numerical_libs
def STL(y, x=None, ns=7, np=7, nl=9, nt=25, ni=1, no=10, log=False):
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from IPython import embed

    # TODO handle x

    # TODO this should be a general box-cox
    if log:
        power_transform = YeoJohnson()
        y = power_transform.fit(y)
        #y = xp.log1p(y)

    trend = xp.zeros_like(y)
    resid = xp.zeros_like(y)
    n_seasons = int(y.shape[1]//np)

    rho = xp.ones_like(y)
    for _ in range(no):

        for _ in range(ni):
            detrended = y-trend
            #embed()
            # TODO handle case when y.shape[1]/seasonality isn't an int
            cycle_subseries = detrended.reshape(y.shape[0], -1, np)
            batched_cycle_subseries = xp.swapaxes(cycle_subseries,1,2).reshape(-1, n_seasons)
            #embed()
            batched_rho = xp.swapaxes(rho.reshape(y.shape[0], -1, np),1,2).reshape(-1, n_seasons)
            smoothed_subseries = loess(batched_cycle_subseries, degree=1, q=ns, data_w=batched_rho) #TODO this should extend beyond the original x, need to out a param like x_out to lin_reg and loess for that...
            #embed()
            smoothed_subseries = smoothed_subseries.reshape((y.shape[0],np,n_seasons))
            smoothed_subseries = xp.swapaxes(smoothed_subseries, 1,2).reshape(y.shape[0], -1)

            filtered_subseries = low_pass_filter(smoothed_subseries, np, nl)
            seasonality = smoothed_subseries - filtered_subseries
            #seasonality = detrended_subseries.reshape((y.shape[0],np,n_seasons))
            #seasonality = xp.swapaxes(seasonality, 1,2).reshape(y.shape[0], -1)
            deseasoned = y - seasonality 
            trend = loess(deseasoned, degree=1, q=nt, data_w=rho)

        resid = deseasoned - trend
        scaled_resid = xp.abs(resid)/(6.*xp.median(resid, axis=1, keepdims=True)+1.e-8)
        rho = xp.clip((1. - scaled_resid**2)**2, a_min=1.e-8, a_max=None)

    #embed()

    if log:
        y = power_transform.inv(y)
        seasonality = power_transform.inv(seasonality)
        trend = power_transform.inv(trend)
        resid = power_transform.inv(resid)
        #y = xp.exp(y) - 1.
        #seasonality = xp.exp(seasonality) - 1.
        #trend = xp.exp(trend) - 1.
        #resid = xp.exp(resid) - 1.

    for i in range(y.shape[0]):
        #plt.plot(xp.to_cpu(y[i]))
        #plt.plot(xp.to_cpu(trend[i]+seasonality[i]))
        #plt.show()
        fig, axs = plt.subplots(4, 1)

        axs[0].plot(xp.to_cpu(y[i]))
        axs[0].plot(xp.to_cpu(trend[i]+seasonality[i]))
        axs[1].plot(xp.to_cpu(y[i]))
        axs[1].plot(xp.to_cpu(trend[i]))
        axs[2].plot(xp.to_cpu(seasonality[i]))
        axs[3].plot(xp.to_cpu(resid[i]))
        plt.show()

