
'''
Este script define una serie de métodos y clases para ayudar a cargar contenido dinámico
de una página ejecutando javascript y usando el módulo splash.

El contenido dinámico puede obtenerse interactuando con el DOM de la página (como un usuario
normal) y realizando acciones sobre este (clickear o escribir en un elemento)

Se proveen las siguientes clases de utilidad, que representan posibles acciones en la página:

- Wait(x) : Para x segundos
- SendText(selector, text) : Escribe un texto a un elemento de tipo input indicando su selector 
- Click(selector) : Clickea en un elemento indicando su selector
- AllElementsReady([selector1, selector2, ...]) : Espera hasta que al menos un elemento que encaje
    con cada selector existan en el DOM de la página
- ElementReady(selector) = AllElementsReady([selector])


Ejemplo para crear un script:
actions = Wait(2) + Click('#first-element') + ElementReady('#new-element-appeared') +
    SendText('#first-element', 'New element appeared!')
    
Este script hace lo siguiente:
- Espera dos segundos
- clickea en el elemento con el selector "#first-element",
- Espera a que "#new-element-appeared" exista en el DOM
- Se envía el texto "New element appeared!" al elemento con el selector "#first-element"


Para ejecutar la request con el script...
yield splash_request(url = ..., callback = ..., actions = actions)

'''


from os.path import dirname, join
from scrapy_splash import SplashRequest
from urllib.parse import urlencode
import logging



# ----- FUNCIONES DE UTILIDAD ------

def stringify(values):
    '''
    Método de utilidad para convertir valores que serán hardcodeados dentro de trozos de
    código LUA o JS, a formato String (escapando los caracteres " y ' si los valores son strings)
    '''
    def _stringify(value):
        if value is None:
            return None
        if isinstance(value, str):
            #return '"{}"'.format(value.replace('"', '\\"').replace("'", "\\'"))
            return ' +\n'.join(['"{}"'.format(line.replace('"', '\\"').replace("'", "\\'")) for line in value.split('\n')])
        return str(value)

    if values is None:
        return None
    if not isinstance(values, list):
        value = values
        return _stringify(value)
    return [_stringify(value) for value in values]



# ----- UTILIDADES PARA LA GENERACIÓN DE CÓDIGO EN JAVASCRIPT ------


class Code:
    '''
    Representa un trozo de código.
    '''
    def __init__(self, body = ''):
        self.body = str(body)

    def get_body(self):
        return self.body

    def __str__(self):
        return self.get_body()

    def __add__(self, other):
        '''
        Concatena dos trozos de código.
        :param other:
        :return:
        '''
        return Code('{}\n{}'.format(self.get_body(), other.get_body()))


class NoEscape(Code):
    '''
    Se usar para encapsular cadenas de caracteres que no deben ser escapadas (por ejemplo
    para indicar nombres de variables en el código JS o LUA)
    e.g:
    >text = ' Message: "Hello World" '
    >stringify(text) => '\" Message: \"Hello World\" \"'
    >stringify(NoEscape(text)) == text => ' Message: "Hello World" '
    '''
    def __init__(self, something):
        self.something = something

    def __str__(self):
        return str(self.something)




class JSFunctionCode(Code):
    '''
    Representa el código de la definición de una clase en Javascript.
    e.g:
    >f = JSFunctionCode(name = 'foo', params = ['a', 'b', 'c'], body = 'doSomething();', return_value = 'Nothing')
    >str(f) =
    "function foo(a, b, c) {
        doSomething();
        return 'Nothing'
    }"
    '''
    def __init__(self, name = None, body = '', params = [], return_value = None):
        '''
        Inicializa la instancia
        :param name: Será el nombre del método
        :param body: Será el trozo de código dentro del método
        :param params: Un listado con los argumentos del método
        '''
        return_value = stringify(return_value)
        code = ('function {} ({}) {{\n' \
               '{}\n' \
               '}}').format(name if not name is None else '', ', '.join([str(param) for param in params]),
                            body if return_value is None else '{}\nreturn {}'.format(body, return_value))
        super().__init__(code)



class JSFunctionCallCode(Code):
    '''
    Es una clase que representa una llamada a un método JS
    e.g:
    >call = JSFunctionCallCode(name = 'foo', args = [1, 2, 3, 'Hello World'])
    >str(call)
    "foo(1, 2, 3, \"Hello World\")"
    '''
    def __init__(self, name, args = [], add_semicolon = True):
        '''
        Inicializa la instancia
        :param name: Es el nombre del método invocado
        :param args: Son los argumentos que deben indicarse.
        :param add_semicolon: Indica si debe añadirse el símbolo ";" al final de la llamada
        al método. Por defecto es True
        '''
        args = stringify(args)
        code = '{}({})'.format(name, ', '.join(args))
        if add_semicolon:
            code += ';'
        super().__init__(code)



class JSObjectMethodCallCode(Code):
    '''
    Representa la llamada a un método de clase en JS
    e.g:
    >call = JSObectMethodCallCode(object = 'robot', method = 'live', args = [1, 2, 3])
    >str(call)
        "robot.live(1, 2, 3)"

    '''
    def __init__(self, object, method, args = [], add_semicolon = True):
        '''
        Inicializa la instancia
        :param object: Es una instancia de una clase
        :param method: Es el nombre método de clase a invocar
        :param args: Son los argumentos que se indicarán en la llamada
        :param add_semicolon: Indica si debe añadirse el símbolo ";" al final de la llamada
        al método. Por defecto es True
        '''
        args = stringify(args)
        code = '{}.{}({})'.format(object, method, ', '.join(args))
        if add_semicolon:
            code += ';'
        super().__init__(code)



class JSAppendHTMLToElementCode(JSObjectMethodCallCode):
    '''
    Genera un trozo de código JS para añadir HTML al contenido de un elemento en el DOM
    e.g:
    > str(JSAppendHTMLToElementCode(selector = 'body', arg = '<span>Hello World!</span>'))
    "$(\"body\").append(\"<span>Hello World!</span>\")"

    '''
    def __init__(self, selector, arg):
        '''
        Inicializa la instancia
        :param selector: Es un selector jQuery
        :param arg: Es el argumento a pasar a la llamada de jQuery.append
        '''
        super().__init__(object = 'jQuery({})'.format(stringify(selector)),
                         method = 'append',
                         args = [arg])


class JSCodeWrapper:
    '''
    Esta clase permite encapsular código javascript para poder escribirlo en un script
    lua como una cadena de caracteres.
    e.g:
    >str(JSCodeWrapper(JSFunctionCode(name = 'foo', body = 'doSomething();')))
    "[[function foo() {
        doSomething();
    }]]"
    '''
    def __init__(self, code):
        '''
        Inicializa la instancia
        :param code: Es el código a encapsular.
        '''
        self.wrapper = '[[{}]]'.format(code)

    def __str__(self):
        return self.wrapper



# ----- UTILIDADES PARA LA GENERACIÓN DE CÓDIGO EN LUA ------


class LuaFunctionCode(Code):
    '''
    Representa la definición de un método en LUA
    e.g:
    >str(LuaFunctionCode(name = 'foo', body = 'doSomething()', params = ['a', 'b', 'c']))
    "function foo (a, b, c)
        doSomething()
    end"
    '''
    def __init__(self, name = None, body = '', params = [], return_value = None):
        '''
        Inicializa la instancia
        :param name: Es el nombre del método
        :param body: Es el código del cuerpo del método.
        :param params: Son los parámetros que recibirá el método.
        :param return_value: Es el valor de retorno del método, por defecto ninguno.
        '''
        return_value = stringify(return_value)
        code = ('function {} ({})\n' \
               '{}\n' \
               'end').format(name if not name is None else '', ', '.join([str(param) for param in params]),
                             body if return_value is None else '{}\nreturn {}'.format(body, return_value))
        super().__init__(code)



class LuaObjectMethodCallCode(Code):
    '''
    Representa una llamada a un método de clase en LUA
    e.g:
    >str(LuaObjectMethodCallCode(object = 'robot', method = 'live', args = [1, 2, 3]),surround_with_assert = False)
    "robot:live(1, 2, 3)"
    >str(LuaObjectMethodCallCode(object = 'robot', method = 'live', args = [1, 2, 3]),surround_with_assert = True)
    "assert(robot:live(1, 2, 3))"
    '''
    def __init__(self, object, method, args = [], surround_with_assert = True):
        '''
        Inicializa la instancia
        :param object: Es el nombre del objeto
        :param method: Es el nombre del método de clase
        :param args: Son los parámetros a indicar como argumentos-
        :param surround_with_assert: Si es True, la llamada se encapsulará en una sentencia
        del tipo assert(...)
        '''
        args = stringify(args)
        code = '{}:{}({})'.format(object, method, ', '.join(args))
        if surround_with_assert:
            code = 'assert({})'.format(code)

        super().__init__(code)



# ----- UTILIDADES PARA LA GENERACIÓN DE CÓDIGO CON SPLASH Y LUA ------


class SplashWaitForResumeCode(LuaObjectMethodCallCode):
    '''
    Permite generar una llamada al método de clase splash:wait_for_resume, pasandole como
    parámetro un código en JS
    '''
    def __init__(self, js_code, timeout = None):
        '''
        :param js_code: Es código JS que se pasará como argumento a splash:wait_for_resume
        :param timeout: Permite establecer el parámetro "timeout" al llamar a splash:wait_for_resume
        '''
        js_code = JSFunctionCode(name = 'main', params = ['splash'],
                                     body = js_code)
        js_snippet = JSCodeWrapper(js_code)

        args = [NoEscape(js_snippet)]
        if not timeout is None:
            args.append(timeout)

        super().__init__(object = 'splash', method = 'wait_for_resume', args = args)



class SplashRunCode(LuaObjectMethodCallCode):
    '''
    Permite generar una llamada al método de clase splash:runjs, pasandole como parámetro
    un código en JS
    '''
    def __init__(self, js_code):
        js_snippet = JSCodeWrapper(js_code)
        args = [NoEscape(js_snippet)]

        super().__init__(object = 'splash', method = 'runjs', args = args)


class SplashGetElementCode(LuaObjectMethodCallCode):
    def __init__(self, selector):
        super().__init__(object = 'splash', method = 'select', args = [selector])



# ----- UTILIDADES PARA INTERACTUAR CON EL DOM DE LA PÁGINA ------



class DOMEventListenerCode(SplashWaitForResumeCode):
    '''
    Esta clase se encarga de generar el código en LUA para un script con el objetivo de
    pausar la ejecución del mismo hasta que un evento en el DOM de la web ocurra.
    No debe instanciarse. Cree objetos de alguna de sus subclases.
    '''
    def __init__(self, selectors = [], timeout = None):
        self.selectors = stringify(selectors)


        callback_method_name = '__callback'
        registration_method_name = '__register'
        register_callback_code = self.get_register_callback_code(NoEscape(callback_method_name))

        js_code = JSFunctionCode(name = registration_method_name,
                                 body = register_callback_code) +\
                  JSFunctionCode(name = callback_method_name,
                                 body = JSObjectMethodCallCode(object = 'splash', method = 'resume')) +\
                  JSFunctionCallCode(name = registration_method_name)

        super().__init__(js_code, timeout)

    def get_selectors(self):
        return self.selectors

    def get_register_callback_code(self, callback_method_name):
        return ''




class ElementsReady(DOMEventListenerCode):
    '''
    Esta clase genera código para que la ejecución de un script se pausé y se resuma hasta que un
    conjunto de elementos están disponibles en el DOM
    e.g:
    ElementsReady(['p', 'ul', '#some-element'])
    Espera a que haya al menos un párrafo, una lista y un elemento con la id "some-element"

    '''
    def __init__(self, selectors = []):
        '''
        Inicializa la instancia.
        :param selectors: Es un conjunto de selectores para jQuery
        Si el script ejecuta el código generado, la ejecución se pausará hasta que al menos un
        elemento que encaje con cada selector indicado esté disponible en el DOM
        '''
        super().__init__(selectors)

    def get_register_callback_code(self, callback_method_name):
        return JSFunctionCallCode(name = 'allElementsAvaliable',
                                  args = [NoEscape('[{}]'.format(', '.join(self.get_selectors()))), callback_method_name])


class ElementReady(ElementsReady):
    '''
    Es igual que ElementsReady, pero solo se especifica un selector.
    '''
    def __init__(self, selector):
        super().__init__([selector])



class InputElementHasValue(DOMEventListenerCode):
    '''
    Esta clase genera código para un script. Al ser ejecutado tal código, pausa la ejecución
    hasta que un elemento (de tipo input), tenga el valor indicado como parámetro.
    '''
    def __init__(self, selector, value):
        '''
        Inicializa la instancia.
        :param selector: Es el selector del elemento
        :param value: Es el valor que debe tener el elemento antes de que la ejecución del script
        se reaunde
        '''
        self.value = value
        super().__init__([selector])

    def get_value(self):
        return self.value

    def get_register_callback_code(self, callback_method_name):
        return JSFunctionCallCode(name = 'onInputHasValue',
                                  args = [NoEscape(self.get_selectors()[0]), self.get_value(), callback_method_name])



class Click(Code):
    '''
    Es una clase que sirve para generar código que de ser ejecutado, se simulará un click sobre
    un elemento del DOM. Después de ejecutar el código generado, se garantiza que se haya clickeado
    sobre el elemento indicado (en caso contrario, la ejecución queda pausada)

    e.g:
    Click('#my-button')
    Espera a que un elemento con el selector "my-button" esté en el DOM de la página y luego lo
    clickea.
    '''
    def __init__(self, selector):
        '''
        Inicializa la instancia
        :param selector: Es el selector del elemento
        '''
        code = ElementReady(selector) +\
               LuaObjectMethodCallCode(object = SplashGetElementCode(selector), method = 'mouse_click')
        super().__init__(code)


class SendText(Code):
    '''
    Es una clase que sirve para generar código que de ser ejecutado, escribe sobre un elemento del
    DOM (de tipo input)
    La ejecución queda pausada hasta garantizar que el elemento sobre el que se ha escrito, tiene
    el valor indicado como parámetro.

    e.g:
    SendText('#my-input', 'Hello World!')
    Espera a que haya un elemento cuya ID es "my-input" en el DOM, y luego escribe sobre él,
    el texto "Hello World!" letra a letra. La ejecución finaliza cuando el valor del input coincide
    con el texto: $('#my-input').val() === 'Hello World!'

    '''
    def __init__(self, selector, text):
        '''
        Inicializa la instancia
        :param selector: Es el selector del elemento
        :param text: Es el texto ha escribir en el elemento
        '''

        code = ElementReady(selector) +\
               LuaObjectMethodCallCode(object = SplashGetElementCode(selector), method = 'send_text', args = [text]) +\
               InputElementHasValue(selector=selector, value=text)

        super().__init__(code)


class Wait(Code):
    '''
    Clase que genera un código que para la ejecución del mismo al ejecutarse durante un periódo
    de tiempo específico.

    e.g:
    ElementReady('#some-element') + Wait(2) + Click('#another-element')
    Se espera a que el elemento con la ID "some-element" esté en el DOM y luego, pasados 2 segundos,
    se clickea sobre el elemento cuya ID es "another-element"
    '''
    def __init__(self, amount):
        code = LuaObjectMethodCallCode(object = 'splash', method = 'wait', args = [amount])
        super().__init__(code)



# ----- UTILIDADES PARA DEPURAR LA CARGA DE CONTENIDO DINÁMICO CON SPLASH ------



class DebugMessage(Code):
    '''
    Esta clase genera un código para imprimir un mensaje de depuración en el DOM de la página.
    e.g:
    Debug('Hello World!') imprime "Hello World!" en el panel de depuración.
     '''
    def __init__(self, message):
        '''
        Inicializa la instancia.
        :param message: Es un mensaje a imprimir
        '''

        code = SplashRunCode(JSAppendHTMLToElementCode(selector = '#debug_messages',
                                                       arg = '<li>INFO: {}</li>'.format(message)))
        super().__init__(code)


class JSDebugCode(Code):
    '''
    Esta clase genera un código para imprimir un mensaje de depuración en el DOM que se obtiene
    como resultado de evaluar código JS (en una línea)
    e.g:
    Debug('len($("p"))') imprime el número de párrafos en el DOM en el panel de depuración.
    '''
    def __init__(self, js_code):
        code = SplashRunCode(JSAppendHTMLToElementCode(selector = '#debug_messages',
                                                       arg = '<li>{}</li>'.format(js_code)))

        text = '{} + {} + {}'.format(stringify('<li class="script-result">'), js_code , stringify('</li>'))
        code += SplashRunCode(JSAppendHTMLToElementCode(selector = '#debug_messages',
                                                        arg = NoEscape(text)))
        super().__init__(code)

class JSDebugElement(JSDebugCode):
    '''
    Esta clase genera código para añadir un mensaje en el panel de depuración, que muestre
    información sobre uno o varios elementos del DOM
    '''
    def __init__(self, selector):

        super().__init__('jQuery({})'.format(stringify(selector)))

class DebugPanel(Code):
    '''
    Esta clase genera código para crear un elemento en el DOM de la página donde se van añadiendo
    mensajes de depuración.
    '''
    def __init__(self):
        panel = """
        <div class="shell-wrap" id="debug_panel">
            <p class="shell-top-bar">Debug from Splash</p>
            <ul class="shell-body" id="debug_messages">
            </ul>
        </div>
        """
        code = SplashRunCode(JSAppendHTMLToElementCode(selector = 'body',
                                                       arg = panel))

        # Añadimos estilos css al panel de depuración.
        with open(join(dirname(__file__), 'static', 'css', 'debug_panel.css')) as fh:
            styles = fh.read()
            code += SplashRunCode(JSAppendHTMLToElementCode(selector = 'body',
                                                            arg = '<style>{}</style>'.format(styles)))

        super().__init__(code)



class LuaSplashScript(Code):
    '''
    Genera un script en lua que ejecuta una serie de acciones sobre el DOM de la página que procesará,
    antes de servirla.
    e.g:
    actions = Click('#first-element') + SendText('#second-element', 'some-value')
    script = LuaSplashScript(actions)
    '''
    def __init__(self, actions = None):
        '''
        Inicializa la instancia.
        :param actions: Son las acciones a realizar por el script.
        '''

        if actions is None:
            actions = Code()
        debug_panel = DebugPanel()
        main_method_body = LuaObjectMethodCallCode(object = 'splash', method = 'go', args = [NoEscape('splash.args.url')]) +\
                           LuaObjectMethodCallCode(object = 'splash', method = 'runjs', args = [NoEscape('splash.args.jquery')]) +\
                           LuaObjectMethodCallCode(object = 'splash', method = 'runjs', args = [NoEscape('splash.args.scrap_utils')]) + \
                           debug_panel + actions

        code = LuaFunctionCode(name = 'main', params = ['splash'],
                               body = main_method_body,
                               return_value = LuaObjectMethodCallCode(object = 'splash', method = 'html', surround_with_assert = False))



        # Formatear las cadenas de caracteres.

        super().__init__(code)


def splash_request(url, callback, actions = None, **kwargs):
    '''
    Realiza una petición a la página cuya url se indica como parámetro y devuelve una instancia
    de la clase Request como valor de retorno.
    Pero antes de servir la página, pueden ejecutarse una serie de acciones como un usuario:
    clickear en un elemento, escribir en un input, ... e.t.c
    Se genera un script en LUA a partir de una secuencia de acciones, que a su vez ejecuta JS
    para interactuar con el DOM.

    e.g:
        splash_request('https://google.com', callback = parse,
        actions = Click('#search-bar') + SendText('#search-bar', 'Why pigs dont fly?'))

    :param url: Es la url de la página
    :param callback: Es un callback que scrapeará la página
    :param actions: Es un listado de acciones a realizar antes de servir la página. Permite crear
    un usuario virtual que pueda interactuar con la web para cargar contenido dinámico.
    '''

    def read_js_script(path):
        with open(join(dirname(__file__), 'static', 'js', path)) as fh:
            return fh.read()

    code = LuaSplashScript(actions)
    return SplashRequest(callback=callback,
                         endpoint='execute',
                         args={
                             'lua_source': str(code),
                             'url': url,
                             'scrap_utils': read_js_script('scrap_utils.js'),
                             'jquery': read_js_script('jquery.min.js')
                         },
                         **kwargs)