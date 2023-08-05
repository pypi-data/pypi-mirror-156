import pandas as pd
import numpy as np
import argparse
from .provider import Provider
from .periods import *
from .version import VERSION

default_provider = Provider['SINA']

def finstats():
  args = parse_args()

  if check_args(args):
    stocks = args.stock
    benchmarks = args.bench
    datalen = args.length
    riskfree = args.riskfree
    period = args.period

    return_list, benchmark_return_list = prepare_data_pair(
      stocks,
      benchmarks,
      datalen=datalen
    )

    result = []
    for benchmark, benchmark_return in zip(benchmarks, benchmark_return_list):
      for stock, returns in zip(stocks, return_list):
        align_returns, align_benchmark_return = align_series(returns, benchmark_return)
        alpha, beta = cal_alpha_beta(
          align_returns,
          align_benchmark_return,
          risk_free=riskfree,
          period=period,
        )
        result.append({
            "stock": stock,
            "benchmark": benchmark, 
            "beta": beta,
            "alpha": alpha
        })

    print(pd.DataFrame(result).set_index('benchmark'))


def cal_alpha_beta(
  returns,
  benchmark_returns,
  risk_free=0,
  period=DAILY,
):
  """
  Parameters
  ----------
  returns: pd.series. stock returns data
  benchmark_returns: pd.series. benchmark return data
  risk_free: risk free return, usually the treasury bond return or bank interest rate
  period: str
      periodicity of the 'returns' data
        Defaults are::
                'y':1
                'q':4
                'm':12
                'w': 52
                'd': 252
  """
  beta = cal_beta(returns, benchmark_returns)
  alpha = cal_alpha(returns, benchmark_returns, beta=beta, risk_free=risk_free, period=period)
  return alpha, beta



def cal_beta(
  returns,
  benchmark_returns,
):
  """
  Parameters
  ----------
  returns: np.array, returns of the strategy
  benchmark_returns: np.array, returns of the benchmark (eg, sh000001, sh000300)

  Returns
  -------
  beta
  """
  # Calculate beta as Cov(X, Y) / Cov(X, X).
    # https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line  # noqa
    #
    # NOTE: The usual formula for covariance is::
    #
    #    mean((X - mean(X)) * (Y - mean(Y)))
    #
    # However, we don't actually need to take the mean of both sides of the
    # product, because of the folllowing equivalence::
    #
    # Let X_res = (X - mean(X)).
    # We have:
    #
    #     mean(X_res * (Y - mean(Y))) = mean(X_res * (Y - mean(Y)))
    #                             (1) = mean((X_res * Y) - (X_res * mean(Y)))
    #                             (2) = mean(X_res * Y) - mean(X_res * mean(Y))
    #                             (3) = mean(X_res * Y) - mean(X_res) * mean(Y)
    #                             (4) = mean(X_res * Y) - 0 * mean(Y)
    #                             (5) = mean(X_res * Y)
    #
    #
    # The tricky step in the above derivation is step (4). We know that
    # mean(X_res) is zero because, for any X:
    #
    #     mean(X - mean(X)) = mean(X) - mean(X) = 0.
    #
    # The upshot of this is that we only have to center one of `independent`
    # and `dependent` when calculating covariances. Since we need the centered
    # `independent` to calculate its variance in the next step, we choose to
    # center `independent`.
  
  bentch_return_residual = benchmark_returns - np.mean(benchmark_returns)
  covariances = np.mean(bentch_return_residual * returns)
  # We end up with different variances in each column here because each
  # column may have a different subset of the data dropped due to missing
  # data in the corresponding dependent column.
  # shape: (M,)
  bentch_return_residual = np.square(bentch_return_residual)
  independent_variances = np.mean(bentch_return_residual)
  return np.divide(covariances, independent_variances)


def cal_alpha(returns, benchmark_returns, beta=None, risk_free=0, period=DAILY):
  """
  Parameters
  ----------
  returns: np.array, returns of the strategy
  benchmark_returns: np.array, returns of the benchmark (eg, sh000001, sh000300)
  beta: The beta for the given inputs
  risk_free: risk free return, usually the treasury bond return or bank interest rate
  period: str
      periodicity of the 'returns' data
        Defaults are::
                'y':1
                'q':4
                'm':12
                'w': 52
                'd': 252

  Returns
  -------
  beta
  """
  adjust_returns = adj_returns(returns, risk_free)
  adjust_benchmark_returns = adj_returns(benchmark_returns, risk_free)

  if beta is None:
    beta = cal_beta(returns, benchmark_returns)
  alpha_series = adjust_returns  - (beta * adjust_benchmark_returns)

  ann_factor = ANNUALIZATION_FACTORS[period]

  return np.subtract(
            np.power(
              np.add(
                np.mean(
                  alpha_series
                ),
                1
              ),
              ann_factor
            ),
            1
          )


def align_series(returns, benchmark_returns):
  """
  align input dataframe's indices and return series

  Parameters
  ----------
  symbol: stock code
  scale: periods. 5、15、30、60,120,240
  datalen: number of records

  Returns
  -------
  pd.series
  """
  df_concated = pd.concat([returns, benchmark_returns], axis=1)
  df_concated = df_concated.dropna()
  return [df_concated.iloc[:,x].values for x in [0, 1]]


def prepare_data_pair(
  return_symbols,
  benchmark_symbols,
  datalen=default_provider.datalen
):
  return_list  = []
  benchmark_return_list = []
  for return_symbol in return_symbols:
    return_list.append(
      provide_return_data(return_symbol, datalen)
    )
  for benchmark_symbol in benchmark_symbols:
    benchmark_return_list.append(
      provide_return_data(benchmark_symbol, datalen)
    )
  return return_list, benchmark_return_list


def provide_return_data(symbol, datalen=default_provider.datalen, period=240):
  """
  fetch data from provider

  Parameters
  ----------
  symbol: stock code
  period: stock period in minutes. 5、15、30、60,120,240
  datalen: number of records

  Returns
  -------
  pd.dataframe
  """

  df = default_provider.provide_daily_bar(symbol, datalen, period)
  return df.set_index('day')[['return']]


def adj_returns(returns, risk_free):
  if risk_free == 0 and isinstance(risk_free, (int, float)):
    return returns
  return returns - risk_free


def check_args(args):
  if args.stock is None:
    print("finstats: please provide stock code. See 'finstats --help'")
    return False
  if args.bench is None:
    print("finstats: please provide benchmark code. See 'finstats --help'")
    return False
  if args.version is not None:
    print("finstats: v{}".format(VERSION))
    return False
  return True
  

def parse_args():
  parser = argparse.ArgumentParser(
    prog="finstats",
    description='get financial metrics with finstats'
  )
  parser.add_argument(
    '--stock',
    '-s', 
    nargs='*',
    help="the stock code to fetch. eg: sh600519"
  )
  parser.add_argument(
    '--bench',
    '-b',
    nargs='*',
    help="the benchmark code to fetch. eg: sh000001"
  )
  parser.add_argument(
    '--riskfree',
    '-r',
    help="risk free return, default is 0. eg: 0.02",
    default=0
  )
  parser.add_argument(
    '--period',
    '-p',
    help="periodicity of the 'returns' data:: y/q/m/w/d, default is d",
    default=DAILY
  )
  parser.add_argument(
    '--length',
    '-l',
    help="number of records to fetch, default is 1023. eg: 30",
    default=default_provider.datalen
  )
  parser.add_argument(
    '--version',
    '-v',
    help="finstats version",
  )
  return parser.parse_args()