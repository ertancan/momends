var Momend = (function(){
    var _jsAnimate = new JSAnimate();
    var _momend_data;
    var created_objects;
    var fullscreen = false;
    var page_redirect_function;
    var _interaction_sent = false;
    var total_objects = 0;
    var loaded_objects = 0;
    var _load_callback;

    function init(){
        _jsAnimate.initAnimation();
    }
    function _momendArrived(momend_data){
        _momend_data = momend_data;
        _jsAnimate.reCalculateDimensions(); //Since they may be needed while creating objects
        if(!_momend_data || _momend_data.length == 0 || _momend_data['error']){
            _loadFailed();
        }else{
            _createObjectsFromData(_startAnimation); //start animation as create objects callback
        }
    }
    function _startAnimation(){
        _jsAnimate.setAnimationQueue(_momend_data['animation_layers']);
        $('#loading-bg').animate({
            'top':'-100%',
            'opacity' : '0.5'
        },{
            duration: 500,
            complete: function(){
                $(this).hide();
            }
        });
        setTimeout(function(){
            _jsAnimate.startAllQueues();
        },500);
    }
    /**
     * Send the queue generated while user interacts with the animation to the given url
     * Needs the CSRF token to be on the player's codes
     * fills id and queue parameters of the request
     * @param url that listens post requests and saves interaction
     * @param callback function to be called when request finished
     * @private
     */
    function _sendUserInteractionToServer(url, callback){
        if(_interaction_sent){
            return;
        }
        console.log('sending')
        var json = _jsAnimate.convertUserInteractionLayerToJSON();
        var token = $('[name="csrfmiddlewaretoken"]')[0].value;
        var momend_id = _momend_data['id'];
        $.ajax({
            type: 'POST',
            url: url,
            beforeSend: function(xhr){xhr.setRequestHeader('X-CSRFToken', token);},
            data: {
                'queue':json,
                'id':momend_id
            },
            success: function(msg){
                var data = jQuery.parseJSON(msg);
                if(callback){
                    if(data.resp === true){
                        callback(true,data.url);
                    }else{
                        callback(false,data.msg);
                    }
                }
                _interaction_sent = true;
            },
            error: function(msg){
                var data = jQuery.parseJSON(msg);
                if(callback){
                    callback(false,data.msg);
                }
            }
        });
    }
    function _loadFailed(){
        jQuery('<h1/>',{
            text : 'Momend could not be found!',
            class : 'error',
            id : 'error'
        }).appendTo('body');
        $('#loading-bg').hide();
    }
    function _createObjectsFromData(load_callback){
        _load_callback = load_callback;
        created_objects = {};
        for(var i = 0;i<_momend_data['animation_layers'].length;i++){
            for(var j = 0;j < _momend_data['animation_layers'][i].length;j++){
                var node = _momend_data['animation_layers'][i][j];
                var _anim = node['animation']['anim'];
                if(_anim && _anim.length > 0){
                    node['animation']['anim'] = _parseStringToDict(_anim);
                }
                var _pre = node['animation']['pre'];
                if(_pre && _pre.length > 0){
                    node['animation']['pre'] = _parseStringToDict(_pre);
                }
                var filepath = node['final_data_path'];
                var theme_filepath;
                if(filepath && filepath.indexOf('http') != 0){
                    theme_filepath = MOMEND_FILE_URL + THEME_DATA_URL + filepath;
                    filepath = MOMEND_FILE_URL + filepath;
                }
                if(node['animation']['used_theme_data'] != null){
                    if(created_objects[node['final_data_path']]){
                        node['animation']['object'] = created_objects[node['final_data_path']];
                    }else{
                        total_objects++; //Player should wait for item to load
                        jQuery('<div/>',{
                            id: 'stub'+i+''+j,
                            class: 'photo'
                        }).appendTo('.scene');
                        var created_div = $('#stub'+i+''+j);
                        var created_obj = jQuery('<img/>',{
                            class: 'photo_image',
                            id: 'stub-image'+i+''+j,
                            src: theme_filepath,
                            ready : function(){
                                __objectReady();
                            }
                        }).appendTo(created_div);
                        if(typeof node['animation']['click_animation'] !== 'undefined'){
                            created_obj.click(function(){
                                handleClick($(this));
                            });
                        }
                        if(typeof node['animation']['hover_animation'] !== 'undefined'){
                            created_obj.mouseenter(function(){
                                handleMouseEnter($(this));
                            });
                        }
                        created_objects[node['final_data_path']] = created_div;
                        node['animation']['object'] = created_objects[node['final_data_path']];
                    }
                }else{
                    switch(node['animation']['used_object_type']){
                        case '{{NEXT_THEME_BG}}':
                        case '{{RAND_THEME_BG}}':
                            total_objects++; //Player should wait for item to load
                            var created_div = jQuery('<div/>',{
                                id: 'bg'+i+''+j,
                                class: 'scene-background'
                            }).appendTo('.scene');
                            var created_pbj = jQuery('<img/>',{
                                class: 'background-image',
                                src: theme_filepath,
                                ready : function(){
                                    __objectReady();
                                }
                            }).appendTo(created_div);
                            created_objects[node['final_data_path']] = $('#bg'+i+''+j);
                        case '{{THEME_BG}}':
                            node['animation']['object'] = created_objects[node['final_data_path']];
                            break;
                        case '{{NEXT_USER_PHOTO}}':
                        case '{{RAND_USER_PHOTO}}':
                            total_objects++; //Player should wait for item to load
                            jQuery('<div/>',{
                                id: 'photo'+i+''+j,
                                class: 'photo'
                            }).appendTo('.scene');
                            var created_div = $('#photo'+i+''+j);
                            var created_obj = jQuery('<img/>',{
                                class: 'photo_image',
                                id: 'photo_image'+i+''+j,
                                src: filepath,
                                ready : function(){
                                    __objectReady();
                                }
                            }).appendTo(created_div);
                            if(typeof node['animation']['click_animation'] !== 'undefined'){
                                created_obj.click(function(){
                                    handleClick($(this));
                                });
                            }
                            if(typeof node['animation']['hover_animation'] !== 'undefined'){
                                created_obj.mouseenter(function(){
                                    handleMouseEnter($(this));
                                });
                            }
                            created_objects[node['final_data_path']] = created_div;
                        case '{{USER_PHOTO}}':
                            node['animation']['object'] = created_objects[node['final_data_path']];
                            break;

                        case '{{NEXT_USER_STATUS}}':
                        case '{{RAND_USER_STATUS}}':
                            jQuery('<div/>',{
                                id: 'status'+i+''+j,
                                class: 'status'
                            }).appendTo('.scene');
                            var created_div = $('#status'+i+''+j);
                            jQuery('<p/>',{
                                class: 'status-text',
                                text:node['data']
                            }).appendTo(created_div);
                            if(typeof node['animation']['click_animation'] !== 'undefined'){
                                created_div.click(function(){
                                    handleClick($(this));
                                });
                            }
                            if(typeof node['animation']['hover_animation'] !== 'undefined'){
                                created_div.mouseenter(function(){
                                    handleMouseEnter($(this));
                                });
                            }
                            if(node['post_enhancements']){
                                __applyPostEnhancements(created_div,node['post_enhancements']);
                            }
                            created_objects[hashCode(node['data'])] = created_div;

                        case '{{USER_STATUS}}':
                            node['animation']['object'] = created_objects[hashCode(node['data'])];
                            break;

                        case '{{NEXT_USER_MUSIC}}':
                            var _is_user_music = true;
                        case '{{NEXT_THEME_MUSIC}}':
                        case '{{RAND_THEME_MUSIC}}':
                            total_objects++; //Player should wait for item to load
                            jQuery('<div/>',{
                                id:'music'+i+''+j,
                                class:'jp-jplayer'
                            }).appendTo('.music');
                            var music_obj = $('#music'+i+''+j);
                            music_obj[0]['filepath'] = node['final_data_path'];
                            var _parsed_paths = __parseMusicSources(node['final_data_path']);
                            music_obj.jPlayer({
                                ready: function (event){
                                    var paths = __parseMusicSources(event.delegateTarget['filepath']);
                                    var _keys = Object.keys(paths);
                                    for(var k = 0; k< _keys.length; k++){
                                        var _type = _keys[k];
                                        if(paths[_type].indexOf('http') == 0){
                                            continue;
                                        }
                                        if(_is_user_music){
                                            paths[_type] = MOMEND_FILE_URL + paths[_type];
                                        }else{
                                            paths[_type] = MOMEND_FILE_URL + THEME_DATA_URL + paths[_type];
                                        }
                                    }
                                    $(this).jPlayer("setMedia",paths);
                                    _jsAnimate.musicLoaded($(this));
                                    __objectReady();
                                },
                                swfPath: STATIC_URL,
                                supplied: Object.keys(_parsed_paths).toString(),
                                wmode: 'window',
                                volume: 0.1,
                                loop: true
                            });
                            created_objects[node['final_data_path']] = music_obj;
                        case '{{THEME_MUSIC}}':
                        case '{{USER_MUSIC}}':
                            node['animation']['object'] = created_objects[node['final_data_path']];
                            break;
                    }

                }
            }
        }
        __checkIfReady();
    }
    function __objectReady(){
        loaded_objects++;
    }
    function __checkIfReady(){
        if(loaded_objects === total_objects){
            _load_callback();
        }else{
            setTimeout(__checkIfReady,300);
        }
    }
    function __applyPostEnhancements(created_obj, enhancements){
        for(var i=0; i<enhancements.length; i++){
            var enh = enhancements[i];
            var path = enh['filepath'];
            if(path && path.indexOf('http') != 0){
                path = MOMEND_FILE_URL + THEME_DATA_URL + path;
            }
            if(enh['type'] === 'apply_font'){
                jQuery('<link/>',{ //Include stylesheet to the html TODO:don't include twice maybe
                    rel : 'stylesheet',
                    href : path + '/stylesheet.css',
                    type : 'text/css',
                    charset : 'utf-8'
                }).appendTo('head');

                created_obj.css('font',enh['parameters']); //Then apply it to div
            }else if(enh['type'] === 'apply_bg'){
                created_obj.css('background-image','url("'+path+'")');
                created_obj.css('background-size', '100% 100%');
                created_obj.css('background-repeat', 'no-repeat');
                var _cssParameters = _parseStringToDict(enh['parameters'],false);
                $(created_obj.children()[0]).css(_cssParameters);
            }
        }
    }

    /**
     * Parses music sources to play in this format:
     * source_type=uri/url,['\n']source_type=uri/url
     * @param _str given music paths
     * @return dictionary contains given values
     * @private
     */
    function __parseMusicSources(_str){
        if(typeof _str !== 'string'){
            return null;
        }
        var _trimmed = _str.replace(/\s/g, ''); //remove whitespaces
        var resp = {};
        var parts = _trimmed.split(',');
        for(var i= 0; i<parts.length;i++){
            var css_parts = parts[i].split('=');
            resp[css_parts[0]] = css_parts[1];
        }
        return resp;
    }
    function _fullscreenToggle(){
        var _button = $('#button-fullscreen');
        var _scene = $('#scene');
        if(fullscreen){ //Was on fullscreen mode
            _button.removeClass('icon-resize-small');
            _button.addClass('icon-fullscreen');
            _scene.removeClass('fullscreen');

        }else{
            _button.removeClass('icon-fullscreen');
            _button.addClass('icon-resize-small');
            _scene.addClass('fullscreen');
        }
        fullscreen = !fullscreen;
    }

    /**
     * Sets the listener of FullScreen trigger button. Sends both fullscreen and shrink events to the same function
     * so you should keep the current state and perform operations.
     * @param _func in signature; func()
     */
    function _setFullscreenFunction(_func){
        $('#button-fullscreen')[0].onclick=_func;
    }

    /**
     * Adds a listener to the animation finish listeners. This function will be called when the main animation finished.
     * @param _func in signature; func()
     */
    function _addFinishListenerFunction(_func){
        _jsAnimate.addFinishListenerFunction(_func);
    }

    /**
     * Sets the function which will handle the url change requests of the player,
     * i.e. view saved interaction
     * opening the url and opening it in the current or new tab is up to you.
     * @param _func in signature; func(url:String)
     */
    function _setRedirectFunction(_func){
        page_redirect_function = _func;
    }

    function _getRedirectFunction(){
        return page_redirect_function;
    }

    return{
        init : init,
        momendArrived : _momendArrived,
        loadFailed : _loadFailed,
        startAnimation : _startAnimation,
        sendUserInteractionToServer : _sendUserInteractionToServer,
        createObjectsFromData : _createObjectsFromData,
        fullscreenToggle : _fullscreenToggle,
        setFullscreenFunction : _setFullscreenFunction,
        addFinishListenerFunction : _addFinishListenerFunction,
        setRedirectFunction :_setRedirectFunction,
        getRedirectFunction : _getRedirectFunction,
        momend_data : _momend_data,
        jsAnimate : _jsAnimate
    }
});
// !! UTILITY !!

/**
 * By default we keep animations in string format in db, however they can be parsed into json, this method gets those strings
 * and returns js dictionaries so that player can play them.
 * @param _str string like "left:200px,top:300px"
 * @param replaceKeywords replace keywords like {{SCREEN_WIDTH}} etc if true
 * @return {*} dictionary {"left":"200px","top":"300px"}
 * @private
 */
function _parseStringToDict(_str,replaceKeywords){
    if(typeof _str !== 'string'){
        return _str;
    }
    var resp = {};
    var parts = _str.split(',');
    for(var i= 0; i<parts.length;i++){
        var css_parts = parts[i].split(':');
        if(replaceKeywords && keywordLookupTable.hasAttribute(css_parts[1])){
            resp[css_parts[0]] = keywordLookupTable[css_parts[1]];
        }else{
            resp[css_parts[0]] = css_parts[1];
        }
    }
    return resp;
}

function hashCode(str){
    var hash = 0;
    if (str.length == 0) return hash;
    for (i = 0; i < str.length; i++) {
        var _char = str.charCodeAt(i);
        hash = ((hash<<5)-hash)+_char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}
/**
 * Key enumeration function for not supported browsers
 * Taken from: https://developer.mozilla.org/en-US/docs/JavaScript/Reference/Global_Objects/Object/keys
 */
if (!Object.keys) {
    Object.keys = (function () {
        var hasOwnProperty = Object.prototype.hasOwnProperty,
            hasDontEnumBug = !({toString: null}).propertyIsEnumerable('toString'),
            dontEnums = [
                'toString',
                'toLocaleString',
                'valueOf',
                'hasOwnProperty',
                'isPrototypeOf',
                'propertyIsEnumerable',
                'constructor'
            ],
            dontEnumsLength = dontEnums.length;

        return function (obj) {
            if (typeof obj !== 'object' && typeof obj !== 'function' || obj === null) throw new TypeError('Object.keys called on non-object');

            var result = [];

            for (var prop in obj) {
                if (hasOwnProperty.call(obj, prop)) result.push(prop);
            }

            if (hasDontEnumBug) {
                for (var i=0; i < dontEnumsLength; i++) {
                    if (hasOwnProperty.call(obj, dontEnums[i])) result.push(dontEnums[i]);
                }
            }
            return result;
        }
    })()
}