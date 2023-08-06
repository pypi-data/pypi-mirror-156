# This file is part of scrilla: https://github.com/chinchalinchin/scrilla.

# scrilla is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# scrilla is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with scrilla.  If not, see <https://www.gnu.org/licenses/>
# or <https://github.com/chinchalinchin/scrilla/blob/develop/main/LICENSE>.

"""
This module provides a data access layer for a SQLite database maintained on the local file system at the location set by the environment variable **SQLITE_FILE**. If this environment variable is not set, the file location defaults to the *installation_directory*/data/cache/scrilla.db. The database caches asset prices, statistical calculations and interest rates. This allows the program to avoid excessive API calls to external services for calculations that involve the same quantity. For instance, to calculate correlation, the mean and variance of the individual assets must be calculated over the price history of each before the correlation is calculated over their combined price history; this involves four references to a sample of prices, at different points in the program which do not necessarily share scope with the location of the other calculations, so they can not share the in-memory version of the prices.

In addition to preventing excessive API calls, the cache prevents redundant calculations. For example, calculating the market beta for a series of assets requires the variance of the market proxy for each calculation. Rather than recalculate this quantity each time, the program will defer to the values stored in the cache.
"""
import pprint
from scrilla import settings

if settings.CACHE_MODE == 'sqlite':
    import sqlite3
elif settings.CACHE_MODE == 'dynamodb':
    from scrilla.cloud import aws

import datetime
from typing import Union
from scrilla.static import keys
from scrilla.util import errors, outputter, dater
from scrilla.files import get_memory_json, save_memory_json

logger = outputter.Logger("scrilla.cache", settings.LOG_LEVEL)


class Cache():
    """
    Class with static methods all other Caches employ. This class tries to hide as much implementation detail as possible behind its methods, i.e. this class is concerned with executing commits and transactions, whereas the other cache classes are concerned with the data structure that is created with these methods.
    """

    @staticmethod
    def provision(table_configuration):
        if settings.CACHE_MODE == 'dynamodb':
            return aws.dynamo_table(table_configuration)

    @staticmethod
    def execute_transaction(transaction, formatter=None):
        """
        Executes and commits a cache transaction. A transaction differs from a query in that all statements are executed, or none are.

        Parameters
        ----------
        1. **transaction**: ``str``
            Statement to be executed and committed.
        2. formatter: `Union[dict, List[dict]]``
            Dictionary of parameters used to format statement. Statements are formatted with DB-API's name substitution. See [sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html) for more information. A list of dictionaries can be passed in to perform a batch execute transaction.
        """
        if settings.CACHE_MODE == 'sqlite':
            con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
            executor = con.cursor()
            if formatter is not None:
                if isinstance(formatter, list):
                    response = executor.executemany(transaction, formatter)
                else:
                    response = executor.execute(transaction, formatter)
            else:
                if isinstance(formatter, list):
                    response = executor.executemany(transaction)
                else:
                    response = executor.execute(transaction)
            con.commit(), con.close()
        elif settings.CACHE_MODE == 'dynamodb':
            response = aws.dynamo_transaction(transaction, formatter)
        else:
            raise errors.ConfigurationError(
                'CACHE_MODE has not been set in "settings.py"')
        return response

    @staticmethod
    def execute_query(query, formatter=None):
        """
        Executes a read-write SQLite query.

        Parameters
        ----------
        1. **query**: ``str``
            Query to be exectued.
        2. **formatter**: ``Union[dict, List[dict]]``
            Dictionary of parameters used to format statement. Statements are formatted with DB-API's name substitution. See [sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html) for more information. A list of dictionaries can be passed in to perform a batch execute query.

        Returns
        -------
        ``list``
            A list containing the results of the query.
        """
        if settings.CACHE_MODE == 'sqlite':
            con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
            con.row_factory = sqlite3.Row
            executor = con.cursor()
            if formatter is not None:
                if isinstance(formatter, list):
                    results = executor.executemany(query, formatter).fetchall()
                else:
                    results = executor.execute(query, formatter).fetchall()
            else:
                results = executor.execute(query).fetchall()
            con.close()
            return results
        elif settings.CACHE_MODE == 'dynamodb':
            return aws.dynamo_statement(query, formatter)
        else:
            raise errors.ConfigurationError(
                'CACHE_MODE has not been set in "settings.py"')


class PriceCache():
    """
    Statically asseses *SQLite* functionality from `scrilla.cache.Cache`. Extends basic functionality to cache prices in a table with columns `(ticker, date, open, close)`, with a unique constraint on the tuplie `(ticker, date)`, i.e. records in the *PriceCache* are uniquely determined by the the combination of the ticker symbol and the date.

    Attributes
    ----------
    1. **sqlite_create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create price cache table if it does not already exist.
    2. **sqlite_insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into price cache table.
    3. **sqlite_price_query**: ``str```
        *SQLite* query to retrieve prices from cache.
    """
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS prices (ticker text, date text, open real, close real, UNIQUE(ticker, date))"
    sqlite_insert_row_transaction = "INSERT OR IGNORE INTO prices (ticker, date, open, close) VALUES (:ticker, :date, :open, :close)"
    sqlite_price_query = "SELECT date, open, close FROM prices WHERE ticker = :ticker AND date <= date(:end_date) AND date >= date(:start_date) ORDER BY date(date) DESC"

    dynamodb_table_configuration = {
        'AttributeDefinitions': [
            {
                'AttributeName': 'ticker',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'date',
                'AttributeType': 'S'
            },
        ],
        'TableName': 'prices',
        'KeySchema': [
            {
                'AttributeName': 'ticker',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'date',
                'KeyType': 'RANGE'
            }
        ],
    }
    dynamodb_insert_transaction = "INSERT INTO \"prices\" VALUE {'ticker': ?, 'date': ?, 'open': ?, 'close': ? }"
    dynamodb_price_query = "SELECT \"date\", \"open\", \"close\" FROM \"prices\" WHERE \"ticker\"=? AND \"date\">=? AND \"date\"<=?"
    # No PartiQL ORDER BY clause yet: https://github.com/partiql/partiql-lang-kotlin/issues/47
    dynamodb_identity_query = "EXISTS(SELECT ticker FROM \"prices\" WHERE ticker=? and date= ?)"

    @staticmethod
    def to_dict(query_results, mode=settings.CACHE_MODE):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        if mode == 'sqlite':
            return {
                result[0]: {
                    keys.keys['PRICES']['OPEN']: result[1],
                    keys.keys['PRICES']['CLOSE']: result[2]
                } for result in query_results
            }
        elif mode == 'dynamodb':
            dates = [result['date'] for result in query_results]
            dates.sort(key=dater.parse)
            dates.reverse()
            formatted_results = {
                result['date']: {
                    keys.keys['PRICES']['OPEN']: result[keys.keys['PRICES']['OPEN']],
                    keys.keys['PRICES']['CLOSE']: result[keys.keys['PRICES']['CLOSE']]
                } for result in query_results
            }
            return {key: formatted_results[key] for key in dates}

    def __init__(self, mode=settings.CACHE_MODE):
        self.mode = mode
        if not get_memory_json()['cache'][mode]['prices']:
            self._table()

    def _table(self):
        if self.mode == 'sqlite':
            Cache.execute_transaction(self.sqlite_create_table_transaction)
        elif self.mode == 'dynamodb':
            self.dynamodb_table_configuration = aws.dynamo_table_conf(
                self.dynamodb_table_configuration)
            Cache.provision(self.dynamodb_table_configuration)

    def _insert(self):
        if self.mode == 'sqlite':
            return self.sqlite_insert_row_transaction
        elif self.mode == 'dynamodb':
            return self.dynamodb_insert_transaction

    def _query(self):
        if self.mode == 'sqlite':
            return self.sqlite_price_query
        elif self.mode == 'dynamodb':
            return self.dynamodb_price_query

    @staticmethod
    def _to_params(ticker, prices):
        return [
            {
                'ticker': ticker,
                'date': date,
                'open': prices[date][keys.keys['PRICES']['OPEN']],
                'close': prices[date][keys.keys['PRICES']['CLOSE']]
            } for date in prices
        ]

    def save_rows(self, ticker, prices):
        logger.verbose(
            F'Attempting to insert {ticker} prices to cache', 'save_rows')
        Cache.execute_query(
            query=self._insert(),
            formatter=self._to_params(ticker, prices)
        )

    def filter_price_cache(self, ticker, start_date, end_date):
        logger.debug(
            f'Querying {self.mode} cache \n\t{self._query()}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}', 'filter_price_cache')
        formatter = {'ticker': ticker,
                     'start_date': start_date, 'end_date': end_date}
        results = Cache.execute_query(
            query=self._query(), formatter=formatter)

        if len(results) > 0:
            logger.debug(
                f'Found {ticker} prices in the cache', 'filter_price_cache')
            return self.to_dict(results)
        logger.debug(
            f'No results found for {ticker} prices in the cache', 'filter_price_cache')
        return None


class InterestCache():
    """
    Statically accesses *SQLite* functionality from `scrilla.cache.Cache`. Extends basic functionality to cache interest rate data in a table with columns `(maturity, date, value)`.

    Attributes
    ----------
    1. **create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create correlation cache table if it does not already exist.
    2. **insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into correlation cache table.
    3. **int_query**: ``str```
        *SQLite* query to retrieve an interest from cache.
    """
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS interest(maturity text, date text, value real, UNIQUE(maturity, date))"
    sqlite_insert_row_transaction = "INSERT OR IGNORE INTO interest (maturity, date, value) VALUES (:maturity, :date, :value)"
    sqlite_interest_query = "SELECT date, value FROM interest WHERE maturity=:maturity AND date <=date(:end_date) AND date>=date(:start_date) ORDER BY date(date) DESC"

    dynamodb_table_configuration = {
        'AttributeDefinitions': [
            {
                'AttributeName': 'maturity',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'date',
                'AttributeType': 'S'
            },
        ],
        'TableName': 'interest',
        'KeySchema': [
            {
                'AttributeName': 'maturity',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'date',
                'KeyType': 'RANGE'
            }
        ],
    }
    dynamodb_insert_transaction = "INSERT INTO \"interest\" VALUE {'maturity': ?, 'date': ?, 'value': ? }"
    dynamodb_query = "SELECT \"date\", \"value\" FROM \"interest\" WHERE \"maturity\"=? AND \"date\">=? AND \"date\"<=?"
    # No PartiQL ORDER BY clause yet: https://github.com/partiql/partiql-lang-kotlin/issues/47
    dynamodb_identity_query = "EXISTS(SELECT 'maturity' FROM \"interest\" WHERE 'maturity'=? AND 'date'<= ?)"

    @staticmethod
    def to_dict(query_results, mode=settings.CACHE_MODE):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        if mode == 'sqlite':
            return {result[0]: result[1] for result in query_results}
        elif mode == 'dynamodb':
            # TODO: need to order by date!
            dates = [result['date'] for result in query_results]
            dates.sort(key=dater.parse)
            dates.reverse()
            formatted_results = {result['date']: result['value']
                                 for result in query_results}
            return {key: formatted_results[key] for key in dates}

    def __init__(self, mode=settings.CACHE_MODE):
        self.mode = mode
        if not get_memory_json()['cache'][mode]['interest']:
            self._table()

    def _table(self):
        if self.mode == 'sqlite':
            Cache.execute_transaction(self.sqlite_create_table_transaction)
        elif self.mode == 'dynamodb':
            self.dynamodb_table_configuration = aws.dynamo_table_conf(
                self.dynamodb_table_configuration)
            Cache.provision(self.dynamodb_table_configuration)

    def _insert(self):
        if self.mode == 'sqlite':
            return self.sqlite_insert_row_transaction
        elif self.mode == 'dynamodb':
            return self.dynamodb_insert_transaction

    def _query(self):
        if self.mode == 'sqlite':
            return self.sqlite_interest_query
        elif self.mode == 'dynamodb':
            return self.dynamodb_query

    @staticmethod
    def _to_params(rates):
        params = []
        for date in rates:
            for index, maturity in enumerate(keys.keys['YIELD_CURVE']):
                entry = {
                    'maturity': maturity,
                    'date': date,
                    'value': rates[date][index]
                }
                params.append(entry)
        return params

    def save_rows(self, rates):
        logger.verbose(
            F'Attempting to insert interest rates into cache', 'save_rows')
        Cache.execute_query(
            query=self._insert(),
            formatter=self._to_params(rates)
        )

    def filter_interest_cache(self, maturity, start_date, end_date):
        logger.debug(
            f'Querying {self.mode} cache \n\t{self._query()}\n\t\t with :maturity={maturity}, :start_date={start_date}, :end_date={end_date}', 'filter_interest_cache')
        formatter = {'maturity': maturity,
                     'start_date': start_date, 'end_date': end_date}
        results = Cache.execute_query(
            query=self._query(), formatter=formatter)

        if len(results) > 0:
            logger.debug(
                f'Found {maturity} yield on in the cache', 'filter_interest_cache')
            return self.to_dict(results)

        logger.debug(
            f'No results found for {maturity} yield in cache', 'filter_interest_cache')
        return None


class CorrelationCache():
    """
    Inherits *SQLite* functionality from `scrilla.cache.Cache`. Extends basic functionality to cache correlation calculations in a table with columns `(ticker_1, ticker_2, correlation, start_date, end_date, estimation_method, weekends)`.

    Attributes
    ----------
    1. **create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create correlation cache table if it does not already exist.
    2. **insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into correlation cache table.
    3. **correlation_query**: ``str```
        *SQLite* query to retrieve correlation from cache.

    .. notes::
        * do not need to order `correlation_query` and `profile_query` because profiles and correlations are uniquely determined by the (`start_date`, `end_date`, 'ticker_1', 'ticker_2')-tuple. More or less. There is a bit of fuzziness, since the permutation of the previous tuple, ('start_date', 'end_date', 'ticker_2', 'ticker_1'), will also be associated with the same correlation value. No other mappings between a date's correlation value and the correlation's tickers are possible though. In other words, the query, for a given (ticker_1, ticker_2)-permutation will only ever return one result.
    """
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS correlations (ticker_1 TEXT, ticker_2 TEXT, start_date TEXT, end_date TEXT, correlation REAL, method TEXT, weekends INT)"
    sqlite_insert_row_transaction = "INSERT INTO correlations (ticker_1, ticker_2, start_date, end_date, correlation, method, weekends) VALUES (:ticker_1, :ticker_2, :start_date, :end_date, :correlation, :method, :weekends)"
    sqlite_correlation_query = "SELECT correlation FROM correlations WHERE ticker_1=:ticker_1 AND ticker_2=:ticker_2 AND start_date=date(:start_date) AND end_date=date(:end_date) AND method=:method AND weekends=:weekends"

    dynamodb_table_configuration = {
        'AttributeDefinitions': [
            {
                'AttributeName': 'ticker_1',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'ticker_2',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'start_date',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'end_date',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'method',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'weekends',
                'AttributeType': 'N'
            },
        ],
        'TableName': 'correlations',
        'KeySchema': [
            {
                'AttributeName': 'ticker_1',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'start_date',
                'KeyType': 'RANGE'
            }
        ],
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'AssetTelescoping',
                'KeySchema': [
                    {
                        'AttributeName': 'ticker_2',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'end_date',
                        'KeyType': 'RANGE'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'KEYS_ONLY'
                }
            },
            {
                'IndexName': 'WeekendTelescoping',
                'KeySchema': [
                    {
                        'AttributeName': 'weekends',
                        'KeyType': 'HASH'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'KEYS_ONLY'
                }
            },
            {
                'IndexName': 'EstimationTelescoping',
                'KeySchema': [
                    {
                        'AttributeName': 'method',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL',
                }
            },
        ]
    }
    # be careful with the dates here. order matters.
    dynamodb_insert_transaction = "INSERT INTO \"correlations\" VALUE {'ticker_1': ?, 'ticker_2': ?, 'end_date': ?, 'start_date': ?, 'correlation': ?, 'method': ?, 'weekends': ? }"
    dynamodb_query = "SELECT correlation FROM \"correlations\" WHERE ticker_1=? AND ticker_2=? AND start_date=? AND end_date=? AND method=? AND weekends=?"
    dynamodb_identity_query = "EXISTS(SELECT correlation FROM \"correlations\" WHERE ticker_1=? AND ticker_2=? AND start_date=? AND end_date=? AND method=? AND weekends=?)"

    @staticmethod
    def to_dict(query_results):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        return {keys.keys['STATISTICS']['CORRELATION']: query_results[0][0]}

    def __init__(self, mode=settings.CACHE_MODE):
        self.mode = mode
        if not get_memory_json()['cache'][mode]['correlations']:
            self._table()

    def _table(self):
        if self.mode == 'sqlite':
            Cache.execute_transaction(self.sqlite_create_table_transaction)
        elif self.mode == 'dynamodb':
            self.dynamodb_table_configuration = aws.dynamo_table_conf(
                self.dynamodb_table_configuration)
            Cache.provision(self.dynamodb_table_configuration)

    def _insert(self):
        if self.mode == 'sqlite':
            return self.sqlite_insert_row_transaction
        elif self.mode == 'dynamodb':
            return self.dynamodb_insert_transaction

    def _query(self):
        if self.mode == 'sqlite':
            return self.sqlite_correlation_query
        elif self.mode == 'dynamodb':
            return self.dynamodb_query

    def save_row(self, ticker_1: str, ticker_2: str, start_date: datetime.date, end_date: datetime.date, correlation: float, weekends: bool, method: str = settings.ESTIMATION_METHOD):
        """
        Uses `self.insert_row_transaction` to save the passed-in information to the SQLite cache.

        Parameters
        ----------
        1. **ticker_1**: ``str``
        2. **ticker_2**: ``str``
        3. **start_date**: ``datetime.date``
        4. **end_date**: ``datetime.date``
        5. **correlation**: ``float``
        6. **weekends**: ``bool``
        7. **method**: ``str``
            *Optional*. Method used to calculate the correlation. Defaults to `scrilla.settings.ESTIMATION_METHOD`, which in turn is configured by the environment variable, *DEFAULT_ESTIMATION_METHOD*.
        """
        logger.verbose(
            f'Saving ({ticker_1}, {ticker_2}) correlation from {start_date} to {end_date} to the cache', 'save_row')
        formatter_1 = {'ticker_1': ticker_1, 'ticker_2': ticker_2,
                       'start_date': start_date, 'end_date': end_date,
                       'correlation': correlation,
                       'method': method, 'weekends': weekends}
        formatter_2 = {'ticker_1': ticker_2, 'ticker_2': ticker_1,
                       'start_date': start_date, 'end_date': end_date,
                       'correlation': correlation,
                       'method': method, 'weekends': weekends}
        Cache.execute_transaction(
            transaction=self._insert(), formatter=formatter_1)
        Cache.execute_transaction(
            transaction=self._insert(), formatter=formatter_2)

    def filter_correlation_cache(self, ticker_1, ticker_2, start_date, end_date, weekends, method=settings.ESTIMATION_METHOD):
        formatter_1 = {'ticker_1': ticker_1, 'ticker_2': ticker_2, 'method': method,
                       'start_date': start_date, 'end_date': end_date, 'weekends': weekends}
        formatter_2 = {'ticker_1': ticker_2, 'ticker_2': ticker_1, 'method': method,
                       'start_date': start_date, 'end_date': end_date, 'weekends': weekends}

        logger.debug(
            f'Querying {self.mode} cache \n\t{self._query()}\n\t\t with :ticker_1={ticker_1}, :ticker_2={ticker_2},:start_date={start_date}, :end_date={end_date}', 'filter_correlation_cache')
        results = Cache.execute_query(
            query=self._query(), formatter=formatter_1)

        if len(results) > 0:
            logger.debug(
                f'Found ({ticker_1},{ticker_2}) correlation in the cache', 'filter_correlation_cache')
            return self.to_dict(results)
        results = Cache.execute_query(
            query=self._query(), formatter=formatter_2)

        if len(results) > 0:
            logger.debug(
                f'Found ({ticker_1},{ticker_2}) correlation in the cache', 'filter_correlation_cache')
            return self.to_dict(results)
        logger.debug(
            f'No results found for ({ticker_1}, {ticker_2}) correlation in the cache', 'filter_correlation_cache')
        return None


class ProfileCache():
    """
    Statically assesses the *SQLite* functionality from `scrilla.cache.Cache`. Extends basic functionality to cache risk profile calculations in a table with columns `(ticker, start_date, end_date, annual_return, annual_volatility, sharpe_ration, asset_beta, equity_cost, estimation_method)`.

    Attributes
    ----------
    1. **create_table_transaction**: ``str``
        *SQLite* transaction passed to Cache. Used to create profile cache table if it does not already exist.
    """
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, ticker TEXT, start_date TEXT, end_date TEXT, annual_return REAL, annual_volatility REAL, sharpe_ratio REAL, asset_beta REAL, equity_cost REAL, method TEXT, weekends INT)"
    sqlite_filter = "ticker=:ticker AND start_date=date(:start_date) AND end_date=date(:end_date) AND :method=method AND weekends=:weekends"
    sqlite_identity_query = "SELECT id FROM profile WHERE ticker=:ticker AND start_date=:start_date AND end_date=:end_date AND method=:method AND weekends=:weekends"
    sqlite_profile_query = "SELECT ifnull(annual_return, 'empty'), ifnull(annual_volatility, 'empty'), ifnull(sharpe_ratio, 'empty'), ifnull(asset_beta, 'empty'), ifnull(equity_cost, 'empty') FROM profile WHERE {sqlite_filter}".format(
        sqlite_filter=sqlite_filter)

    dynamodb_table_configuration = {
        'AttributeDefinitions': [
            {
                'AttributeName': 'ticker',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'start_date',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'end_date',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'method',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'weekends',
                'AttributeType': 'N'
            }
        ],
        'TableName': 'profile',
        'KeySchema': [
            {
                'AttributeName': 'ticker',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'start_date',
                'KeyType': 'RANGE'
            }
        ],
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'DateTelescoping',
                'KeySchema': [
                    {
                        'AttributeName': 'weekends',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'end_date',
                        'KeyType': 'RANGE'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'KEYS_ONLY'
                }
            },
            {
                'IndexName': 'EstimationTelescoping',
                'KeySchema': [
                    {
                        'AttributeName': 'method',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL',
                }
            }
        ]
    }
    dynamodb_profile_query = "SELECT annual_return,annual_volatility,sharpe_ratio,asset_beta,equity_cost FROM \"profile\" WHERE ticker=? AND start_date=? AND end_date=? AND method=? AND weekends=?"
    # TODO: exists() needs to be inside of a transaction, not query. however, the following transaction does not work for some reason...
    # dynamodb_identity_query = "EXISTS(SELECT * FROM \"profile\" WHERE ticker=? AND start_date=? AND end_date=? AND method=? AND weekends=?)"
    dynamodb_identity_query = "SELECT * FROM \"profile\" WHERE ticker =? AND start_date=? AND end_date=? AND method=? AND weekends=?"

    @staticmethod
    def to_dict(query_result, mode=settings.CACHE_MODE):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        if mode == 'sqlite':
            return {
                keys.keys['STATISTICS']['RETURN']: query_result[0][0] if query_result[0][0] != 'empty' else None,
                keys.keys['STATISTICS']['VOLATILITY']: query_result[0][1] if query_result[0][1] != 'empty' else None,
                keys.keys['STATISTICS']['SHARPE']: query_result[0][2] if query_result[0][2] != 'empty' else None,
                keys.keys['STATISTICS']['BETA']: query_result[0][3] if query_result[0][3] != 'empty' else None,
                keys.keys['STATISTICS']['EQUITY']: query_result[0][4] if query_result[0][4] != 'empty' else None
            }
        elif mode == 'dynamodb':
            return query_result[0]

    @staticmethod
    def _construct_update(params, mode=settings.CACHE_MODE):
        if mode == 'sqlite':
            update_query = 'UPDATE profile SET '
            for param in params.keys():
                update_query += f'{param}=:{param}'
                if list(params.keys()).index(param) != len(params)-1:
                    update_query += ','
            update_query += " WHERE ticker=:ticker AND start_date=:start_date AND end_date=:end_date AND method=:method AND weekends=:weekends"
            return update_query
        elif mode == 'dynamodb':
            update_query = 'UPDATE profile '
            for param in params.keys():
                update_query += f'SET {param}=? '
            update_query += "WHERE ticker=? AND start_date=? AND end_date=? AND method=? AND weekends=?"
            return update_query

    @staticmethod
    def _construct_insert(params_and_filter, mode=settings.CACHE_MODE):
        if mode == 'sqlite':
            insert_query = 'INSERT INTO profile ('
            for param in params_and_filter.keys():
                insert_query += f'{param}'
                if list(params_and_filter.keys()).index(param) != len(params_and_filter) - 1:
                    insert_query += ","
                else:
                    insert_query += ") VALUES ("
            for param in params_and_filter.keys():
                insert_query += f':{param}'
                if list(params_and_filter.keys()).index(param) != len(params_and_filter) - 1:
                    insert_query += ","
                else:
                    insert_query += ")"
            return insert_query
        elif mode == 'dynamodb':
            insert_query = "INSERT INTO \"profile\" VALUE {"
            for param in params_and_filter.keys():
                insert_query += f'\'{param}\': ?'
                if list(params_and_filter.keys()).index(param) != len(params_and_filter)-1:
                    insert_query += ", "
                else:
                    insert_query += "}"
            return insert_query

    def __init__(self, mode=settings.CACHE_MODE):
        self.mode = mode
        if not get_memory_json()['cache'][mode]['profile']:
            self._table()

    def _table(self):
        if self.mode == 'sqlite':
            Cache.execute_transaction(self.sqlite_create_table_transaction)
        elif self.mode == 'dynamodb':
            self.dynamodb_table_configuration = aws.dynamo_table_conf(
                self.dynamodb_table_configuration)
            Cache.provision(self.dynamodb_table_configuration)

    def _query(self):
        if self.mode == 'sqlite':
            return self.sqlite_profile_query
        elif settings.CACHE_MODE == 'dynamodb':
            return self.dynamodb_profile_query

    def _identity(self):
        if self.mode == 'sqlite':
            return self.sqlite_identity_query
        elif self.mode == 'dynamodb':
            return self.dynamodb_identity_query

    def save_or_update_row(self, ticker: str, start_date: datetime.date, end_date: datetime.date, annual_return: Union[float, None] = None, annual_volatility: Union[float, None] = None, sharpe_ratio: Union[float, None] = None, asset_beta: Union[float, None] = None, equity_cost: Union[float, None] = None, weekends: int = 0, method: str = settings.ESTIMATION_METHOD):
        filter = {'ticker': ticker, 'start_date': start_date,
                  'end_date': end_date, 'method': method, 'weekends': weekends}
        params = {}

        if annual_return is not None:
            params['annual_return'] = annual_return
        if annual_volatility is not None:
            params['annual_volatility'] = annual_volatility
        if sharpe_ratio is not None:
            params['sharpe_ratio'] = sharpe_ratio
        if asset_beta is not None:
            params['asset_beta'] = asset_beta
        if equity_cost is not None:
            params['equity_cost'] = equity_cost

        identity = Cache.execute_query(self._identity(), filter)

        if len(identity) == 0:
            return Cache.execute_transaction(self._construct_insert({**params, **filter}),
                                             {**params, **filter})
        return Cache.execute_transaction(self._construct_update(params),
                                         {**params, **filter})

    def filter_profile_cache(self, ticker: str, start_date: datetime.date, end_date: datetime.date, weekends: int = 0, method=settings.ESTIMATION_METHOD):
        logger.debug(
            f'Querying {self.mode} cache: \n\t{self._query()}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}', 'filter_profile_cache')
        formatter = {'ticker': ticker, 'start_date': start_date,
                     'end_date': end_date, 'method': method, 'weekends': weekends}
        result = Cache.execute_query(
            query=self._query(), formatter=formatter)

        if len(result) > 0:
            logger.debug(f'{ticker} profile found in cache',
                         'filter_profile_cache')
            return self.to_dict(result)
        logger.debug(
            f'No results found for {ticker} profile in the cache', 'filter_profile_cache')
        return None


def init_cache():
    memory = get_memory_json()
    if not memory['cache'][settings.CACHE_MODE]['prices']:
        PriceCache()
        memory['cache'][settings.CACHE_MODE]['prices'] = True
    if not memory['cache'][settings.CACHE_MODE]['interest']:
        InterestCache()
        memory['cache'][settings.CACHE_MODE]['interest'] = True
    if not memory['cache'][settings.CACHE_MODE]['profile']:
        ProfileCache()
        memory['cache'][settings.CACHE_MODE]['profile'] = True
    if not memory['cache'][settings.CACHE_MODE]['correlations']:
        CorrelationCache()
        memory['cache'][settings.CACHE_MODE]['correlations'] = True
    save_memory_json(memory)
