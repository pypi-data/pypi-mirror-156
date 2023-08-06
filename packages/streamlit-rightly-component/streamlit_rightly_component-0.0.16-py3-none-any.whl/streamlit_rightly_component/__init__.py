import os
import streamlit.components.v1 as components
import streamlit as st

class RightlyComponent:
    def __init__(self):
        self._RELEASE = True
        self.url = 'http://localhost:3001'
        self._component_func = self.get_component_func()
    
    def set_debug(self, release = False, url = 'http://localhost:3001'):
        self._RELEASE = release
        self.url = url
        self._component_func = self.get_component_func()

    def get_component_func(self):
        if not self._RELEASE:
            _component_func = components.declare_component(
                # We give the component a simple, descriptive name ("my_component"
                # does not fit this bill, so please choose something better for your
                # own component :)
                "rightly_component",
                # Pass `url` here to tell Streamlit that the component will be served
                # by the local dev server that you run via `npm run start`.
                # (This is useful while your component is in development.)
                url=self.url,
            )
        else:
            # When we're distributing a production version of the component, we'll
            # replace the `url` param with `path`, and point it to to the component's
            # build directory:
            parent_dir = os.path.dirname(os.path.abspath(__file__))
            build_dir = os.path.join(parent_dir, "frontend/build")
            _component_func = components.declare_component("rightly_component", path=build_dir)
        return _component_func

    def initEvent(self):
        if 'init_event' in st.session_state:
            return
        st.session_state['init_event'] = True
        components.html('''
            <script>
                let listerens = [];
                window.parent.addEventListener('message', (event) => {
                    const { type } = event.data;
                    if (type === 'component-message-dispatch') {
                        // 广播
                        console.log('[dispatch]');
                        listerens.forEach(listeren => listeren.postMessage(event.data, '*'))
                    }
                    if (type === 'component-message-listeren') {
                        console.log('[listeren]');
                        listerens.push(event.source);
                    }
                });
                const iframs = window.parent.document.getElementsByTagName('iframe');
                Array.from(iframs).forEach(iframe => {
                    const srcdoc = iframe.srcdoc;
                    if (srcdoc.includes('window.parent.document')) {
                        iframe.style.display = 'none';
                    }
                })
            </script>
        ''')

    def rightly_component(self, component_name, data = {}, default = {}, key = None, events = None):
        if events is not None:
            self.initEvent()
        component_value = self._component_func(componentName=component_name, data=data, key=key or component_name, default=default, events=events)
        # We could modify the value returned from the component if we wanted.
        # There's no need to do this in our simple example - but it's an option.
        return component_value

    def modal():
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
            #modal {
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
                width: 600px;
                left: 50%;
                top: 50%;
                z-index: 1;
                transform: translate(-50%, -50%);
            }
            
            </style>''', unsafe_allow_html=True)
        
        close = st.button('关闭浮层')
        if close:
            st.write('''<style>#modal {
                        display: none;
                    }</style>''', unsafe_allow_html=True)
            return {"action": "close"}

        return None


instance = RightlyComponent()

def rightly_component(component_name, data = {}, default = None, key = None, events=None):
    return instance.rightly_component(component_name, data, default, key, events)

def set_debug(release = False, url = 'http://localhost:3001'):
    return instance.set_debug(release, url)

class modal:
    def __init__(self, close_fn = None):
        self.action = None
        self.container = None
        self.content_container = None
        self.close_fn = close_fn

    def __enter__(self):
        self.container = st.container()
        self.container.markdown('<div id="modal-mask"></div>', unsafe_allow_html=True)
        with self.container:
          components.html('''
              <script>
                  var d = window.parent.document;
                  var b = d.getElementById('modal-mask');
                  var c = b.parentNode.parentNode.parentNode.parentNode;
                  c.id += 'modal';
                  console.log(c.className)
              </script>
          ''')
        self.container.write('''<style>
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

            #modal > .element-container:last-child {
                display: block;
                position: absolute;
                left: calc(50% + 200px);
                top: 50%;
                z-index: 2;
            }

            #modal > div:nth-child(4) > div > div {
              width: 100%;
            }

            #modal > div:nth-child(4) > div > div > div {
              width: 100%;
            }

            #modal > div:nth-child(4) > div > div > iframe {
              width: 100%;
            }

            #modal > div:nth-child(4) > div > div:last-child {
              position: absolute;
              left: calc(100% - 42px);
              top: 6px;
            }

            #modal > div:nth-child(4) > div {
                display: block;
                position: absolute;
                width: 90%;
                left: 50%;
                top: 50%;
                z-index: 1;
                transform: translate(-50%, -50%);
                background: #fff;
                padding: 20px;
            }
            
            </style>''', unsafe_allow_html=True)
        self.content_container = self.container.container()
        return self.content_container

    def __exit__(self, exc_type, exc_val, exc_tb):
        close = self.content_container.button('X', kwargs={"id": "close"})
        if close:
            self.container.write('''<style>#modal {
                    display: none;
                }</style>''', unsafe_allow_html=True)
            if self.close_fn:
                self.close_fn()

            return {"action": "close"}
        return None
