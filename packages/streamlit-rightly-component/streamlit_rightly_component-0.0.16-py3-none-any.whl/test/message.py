from streamlit_rightly_component import rightly_component, set_debug, instance
import pandas as pd

set_debug(False, 'http://127.0.0.1:3001')

result = rightly_component(component_name="LuckSheet", data={}, events={
  "dispatchs": [{ "action": "onSave", "out": "dataframe" }]
})

result2 = rightly_component(component_name="LuckSheet", data={}, events={
  "listerens": [{ "key": "dataframe2", "out": "data" }],
}, key="luck2")

rightly_component(component_name="Pandas", data={
  "fn": """
    return {
      ...data,
      data: {
        ...data.data,
        value: {
          0: data.data.value[0] + 1,
        },
      },
    };
  """
}, events={
  "dispatchs": [{ "action": "onSave", "out": "dataframe2" }],
  "listerens": [{ "key": "dataframe", "out": "data" }],
})

if result2 and result2['action'] == 'onSave':
  print(result2['data'])
  df2 = pd.DataFrame(data=result2['data'])
  print(df2.head(5))