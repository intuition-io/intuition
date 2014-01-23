#
# Copyright 2014 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pandas as pd


#NOTE with_market symbol, build jxr.pa => JXR:EPA
def use_google_symbol(fct):
    '''
    Removes ".PA" or other market indicator from yahoo symbol
    convention to suit google convention
    '''
    def decorator(symbols):
        google_symbols = []

        # If one symbol string
        if isinstance(symbols, str):
            symbols = [symbols]

        symbols = sorted(symbols)
        for symbol in symbols:
            dot_pos = symbol.find('.')
            google_symbols.append(
                symbol[:dot_pos] if (dot_pos > 0) else symbol)

        data = fct(google_symbols)
        data.columns = symbols
        return data
    return decorator


def invert_dataframe_axis(fct):
    '''
    Make dataframe index column names,
    and vice et versa
    '''
    def decorator(*args, **kwargs):
        df_to_invert = fct(*args, **kwargs)
        assert isinstance(df_to_invert, pd.DataFrame)
        return pd.DataFrame(df_to_invert.to_dict().values(),
                            index=df_to_invert.to_dict().keys())
    return decorator
