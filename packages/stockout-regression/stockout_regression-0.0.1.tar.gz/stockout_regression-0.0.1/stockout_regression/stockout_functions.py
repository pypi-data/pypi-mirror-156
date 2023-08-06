# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 23:36:04 2022

@author: FDN-Aysu
"""

def get_lapses(idp):
    # It generates list (lapses) of periods (tuples) where the product (idp) wasn't available considering last sale
    a = stock.loc[stock.product_id == idp, ['date', 'is_available']].set_index('date')
    b = sales.loc[sales.product_id == idp, ['order_datetime']].set_index('order_datetime')
    is_available = pd.concat([a,b]).sort_index().is_available

    lapses = []
    for n in range(len(is_available) - 1):
        if (is_available[n] == False) & (is_available[n-1] != False):      
            m = 1
            while (is_available[n+m] == False) & (n+m < len(is_available)-1):
                m = m + 1
            try:
                if is_available[n-1] == True:
                    lapses.append((is_available.index[n],is_available.index[n+m]))
                else :
                    lapses.append((is_available.index[n-1],is_available.index[n+m]))
            except:
                pass
    return(lapses)

def get_df_stock_day(lapses_x):
    # It generates data.frame of X stockout days that shows 
    # when the stockout starts, ends and how long the stock lasted (span), 
    # where the time is normalized from 0 (5:00:00 am) to 1 (4:59:59 am).
    anyday = datetime(1,1,1,0,0,0)
    stock_day = []
    for start, end in lapses_x:    
        start_5h = (start - pd.Timedelta(hours=5)) # when the stockout started
        end_5h = (end - pd.Timedelta(hours=5)) # when the stockout ended
        stock_first = (datetime.combine(anyday, start_5h.time()) - anyday).total_seconds() / (24*60*60) # prop of day with stock
        stock_last = (datetime.combine(anyday, end_5h.time()) - anyday).total_seconds() / (24*60*60) # prop of day with stock

        days = pd.date_range(start_5h.date(), end_5h.date(), freq='d') # stockout days
        ndays = len(days)
        if ndays == 1:
            stock_day.append(pd.DataFrame({'date_5h': days, 'span': stock_last - stock_first,
                                           'start': stock_first, 'end': stock_last}))
        else:
            stock_span = [stock_first] + [0]*(ndays-2) + [1-stock_last] # how long stock lasted for each day
            stock_start = [0]*(ndays-1) + [stock_last] # when stock started for each day
            stock_end = [stock_first] + [1]*(ndays-1) # when stock ended for each day
            stock_day.append(pd.DataFrame({'date_5h': days, 'span': stock_span, 'start': stock_start, 'end': stock_end}))

    stock_day = pd.concat(stock_day) # create data.frame of stockout days with start and length of stock time
    stock_day = (stock_day.sort_values(['date_5h', 'start']).groupby(['date_5h'])
                 .agg(start=('start','first'), end=('end','first'), span=('span', sum))
                 .reset_index())
    stock_day['span2'] = stock_day.span**2
    return(stock_day)

def get_list_stockout_y(lapses_y):
    # It generates a list of Y stockout days, where the day starts at 5:00:00 am and ends at 4:59:59 am.
    stockout_y = []
    for start, end in lapses_y:    
        start_5h = (start - pd.Timedelta(hours=5)) # when the stockout started
        end_5h = (end - pd.Timedelta(hours=5)) # when the stockout ended
        stockout_y = stockout_y + list(pd.date_range(start_5h.date(), end_5h.date(), freq='d')) # stockout days
    return(stockout_y)


def get_df_regress(df, idpy, idpx):
    # It generates a dataframe with all the regressors to implement the regressions
    oneprod = df.loc[df.product_id == idpy, ['order_datetime', 'sold_quantity']].sort_values(['order_datetime'])

    oneprod['order_datetime'] = oneprod.order_datetime - pd.Timedelta(hours=5) # to make day start at 5 am
    oneprod['date_5h'] = oneprod.order_datetime.dt.normalize() # save date
    oneprod['time_5h'] = oneprod.order_datetime.dt.time # save time
    oneprod['order_datetime'] = oneprod.order_datetime + pd.Timedelta(hours=5) # original order_datetime

    lapses_x = get_lapses(idpx) # information on stockout of X by date 
    stock_day = get_df_stock_day(lapses_x)
    oneprod = oneprod.merge(stock_day, how = 'left', on = 'date_5h', validate = 'many_to_one').fillna(0)

    lapses_y = get_lapses(idpy) # filter only when Y is in stock
    stockout_y = get_list_stockout_y(lapses_y)
    oneprod = oneprod.loc[~oneprod.date_5h.isin(stockout_y),]

    oneprod = oneprod.loc[oneprod.sold_quantity != 0,] # filter if any sale has 0 quantity
    oneprod['cumsales'] = oneprod.groupby('date_5h')['sold_quantity'].cumsum() # cumulative sales by date
    oneprod['lncumsales'] = np.log(oneprod.cumsales)

    onesout = [] # stockout_day and stockout_hour dummies
    for start, end in lapses_x:
        mini = oneprod[(oneprod.order_datetime > start) & (oneprod.order_datetime < end)]
        if len(mini.index) > 1:
            onesout.append(mini)
    try:
        onesout = pd.concat(onesout)
    except ValueError:
        print('no orders on product Y =',idpy,' during X =',idpx,'stockout')
        return ValueError
    
    oneprod['stockout_day'] = oneprod.date_5h.isin(onesout.date_5h)
    oneprod['stockout_hour'] = oneprod.order_datetime.isin(onesout.order_datetime)

    oneprod['hours1'] = oneprod['time_5h'].apply(lambda x: (x.hour*60*60 + x.minute*60 + x.second)/(24*60*60) - 1)
    oneprod['hours2'] = oneprod.hours1 ** 2
    oneprod['stockout_x_hours1'] = oneprod.stockout_hour * oneprod.hours1
    oneprod['stockout_x_hours2'] = oneprod.stockout_hour * oneprod.hours2

    oneprod['date_5h'] = pd.to_datetime(oneprod.date_5h)
    oneprod['days1'] = (oneprod.date_5h - oneprod.date_5h.min()).dt.days
    oneprod['days2'] = oneprod.days1 ** 2
    oneprod['days3'] = oneprod.days1 ** 3
    oneprod = oneprod.merge(pd.get_dummies(oneprod.date_5h.dt.dayofweek, prefix = 'd', prefix_sep = ''), 
                            left_index = True, right_index=True)
    return(oneprod)

def get_list_result(df, idpy, idpx):
    # it generates a list of dictionaries with the main results for each model
    try:
        oneprod = get_df_regress(df, idpy, idpx)
    except ValueError:
        return ValueError
    
    zeta = '+ hours1 + hours2 + days1 + days2 + days3 + start + d1 + d2 + d3 + d4 + d5 + d6'

    formula = 'lncumsales ~ stockout_day' + zeta
    model = sm.ols(formula = formula, data = oneprod)
    fitted1 = model.fit()

    formula = 'lncumsales ~ stockout_day + stockout_hour + stockout_x_hours1 + stockout_x_hours2' + zeta
    model = sm.ols(formula = formula, data = oneprod)
    fitted2 = model.fit()

    formula = 'lncumsales ~ stockout_day + stockout_hour + stockout_x_hours1 + stockout_x_hours2 + span + span2' + zeta
    model = sm.ols(formula = formula, data = oneprod)
    fitted3 = model.fit()

    def gen_prob(x):
        b_h1 = fitted3.params['hours1']
        b_h2 = fitted3.params['hours2']
        b_s = fitted3.params['stockout_hour[T.True]']
        b_sh1 = fitted3.params['stockout_x_hours1']
        b_sh2 = fitted3.params['stockout_x_hours2']
        if (x[0] == 0) & (x[1] == 0):
            return 0
        else:
            denom = b_s + (b_h1+b_sh1) + (b_h2+b_sh2)
            x0, x1 = x
            try:
                return (b_s + (b_h1+b_sh1)*x1 + (b_h2+b_sh2)*x1**2 - b_h1*x0 - b_h2*x0**2)/denom
            except ZeroDivisionError:
                return 1

    oneprod['stockout_day_x_prob'] = oneprod[['start','end']].apply(gen_prob, axis = 1)

    formula = 'lncumsales ~ stockout_day_x_prob' + zeta
    model = sm.ols(formula = formula, data = oneprod)
    fitted4 = model.fit()

    formula = 'lncumsales ~ stockout_day_x_prob + stockout_hour + stockout_x_hours1 + stockout_x_hours2' + zeta
    model = sm.ols(formula = formula, data = oneprod)
    fitted5 = model.fit()

    formula = 'lncumsales ~ stockout_day_x_prob + stockout_hour + stockout_x_hours1 + stockout_x_hours2 + start + span + span2' + zeta
    model = sm.ols(formula = formula, data = oneprod)
    fitted6 = model.fit()
    
    days_obs = oneprod.groupby('date_5h')['stockout_day'].first()
    pair_info = {
        'idp_y': idpy,
        'idp_x': idpx,
        'N_obs': len(oneprod.index),
        'N_days': len(days_obs.index),
        'T_days': days_obs.sum(),
        'T_perc': 100*days_obs.mean()
    }

    models = [fitted1, fitted2, fitted3, fitted4, fitted5, fitted6]
    x_star = ['stockout_day[T.True]']*3 + ['stockout_day_x_prob']*3
    number = list(range(6))

    result = []
    for i,m,x in zip(number, models, x_star):
        result.append(
            {
                **pair_info,
                'model' : i+1, 
                'coef': 100*m.params[x], 
                'stderr': 100*m.bse[x],
                'pvalue': m.pvalues[x],
            }
        )

    return(result) #pd.DataFrame(result)