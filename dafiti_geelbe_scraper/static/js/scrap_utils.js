
/**
Si esta activado el sandboxing y la página web a scrapear está embebida en un iframe,
redefinimos $...
*/

callback_wrapper = function(callback) {
    this.callback = callback;
}

callback_wrapper.prototype.executeWhen = function(condition) {
    if(condition())
        this.callback();
    else
    {
        var wrapper = this;
        var checkInterval = 10
        var interval = setInterval(function() {
            if(condition()) {
                clearInterval(interval);
                wrapper.callback();
            }
        }, checkInterval);
    }
}

callback_wrapper.prototype.executeWhenElementAvaliable = function(selector) {
    this.executeWhen(function() {
        return $(selector).length > 0;
    });
}


callback_wrapper.prototype.executeWhenAllElementsAvaliable = function(selectors) {
    if(selectors.length == 0) {
        this.callback();
    }
    else if(selectors.length == 1) {
        this.executeWhenElementAvaliable(selectors[0]);
    }
    else
    {
        var selectors = selectors.slice();
        var selector = selectors.pop();

        var wrapper = this;
        var another_wrapper = new callback_wrapper(function() {
            wrapper.executeWhenElementAvaliable(selector);
        });
        another_wrapper.executeWhenAllElementsAvaliable(selectors);
    }
}

callback_wrapper.prototype.executeWhenInputHasValue = function(selector, value) {
    this.executeWhen(function() {
        return $(selector).val() === value;
    });
}



/**
Este método ejecuta el callback cuando se añade un elemento que encaje con el selector especificado.
Si ya existe algún elemento que encaje con este, se llama al callback inmediatamente.
*/
onElementAvaliable = function(selector, callback) {
    var wrapper = new callback_wrapper(callback);
    wrapper.executeWhenElementAvaliable(selector);
}


/**
Es igual que onElementAvaliable, solo que en vez de pasar un selector, se pasa una lista de selectores.
El callback se ejecutará cuando esté disponible al menos 1 elemento del DOM que encaje con cada
uno de los selectores indicados.
*/
allElementsAvaliable = function(selectors, callback) {
    var wrapper = new callback_wrapper(callback);
    wrapper.executeWhenAllElementsAvaliable(selectors);
}




/**
Este método llama al callback pasado como argumento cuando el elemento de tipo input cuyo selector
también se indica, tenga el valor especificado
*/
onInputHasValue = function(selector, value, callback) {
    var wrapper = new callback_wrapper(callback);
    wrapper.executeWhenInputHasValue(selector, value);
}
