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


def st_modal():
    st.markdown('<div id="modal-mask"></div>', unsafe_allow_html=True)
    components.html('''
        <script>
            var d = window.parent.document;
            var b = d.getElementById('modal-mask');
            var c = b.parentNode.parentNode.parentNode.parentNode;
            c.id += 'modal';
            console.log(c.className)
        </script>
    ''')
    st.write('''<style>
        .appview-container > section > div > div > div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
            display: none;
        }

        #modal {
            display: block;
            position: fixed;
            left: 0;
            top: 0;
            z-index: 900;
            width: 100%;
            height: 100%;
        }

        #modal > div:nth-child(-n + 3) {
            display: none;
        }

        #modal > div:first-child {
            display: block;
            width: 100%;
            height: 100%;
            background: rgba(333, 333, 333, 0.5);
        }

        #modal > div:nth-child(4) {
            position: absolute;
            left: calc(50% + 200px);
            top: 50%;
            z-index: 2;
        }

        #modal > div:nth-child(5) > div {
            position: absolute;
            width: 600px;
            left: 50%;
            top: 50%;
            z-index: 1;
            transform: translate(-50%, -50%);
            background: #fff;
            padding: 20px;
        }
        
        </style>''', unsafe_allow_html=True)
    
    close = st.button('关闭浮层')
    if close:
        st.write('''<style>#modal {
                    display: none;
                }</style>''', unsafe_allow_html=True)
        return {"action": "close"}

    return None

# class modal:
#     def __init__(self):
#         self.action = None

#     def __enter__(self):
#         st.markdown('<div id="modal-mask"></div>', unsafe_allow_html=True)
#         components.html('''
#             <script>
#                 var d = window.parent.document;
#                 var b = d.getElementById('modal-mask');
#                 var c = b.parentNode.parentNode.parentNode.parentNode;
#                 c.id += 'modal';
#                 console.log(c.className)
#             </script>
#         ''')
#         st.write('''<style>
#             #modal {
#                 position: fixed;
#                 left: 0;
#                 top: 0;
#                 z-index: 900;
#                 width: 100%;
#                 height: 100%;
#             }

#             #modal > div {
#                 display: none;
#             }

#             #modal > div:first-child {
#                 display: block;
#                 width: 100%;
#                 height: 100%;
#                 background: rgba(333, 333, 333, 0.5);
#             }

#             #modal > .element-container:last-child {
#                 display: block;
#                 position: absolute;
#                 left: calc(50% + 200px);
#                 top: 50%;
#                 z-index: 2;
#             }

#             #modal > div:nth-child(5) {
#                 display: block;
#                 position: absolute;
#                 left: calc(50% + 200px);
#                 top: 50%;
#                 z-index: 2;
#             }

#             #modal > div:nth-child(4) > div {
#                 display: block;
#                 position: absolute;
#                 width: 600px;
#                 left: 50%;
#                 top: 50%;
#                 z-index: 1;
#                 transform: translate(-50%, -50%);
#                 background: #fff;
#                 padding: 20px;
#             }
            
#             </style>''', unsafe_allow_html=True)

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         close = st.button('关闭浮层', kwargs={"id": "close"})
#         if close:
#             st.write('''<style>#modal {
#                     display: none;
#                 }</style>''', unsafe_allow_html=True)
#             return {"action": "close"}
#         return None

def render_modal():
    open = st.button('点击展示浮层')


    if 'open_modal' in st.session_state:
        open = st.session_state['open_modal']

    if open:
        # with st.container():
        #     with modal() as m:
        #         with st.container():
        #             st.markdown('这是一个浮动')
        #             st.button('233')
        #         print(m)

        st.session_state['open_modal'] = True
        with st.container():
            result = st_modal()

            if result and result['action'] == "close":
                del st.session_state['open_modal']

            with st.container():
                st.markdown('这是一个浮层')
                st.button('233')


url = get_url()
if url and 'click-demo' in url:
    render_click_demo()
elif url and 'dagre' in url:
    render_dagre()
elif url and 'modal' in url:
    render_modal()
elif url:
    st.markdown('<a href="javascript:location.hash=`click-demo`;location.reload();" target="_self">点击跳转 click-demo</a>', unsafe_allow_html=True)
    st.markdown('<a href="javascript:location.hash=`dagre`;location.reload();" target="_self">点击跳转 Dagre</a>', unsafe_allow_html=True)
