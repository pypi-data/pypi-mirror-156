from __future__ import annotations

import pandas as pd
import re
import numpy as np
import functools
import warnings

from typing import Union, Optional
from datetime import datetime

import teaspoon
from teaspoon.physics import analytical_fourier
from teaspoon.misc import _is_depth_column
from teaspoon.plots.static import trumpet_curve, colour_contour, time_series

if False:  # work-around for type hints error (F821 undefined name)
    import matplotlib


class TSP:
    """ A Time Series Profile (a collection of time series data at different depths)
    
    A TSP can also be:
    Thermal State of Permafrost
    Temperature du Sol en Profondeur
    Temperatures, Secondes, Profondeurs

    Parameters
    ----------
    times : list-like
        t-length array of datetime objects
    depths : list-like
        d-length array of depths
    values : numpy.ndarray
        array with shape (t,d) containing values at (t)emperatures and (d)epths
    longitude : float, optional
        Longitude at which data were collected
    latitude : float, optional
        Latitude at which data were collected
    site_id : str, optional
        Name of location at which data were collected
    metadata : dict
        Additional metadata
    """

    def __repr__(self) -> str:
        return repr(self.wide)

    def __str__(self) -> str:
        return str(self.wide)

    def __init__(self, times, depths, values, 
                 latitude: Optional[float]=None, 
                 longitude: Optional[float]=None,
                 site_id: Optional[str]=None,
                 metadata:dict={}):

        self._times = np.atleast_1d(times)
        self._depths = np.atleast_1d(depths)
        self._values = np.atleast_2d(values)
        self.metadata = metadata
        self.latitude = latitude
        self.longitude = longitude
        self.site_id = site_id

    @property
    @functools.lru_cache()
    def long(self) -> "pd.DataFrame":
        """ Return the data in a 'long' or 'tidy' format (one row per observation, one column per variable)

        Returns
        -------
        DataFrame
            Time series profile data
        """
        return self.wide.melt(id_vars='time',
                               var_name="depth",
                               value_name="temperature_in_ground")

    @property
    @functools.lru_cache()
    def wide(self) -> "pd.DataFrame":
        """ Return the data in a 'wide' format (one depth per column)

        Returns
        -------
        DataFrame
            Time series profile data
        """
        tabular = pd.DataFrame(self._values)
        tabular.columns = self._depths
        tabular.index = self._times
        tabular.insert(0, "time", self._times)

        return tabular

    def monthly(self) -> "TSP":
        """ Monthly averages 

        Returns
        -------
        TSP
            A TSP object with data aggregated to monthly averages
        """
        YM = self.wide['time'].dt.strftime("%Y%m")
        grouped = self.wide.groupby(YM)
        mth_avg = grouped.mean().to_numpy()
        times = pd.to_datetime(YM, format="%Y%m").unique()
        tsp = TSP(times=times, depths=self.depths, values=mth_avg)
        return tsp

    def daily(self) -> "TSP":
        """Daily averages 

        Returns
        -------
        TSP
            A TSP object with data aggregated to daily averages
        """
        YM = self.wide['time'].dt.strftime("%Y%m%d")
        grouped = self.wide.groupby(YM)
        day_avg = grouped.mean().to_numpy()
        times = pd.to_datetime(YM, format="%Y%m%d").unique()
        tsp = TSP(times=times, depths=self.depths, values=day_avg)
        return tsp

    @property
    def depths(self) -> "np.ndarray":
        """ Return the depth values in the profile 

        Returns
        -------
        numpy.ndarray
            The depths in the profile
        """
        return self._depths

    @depths.setter
    def depths(self, value):
        depths = np.atleast_1d(value)
        
        if not len(depths) == len(self._depths):
            raise ValueError(f"List of depths must have length of {len(self._depths)}.")

        self._depths = depths

    @property
    def times(self):
        """ Return the timestamps in the time series 

        Returns
        -------
        numpy.ndarray
            The timestamps in the time series
        """
        return self._times

    @property
    def values(self):
        return self._values

    def to_gtnp(self, filename: str) -> None:
        """ Write the data in GTN-P format
        
        Parameters
        ----------
        filename : str
            Path to the file to write to
        """
        df = self.wide.rename(columns={'time': 'Date/Depth'})
        df['Date/Depth'] = df['Date/Depth'].dt.strftime("%Y-%m-%d %H:%M:%S")

        df.to_csv(filename, index=False, na_rep="-999")

    def to_ntgs(self, filename:str, project_name:str="", site_id:"Optional[str]" = None, latitude:"Optional[float]"=None, longitude:"Optional[float]"=None) -> None:
        """ Write the data in NTGS template format 

        Parameters
        ----------
        filename : str
            Path to the file to write to
        project_name : str, optional
            The project name, by default ""
        site_id : str, optional
            The name of the site , by default None
        latitude : float, optional
            WGS84 latitude at which the observations were recorded, by default None
        longitude : float, optional
            WGS84 longitude at which the observations were recorded, by default None
        """
        if latitude is None:
            latitude = self.latitude if self.latitude is not None else ""

        if longitude is None:
                longitude = self.longitude if self.longitude is not None else ""

        if site_id is None:
                site_id = self.site_id if self.site_id is not None else ""
        data = self.values
        
        df = pd.DataFrame()
        df["project_name"] = project_name
        df["site_id"] = site_id
        df["latitude"] = latitude
        df["longitude"] = longitude
        df["date_YYYY-MM-DD"] = pd.Series(self.times).dt.strftime(r"%Y-%m-%d")
        df["time_HH:MM:SS"] = pd.Series(self.times).dt.strftime(r"%H:%M:%S")
        
        headers = [str(d) + "_m" for d in self.depths]
        
        for i, h in enumerate(headers):
            df[h] = data[:, i]

        df.to_csv(filename, index=False)

    def to_netcdf(self, file: str) -> None:
        """  Write the data as a netcdf"""
        pass

    def to_json(self, file: str) -> None:
        """ Write the data to a serialized json file """
        with open(file, 'w') as f:
            f.write(self._to_json())

    def _to_json(self) -> str:
        return self.wide.to_json()

    @classmethod
    def from_json(cls, json_file) -> "TSP":
        """ Read data from a json file 

        Parameters
        ----------
        json_file : str
            Path to a json file from which to read
        """
        df = pd.read_json(json_file)
        depth_pattern = r"^(-?[0-9\.]+)$"

        times = pd.to_datetime(df['time']).values
        depths = [re.search(depth_pattern, c).group(1) for c in df.columns if teaspoon._is_depth_column(c, depth_pattern)]
        values = df.loc[:, depths].to_numpy()
        
        tsp = cls(times=times, depths=depths, values=values)
        
        return tsp

    @classmethod
    def synthetic(cls, depths: "np.ndarray", start="2000-01-01", end="2003-01-01",
                  Q:"Optional[float]"=0.2, 
                  c:"Optional[float]"=1.6e6,
                  k:"Optional[float]"=2.5,
                  A:"Optional[float]"=6,
                  MAGST:"Optional[float]"=-0.5) -> "TSP":
        """
        Create a 'synthetic' temperature time series using the analytical solution to the heat conduction equation.
        Suitable for testing 
        
        Parameters
        ----------   
        depths : np.ndarray
            array of depths in m
        start : str
            array of times in seconds
        Q : Optional[float], optional
            Ground heat flux [W m-2], by default 0.2
        c : Optional[float], optional
            heat capacity [J m-3 K-1], by default 1.6e6
        k : Optional[float], optional
            thermal conductivity [W m-1 K-1], by default 2.5
        A : Optional[float], optional
            Amplitude of temperature fluctuation [C], by default 6
        MAGST : Optional[float], optional
            Mean annual ground surface temperature [C], by default -0.5
        
        Returns 
        -------
        TSP 
            A timeseries profile (TSP) object
        """
        times = pd.date_range(start=start, end=end).to_pydatetime()
        t_sec = np.array([(t-times[0]).total_seconds() for t in times])
        
        values = analytical_fourier(depths=depths, times=t_sec, Q=Q, c=c, k=k, A=A, MAGST=MAGST)
        
        this = cls(depths=depths, times=times, values=values)
        
        return this

    def plot_trumpet(self, year: Optional[int]=None, begin: Optional[datetime]=None, end: Optional[datetime]=None, **kwargs) -> 'matplotlib.figure.Figure':
        """ Create a trumpet plot from the data
        
        Parameters
        ----------
        year : int, optional
            Which year to plot
        begin : datetime, optional
            If 'end' also provided, the earliest measurement to include in the averaging for the plot
        end : datetime, optional
            If 'begin' also provided, the latest measurement to include in the averaging for the plot
        **kwargs : dict, optional
            Extra arguments to the plotting function: refer to the documentation for :func:`~teaspoon.plots.static.trumpet_curve` for a
            list of all possible arguments.

        Returns
        -------
        Figure
            a matplotlib `Figure` object
        """
        df = self.long.dropna()
        grouped = df.groupby('depth')
        if year is not None:
            df = df[df['time'].dt.year == year]
        
        elif begin is not None or end is not None:
            pass
        
        else:
            raise ValueError("One of 'year', 'begin', 'end' must be provided.")

        max_t = grouped.max().get('temperature_in_ground').values
        min_t = grouped.min().get('temperature_in_ground').values
        mean_t = grouped.mean().get('temperature_in_ground').values
        depth = np.array([d for d in grouped.groups.keys()])

        fig = trumpet_curve(depth=depth, t_max=max_t, t_min=min_t, t_mean=mean_t, **kwargs)
        fig.show()

        return fig
    
    def plot_contour(self, **kwargs) -> 'matplotlib.figure.Figure':
        """ Create a contour plot
        
        Parameters
        ----------
        **kwargs : dict, optional
            Extra arguments to the plotting function: refer to the documentation for :func:`~teaspoon.plots.static.colour_contour` for a
            list of all possible arguments.

        Returns
        -------
        Figure
            matplotlib `Figure` object
        """
        fig = colour_contour(depths=self.depths, times=self.times, values=self._values, **kwargs)
        fig.show()

        return fig

    def plot_timeseries(self, depths: list=[], **kwargs) -> 'matplotlib.figure.Figure':
        """Create a time series T(t) plot 

        Parameters
        ----------
        depths : list, optional
            If non-empty, restricts the depths to include in the plot, by default []
        **kwargs : dict, optional
            Extra arguments to the plotting function: refer to the documentation for :func:`~teaspoon.plots.static.time_series` for a
            list of all possible arguments.

        Returns
        -------
        Figure
            matplotlib `Figure` object
        """
        if depths == []:
            depths = self.depths
        
        d_mask = np.isin(self.depths, depths)
        
        fig = time_series(self.depths[d_mask], self.times, self.values[:, d_mask], **kwargs)
        
        fig.show()
        
        return fig


class IndexedTSP(TSP):
    """ A Time Series Profile that uses indices (1,2,3,...) instead of depth values. 
    
    Used in situations when depths are unknown (such as when reading datlogger exports
    that don't have depth measurements.)
    
    Parameters
    ----------
    times : list-like
        t-length array of datetime objects
    values : numpy.ndarray
        array with shape (t,d) containing values at (t)emperatures and (d)epths
    **kwargs : dict
        Extra arguments to parent class: refer to :py:class:`teaspoon.TSP` documentation for a
        list of all possible arguments.
    """

    def __init__(self, times, values, **kwargs):
        depths = np.arange(0, values.shape[1]) + 1
        super().__init__(times=times, depths=depths, values=values, **kwargs)

    @property
    def depths(self) -> np.ndarray:
        """Depth indices 

        Returns
        -------
        numpy.ndarray
            An array of depth indices
        """
        warnings.warn("This TSP uses indices (1,2,3,...) instad of depths. Use set_depths() to use measured depths.")
        return self._depths

    @depths.setter
    def depths(self, value):
        TSP.depths.__set__(self, value)

    def set_depths(self, depths: np.ndarray):
        """Assign depth values to depth indices. Change the object to a :py:class:`teaspoon.TSP`

        Parameters
        ----------
        depths : np.ndarray
            An array or list of depth values equal in lenth to the depth indices
        """
        self.depths = depths
        self.__class__ = TSP
