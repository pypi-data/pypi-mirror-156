from streamlit_rightly_component import rightly_component, set_debug
import streamlit as st
import streamlit.components.v1 as components

set_debug('http://127.0.0.1:3001')

def get_url():
    # 获取当前页面 url
    url = rightly_component(component_name='getUrl')
    return url

def render_dagre():
    st.markdown('<a href="javascript:location.hash=``;location.reload();" target="_self">点击回到首页</a>', unsafe_allow_html=True)

    nodes = []
    edges = []

    nodes.append({
        "id": "Test1",
        "label": "Test1" 
    })

    nodes.append({
        "id": "Test2",
        "label": "Test2" 
    })

    nodes.append({
        "id": "Test3",
        "label": "Test3" 
    })

    edges.append({
        "source": "Test1",
        "target": "Test2", 
    })

    edges.append({
        "source": "Test1",
        "target": "Test3", 
    })


    dagre_click = rightly_component(component_name='dagre', data={ "nodes": nodes, "edges": edges })
    print(dagre_click)
    rightly_component(component_name='dagre', data={ "nodes": nodes, "edges": edges }, key="dagre2")

def render_click_demo():
    # 渲染样式有问题
    st.markdown('<a href="javascript:location.hash=``;location.reload();" target="_self">点击回到首页</a>', unsafe_allow_html=True)

    st.subheader("Component with constant args")
    num_clicks = rightly_component(component_name="ClickDemo", data={'name': 'click-demo'},  default=0)
    st.markdown("You've clicked %s times!" % int(num_clicks))


url = get_url()
if url and 'click-demo' in url:
    render_click_demo()
elif url and 'dagre' in url:
    render_dagre()
elif url:
    st.markdown('<a href="javascript:location.hash=`click-demo`;location.reload();" target="_self">点击跳转 click-demo</a>', unsafe_allow_html=True)
    st.markdown('<a href="javascript:location.hash=`dagre`;location.reload();" target="_self">点击跳转 Dagre</a>', unsafe_allow_html=True)
