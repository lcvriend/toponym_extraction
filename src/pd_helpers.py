# standard library
import itertools

# third party
import pandas as pd


def aggregate(df, cols, grouper, agg='mean'):
    df_count = df.groupby(grouper)[grouper].count().to_frame()
    df_agg = df.groupby(grouper)[cols].agg([agg]).round(1)
    df_agg.columns = [col for col in df_agg.columns]
    df_agg = df_count.join(df_agg)
    df_agg = df_agg.T
    df_agg['std'] = df_agg.agg('std', axis=1).round(2)
    return df_agg


def normalize_cols(df, columns, size_variable, invert=False):
    """
    Normalize a collection of columns by dividing them by a size_variable.
    If invert=True, normalize by dividing size_variable by columns instead.

    Parameters
    ==========
    :param df: `DataFrame`
    :param columns:
        Collection of column names to be normalized.
    :param size_variable: `str`
        Name of column to use as size variable.

    Optional key-word arguments
    ===========================
    :param invert: `boolean`, default=False
        If True divide size_variable by columns.

    Return
    ======
    :normalize_cols: `DataFrame`
    """

    if invert:
        df_ = 1 / df[columns].div(df[size_variable], axis=0)
        df_.columns = [f"{size_variable}/{col}" for col in columns]
    else:
        df_ = df[columns].div(df[size_variable], axis=0)
        df_.columns = [f"{col}/{size_variable}" for col in columns]
    return df.join(df_)


def count_per_week(
    df,
    date_field,
    groupers,
    start=None,
    end=None,
    agg_field_name='count',
    date_field_name='date',
    ):
    """
    Count the number of records per group and per week.

    Parameters
    ==========
    :param df: `DataFrame`
    :param date_field: `str`
        Name of the column with the dates to aggregate.
    :param grouper: `str`
        Name of the column with the categories to group by.

    Optional key-word arguments
    ===========================
    :param start: `Timestamp`, default=None
        Start date of period, if None uses date_field.min().
    :param end: `Timestamp`, default=None
        End date of period, if None uses date_field.max().
    :param agg_field_name: `str`, default='count'
        Column name for count column in output.
    :param date_field_name: `str`, default='date'
        Column name for date column in output.

    Returns
    =======
    :count_per_week: `DataFrame`
    """

    df = df.copy()
    df[date_field] = df[date_field].dt.date.astype('datetime64[ns]')

    if not isinstance(groupers, list):
        groupers = [groupers]

    if not start:
        start = df[date_field].min()
    if not end:
        end = df[date_field].max()

    # create a base frame
    # this ensures all weeks within the period are present in the output
    # even if there are no observations in the DataFrame for certain weeks
    cols = [*groupers]
    df_out = pd.DataFrame(columns=cols)

    idx = weeks_in_period(start, end)

    combos = list(
        itertools.product(*[df[grouper].unique() for grouper in groupers])
        )

    for combo in combos:
        data = [combo] * len(idx)
        df_ = pd.DataFrame(data, index=idx, columns=cols)
        df_out = df_out.append(df_, sort=False)

    df_out = df_out.set_index(groupers, append=True)
    df_out[agg_field_name] = 0

    df = period_selector(df, date_field, start=start, end=end)
    if not df.empty:
        # find previous first day of the week for each date
        df[date_field_name] = (
            df[date_field] - df[date_field].dt.weekday.astype('timedelta64[D]')
            )

        df[agg_field_name] = 0
        df_agg = (
            df.groupby(
                [date_field_name, *groupers]
                )[agg_field_name].count()
            )

        df_out.update(df_agg)
    df_out = df_out.reset_index(level=list(range(1, df_out.index.nlevels)))
    df_out.index.name = date_field_name
    return df_out


def count_per_day(
    df,
    date_field,
    groupers,
    start=None,
    end=None,
    agg_field_name='count',
    date_field_name='date',
    ):
    """
    Count the number of records per group and per week.

    Parameters
    ==========
    :param df: `DataFrame`
    :param date_field: `str`
        Name of the column with the dates to aggregate.
    :param grouper: `str`
        Name of the column with the categories to group by.

    Optional key-word arguments
    ===========================
    :param start: `Timestamp`, default=None
        Start date of period, if None uses date_field.min().
    :param end: `Timestamp`, default=None
        End date of period, if None uses date_field.max().
    :param agg_field_name: `str`, default='count'
        Column name for count column in output.
    :param date_field_name: `str`, default='date'
        Column name for date column in output.

    Returns
    =======
    :count_per_week: `DataFrame`
    """

    df = df.copy()
    df[date_field] = df[date_field].dt.date.astype('datetime64[ns]')

    if not isinstance(groupers, list):
        groupers = [groupers]

    if not start:
        start = df[date_field].min()
    if not end:
        end = df[date_field].max()

    # create a base frame
    # this ensures all weeks within the period are present in the output
    # even if there are no observations in the DataFrame for certain weeks
    cols = [*groupers]
    df_out = pd.DataFrame(columns=cols)

    idx = days_in_period(start, end)

    combos = list(
        itertools.product(*[df[grouper].unique() for grouper in groupers])
        )

    for combo in combos:
        data = [combo] * len(idx)
        df_ = pd.DataFrame(data, index=idx, columns=cols)
        df_out = df_out.append(df_, sort=False)

    df_out = df_out.set_index(groupers, append=True)
    df_out[agg_field_name] = 0

    df = period_selector(df, date_field, start=start, end=end)
    if not df.empty:
        # find previous first day of the week for each date
        df[agg_field_name] = 0
        df_agg = (
            df.groupby(
                [date_field, *groupers]
                )[agg_field_name].count()
            )

        df_out.update(df_agg)
    df_out = df_out.reset_index(level=list(range(1, df_out.index.nlevels)))
    df_out.index.name = date_field_name
    return df_out


def weeks_in_period(start, end):
    """
    Return a list of dates containing all weeks within the selected period.
    Each week is represented by the date of the first day of the week.

    Arguments
    =========
    :param start: `Timestamp`
    :param end: `Timestamp`

    Returns
    =======
    :weeks_in_period: `list`
    """

    week_strt = start - pd.Timedelta(start.weekday(), 'D')
    week_end  = end   - pd.Timedelta(end.weekday(), 'D')

    date = week_strt
    period = list()
    while date < week_end:
        if date.weekday() == 0:
            period.append(date)
        date = date + pd.Timedelta(1, 'D')
    return period


def days_in_period(start, end):
    """
    Return a list of dates containing all weeks within the selected period.
    Each week is represented by the date of the first day of the week.

    Arguments
    =========
    :param start: `Timestamp`
    :param end: `Timestamp`

    Returns
    =======
    :weeks_in_period: `list`
    """

    date = start
    period = list()
    while date < end:
        period.append(date)
        date = date + pd.Timedelta(1, 'D')
    return period


def period_selector(df, date_field, start, end):
    """
    Select records from df within a specified period.

    Parameters
    ==========
    :param df: DataFrame.
    :param date_field: Name of date field to query (string)
    :param start: Start of period as timestamp.
    :param end: End of period as timestamp.

    Returns
    =======
    :selector: `DataFrame`
    """

    qry = (
        f"{date_field} >= @start & "
        f"{date_field} < @end"
    )
    return df.query(qry).copy()
