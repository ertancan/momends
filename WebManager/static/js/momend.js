var Momend = (function(){
    var _jsAnimate = JSAnimate;
    var _momendData;
    var _shadowData;
    var fullscreen = false;
    var pageRedirectFunction;
    var _interactionSent = false;
    var totalObjects = 0;
    var loadedObjects = 0;
    var _loadCallback;
    var musicObjects;
    var createdObjects;
    var logger;

    function init(){
        if(arguments.length > 0){
            for(var i=0; i<arguments.length; i++){
                if(arguments[i].hasOwnProperty('logEvent')){
                    logger = arguments[i];
                }
            }
        }
        if(!logger){
            logger = MomendsLogger;
        }
        _jsAnimate.initAnimation(logger);
    }
    function _momendArrived(momend_data){
        _momendData = $.extend(momend_data, {}, true);
        _jsAnimate.reCalculateDimensions(); //Since they may be needed while creating objects
        if(!_momendData || _momendData.length === 0 || _momendData['error']){
            _loadFailed();
            _gaq.push(['_trackEvent', 'Player', 'Load', 'Failed']);
        }else{
            _createObjectsFromData(_loadSuccessful); //start animation as create objects callback
            _gaq.push(['_trackEvent', 'Player', 'Load', 'Successful']);
            logger.logEvent({'msg': 'Player is ready to play'});
        }
    }
    function _startAnimation(){
        _gaq.push(['_trackEvent', 'Player', 'Action', 'Start']);
        _jsAnimate.setAnimationQueue(_momendData['animation_layers']);
        _jsAnimate.setShadowData(_shadowData);
        $('#load-modal').animate({
            'top':'-100%',
            'opacity' : '0.5'
        },{
            duration: 500,
            complete: function(){
                $(this).hide();
            }
        });
        setTimeout(function(){
            for(var i = 0; i< musicObjects.length; i++){
                musicObjects[i].jPlayer('play');
                musicObjects[i].jPlayer('pause');
            }
            _jsAnimate.startAllQueues();
            logger.logEvent({'msg': 'Player started'});
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
        if(_interactionSent){
            return;
        }
        //console.log('sending');
        logger.logEvent({'msg': 'sending user interaction to server'});
        var json = _jsAnimate.convertUserInteractionLayerToJSON();
        var token = $('[name="csrfmiddlewaretoken"]')[0].value;
        var momend_id = _momendData['cryptic_id'];
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
                _interactionSent = true;
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
        logger.logEvent({'msg': 'momend load failed'});
        jQuery('<h1/>',{
            text : 'Momend could not be found!',
            class : 'error',
            id : 'error'
        }).appendTo('body');
        $('#load-modal').hide();
    }

    function _loadSuccessful(){
        $('#loading-main').hide();
        $('#loaded-main').show();
    }
    function _createObjectsFromData(load_callback){
        _loadCallback = load_callback;
        createdObjects = {};
        musicObjects = [];
        _shadowData = {};
        for(var i = 0;i<_momendData['animation_layers'].length;i++){
            for(var j = 0;j < _momendData['animation_layers'][i].length;j++){
                var node = _momendData['animation_layers'][i][j];
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
                if(filepath && filepath.indexOf('http') !== 0){
                    theme_filepath = MOMEND_FILE_URL + THEME_DATA_URL + filepath;
                    filepath = MOMEND_FILE_URL + filepath;
                }
                if(node['animation']['used_theme_data'] != null){
                    if(createdObjects[node['final_data_path']]){
                        node['animation']['object'] = createdObjects[node['final_data_path']];
                    }else{
                        node['animation']['object'] = __createStubPhoto(node, i, j, theme_filepath);
                    }
                }else{
                    switch(node['animation']['used_object_type']){
                        case '{{NEXT_THEME_BG}}':
                        case '{{RAND_THEME_BG}}':
                            node['animation']['object'] = __createThemeBg(node, i, j, theme_filepath);
                            break;
                        case '{{THEME_BG}}':
                            node['animation']['object'] = createdObjects[node['final_data_path']];
                            break;
                        case '{{NEXT_USER_PHOTO}}':
                        case '{{RAND_USER_PHOTO}}':
                            node['animation']['object'] = __createPhoto(node, i, j, filepath);
                            break;
                        case '{{USER_PHOTO}}':
                            node['animation']['object'] = createdObjects[_getPhotoIdentifier(node['final_data_path'])];
                            break;
                        case '{{NEXT_USER_STATUS}}':
                        case '{{RAND_USER_STATUS}}':
                            node['animation']['object'] = __createStatus(node, i, j);
                            break;
                        case '{{USER_STATUS}}':
                            node['animation']['object'] = createdObjects[hashCode(node['data'])];
                            break;
                        case '{{NEXT_USER_MUSIC}}':
                            var isUserMusic = true;
                        case '{{NEXT_THEME_MUSIC}}':
                        case '{{RAND_THEME_MUSIC}}':
                            node['animation']['object'] = __createMusic(node, i, j, isUserMusic);
                            break;
                        case '{{THEME_MUSIC}}':
                        case '{{USER_MUSIC}}':
                            node['animation']['object'] = createdObjects[node['final_data_path']];
                            break;
                        case '{{CURRENT_PHOTO_TITLE}}':  //Title has the owner photo as final_data_path
                            var title = createdObjects[hashCode(node['date'])];
                            if(title){
                                node['animation']['object'] = title;
                            }else{
                                __createTitle(node, i, j);
                                node['animation']['object'] = createdObjects[hashCode(node['date'])];
                            }
                    }

                }
            }
        }
        __checkIfReady();
    }

    /**
    Creates a div and photo dom objects for given stub data node
    handles user interactions and shadow, too
    Appends the result to createdObjects dictionary
    */
    function __createStubPhoto(node, layer, order, theme_filepath){
        totalObjects++; //Player should wait for item to load
        var _id = 'stub'+layer+''+order;
        var created_div = jQuery('<div/>',{
            id: _id,
            class: 'photo'
        }).appendTo('.scene');
        var created_obj = jQuery('<img/>',{
            class: 'photo_image',
            id: 'stub-image'+layer+''+order,
            src: theme_filepath,
            ready : function(){
                __objectReady();
            }
        }).appendTo(created_div);
        if(typeof node['animation']['click_animation'] !== 'undefined'){
            created_obj.click(function(){
                _jsAnimate.handleClick($(this));
            });
        }
        if(typeof node['animation']['hover_animation'] !== 'undefined'){
            created_obj.mouseenter(function(){
                _jsAnimate.handleMouseEnter($(this));
            });
        }
        if(typeof node['animation']['shadow'] !== 'undefined'){
             _shadowData[_id] = node['animation']['shadow'];
        }
        createdObjects[node['final_data_path']] = created_div;
        return created_div;
    }

    /**
    Creates a div that contains background picture
    has no user interaction or shadow
    */
    function __createThemeBg(node, layer, order, theme_filepath){
        totalObjects++; //Player should wait for item to load
        var _id = 'bg'+layer+''+order;
        var created_div = jQuery('<div/>',{
            id: _id,
            class: 'scene-background'
        }).appendTo('.scene');
        var created_pbj = jQuery('<img/>',{
            class: 'background-image',
            src: theme_filepath,
            ready : function(){
                __objectReady();
            }
        }).appendTo(created_div);
        createdObjects[node['final_data_path']] = created_div;
        return created_div;
    }

    /**
    Creates a div that contains user photo
    Appends the result to the createdObjects dictionary
    */
    function __createPhoto(node, layer, order, filepath){
        totalObjects++; //Player should wait for item to load
        var _id = 'photo'+layer+''+order;
        var created_div = jQuery('<div/>',{
            id: _id,
            class: 'photo'
        }).appendTo('.scene');
        var created_obj = jQuery('<img/>',{
            class: 'photo_image',
            id: 'photo_image'+layer+''+order,
            src: filepath,
            ready : function(){
                __objectReady();
            }
        }).appendTo(created_div);
        if(typeof node['animation']['click_animation'] !== 'undefined'){
            created_obj.click(function(){
                _jsAnimate.handleClick($(this));
            });
        }
        if(typeof node['animation']['hover_animation'] !== 'undefined'){
            created_obj.mouseenter(function(){
                _jsAnimate.handleMouseEnter($(this));
            });
        }
        if(typeof node['animation']['shadow'] !== 'undefined'){
            _shadowData[_id] = node['animation']['shadow'];
        }
        createdObjects[_getPhotoIdentifier(node['final_data_path'])] = created_div;
        return created_div;
    }

    /**
    Creates a status dom object and adds it to createdObjects array.
    Also applies post enhancements if the given node has enhancement values on post_enhancements key
    */
    function __createStatus(node, layer, order){
        var _id = 'status'+layer+''+order;
        var created_div = jQuery('<div/>',{
            id: _id,
            class: 'status'
        }).appendTo('.scene');
        jQuery('<p/>',{
            class: 'status-text',
            text:node['data']
        }).appendTo(created_div);
        if(typeof node['animation']['click_animation'] !== 'undefined'){
            created_div.click(function(){
                _jsAnimate.handleClick($(this));
            });
        }
        if(typeof node['animation']['hover_animation'] !== 'undefined'){
            created_div.mouseenter(function(){
                _jsAnimate.handleMouseEnter($(this));
            });
        }
        if(typeof node['animation']['shadow'] !== 'undefined'){
            _shadowData[_id] = node['animation']['shadow'];
        }
        if(node['post_enhancements']){
            __applyPostEnhancements(created_div,node['post_enhancements']);
        }
        createdObjects[hashCode(node['data'])] = created_div;
        return created_div;
    }

    /**
    Creates required divs and instantiates jPlayer to be ready to play music
    Adds the resulting player to createdObjects dictionary
    !IMPORTANT: sets the volume of the player to 0.1, by the time I was looking there was an issue on setting it to 0
    However it won't matter if you set the volume after playing the music since it is not playing automatically.
    */
    function __createMusic(node, layer, order, isUserMusic){
        totalObjects++; //Player should wait for item to load
        var _id = 'music'+layer+''+order;
        var musicObj = jQuery('<div/>',{
            id: _id,
            class:'jp-jplayer'
        }).appendTo('.music');
        musicObjects.push(musicObj);
        musicObj[0]['filepath'] = node['final_data_path'];
        var _parsed_paths = __parseMusicSources(node['final_data_path']);
        musicObj.jPlayer({
            ready: function (event){
                var paths = __parseMusicSources(event.delegateTarget['filepath']);
                var _keys = Object.keys(paths);
                for(var k = 0; k< _keys.length; k++){
                    var _type = _keys[k];
                    if(paths[_type].indexOf('http') === 0){
                        continue;
                    }
                    if(isUserMusic){
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
            volume: 0.1
        });
        createdObjects[node['final_data_path']] = musicObj;
        return musicObj;
    }

    /**
        Creates a title div (Which appears quite like status :) ) and appends it to the owner photo's div
    */
    function __createTitle(node, layer, order){
        var owner = createdObjects[_getPhotoIdentifier(node['final_data_path'])];  // Photo object
        //console.log('Appending to:');
        //console.dir(owner);
        var _id = 'title' + layer + '' + order;
        var created_div = jQuery('<div/>',{
            id: _id,
            class: 'title'
        }).appendTo(owner);
        jQuery('<p/>',{
            class: 'title-text',
            text:node['title']
        }).appendTo(created_div);
        if(node['post_enhancements']){
            __applyPostEnhancements(created_div,node['post_enhancements']);
        }
        createdObjects[hashCode(node['date'])] = created_div;  // Using full date to be unique, title or day part of the date might not be.
        return created_div;
    }

    /**
    Object load callback in order to count how many of the required objects are loaded
    Increaments global variable; loadedObjects
    */
    function __objectReady(){
        loadedObjects++;
    }

    /**
    Checks if all the required objects loaded
    After called once, it will run in every 300ms until player is ready,
    it will call loadCallback if the player is ready
    */
    function __checkIfReady(){
        if(loadedObjects === totalObjects){
            _loadCallback();
        }else{
            setTimeout(__checkIfReady,300);
        }
    }
    function __applyPostEnhancements(created_obj, enhancements){
        for(var i=0; i<enhancements.length; i++){
            var enh = enhancements[i];
            var path = enh['filepath'];
            if(path && path.indexOf('http') !== 0){
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
        pageRedirectFunction = _func;
    }

    function _getRedirectFunction(){
        return pageRedirectFunction;
    }

    function _getMomendData(){
        return _momendData;
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
        getMomendData : _getMomendData,
        jsAnimate : _jsAnimate,
        isPlaying : _jsAnimate.isPlaying
    };
}());
// !! UTILITY !!

/**
    Returns the identifier part (username_provider_providerId) of given photo url
    @param fullPath: path of the photo like /static/collected/user_facebook_123.25.enh0
    return (string) user_facebook_123, null on error
*/
function _getPhotoIdentifier(fullPath){
    var identifier = null;
    try{
        var withoutHost = fullPath.replace(MOMEND_FILE_URL, '');
        var lastPartIndex = withoutHost.lastIndexOf('/');
        var lastStr = withoutHost.substring(lastPartIndex + 1);
        var dotIndex = lastStr.indexOf('.');
        identifier = lastStr.substring(0, dotIndex);
    }catch(Exception){
        Log.error('Filename format is invalid');
    }
    return identifier;
}

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
    if (str.length === 0) return hash;
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
        };
    })();
}