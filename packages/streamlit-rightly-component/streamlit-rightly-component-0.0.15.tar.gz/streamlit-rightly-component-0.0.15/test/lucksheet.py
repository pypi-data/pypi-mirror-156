from streamlit_rightly_component import rightly_component, set_debug, instance
import pandas as pd

# set_debug(False, 'http://127.0.0.1:3001')

d = {'id': [1, 2], 'value': [3, 4]}
df = pd.DataFrame(data=d)

result = rightly_component(component_name="LuckSheet", data={
  "data": df.to_json(),
  "cells": ['id', { 'index': 'value', 'name': 'uv' }]
})

if result and result['action'] == 'onSave':
  print(result['data'])
  df2 = pd.DataFrame(data=result['data'])
  print(df2.head(5))