var momend_data;
var created_objects;
var volume_slider;
var finished_modal;
var fullscreen = false;
var page_redirect_function;
var _interaction_sent = false;
var total_objects = 0;
var loaded_objects = 0;
var _load_callback;
function hashCode(str){
    var hash = 0;
    if (str.length == 0) return hash;
    for (i = 0; i < str.length; i++) {
        var _char = str.charCodeAt(i);
        hash = ((hash<<5)-hash)+_char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
};

function momend_arrived(){
    _calculate_dimensions(); //Since they may be needed while creating objects
    if(!momend_data || momend_data.length == 0 || momend_data['error']){
        load_failed();
        return;
    }
    create_objects_from_data(start_animation); //start animation as create objects callback
}
function start_animation(){
    setAnimationQueue(momend_data['animation_layers']);
    $('#loading-bg').animate({
        'top':'-100%',
        'opacity' : '0.5'
    },{
        duration: 500,
        complete: function(){
            $(this).hide();
            startAllQueues();
        }
    });
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
    var json = _convertLayerToJSON(_userInteractionQueue);
    var token = $('[name="csrfmiddlewaretoken"]')[0].value;
    var momend_id = momend_data['id'];
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
                if(data.resp === "true"){
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
function load_failed(){
    jQuery('<h1/>',{
        text : 'Momend could not be found!',
        class : 'error',
        id : 'error'
    }).appendTo('body');
}
function create_objects_from_data(load_callback){
    _load_callback = load_callback;
    created_objects = {};
    for(var i = 0;i<momend_data['animation_layers'].length;i++){
        for(var j = 0;j < momend_data['animation_layers'][i].length;j++){
            var node = momend_data['animation_layers'][i][j];
            var _anim = node['animation']['anim'];
            if(_anim && _anim.length > 0){
                node['animation']['anim'] = _parse_string_to_dict(_anim);
            }
            var _pre = node['animation']['pre'];
            if(_pre && _pre.length > 0){
                node['animation']['pre'] = _parse_string_to_dict(_pre);
            }
            var filepath = node['final_data_path'];
            if(filepath && filepath.indexOf('http') != 0){
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
                        src: filepath,
                        ready : function(){
                            _object_ready();
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
                            src: filepath,
                            ready : function(){
                                _object_ready();
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
                                _object_ready();
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
                            _apply_post_enhancements(created_div,node['post_enhancements']);
                        }
                        created_objects[hashCode(node['data'])] = created_div;

                    case '{{USER_STATUS}}':
                        node['animation']['object'] = created_objects[hashCode(node['data'])];
                        break;


                    case '{{NEXT_THEME_MUSIC}}':
                    case '{{RAND_THEME_MUSIC}}':
                    case '{{NEXT_USER_MUSIC}}':
                        total_objects++; //Player should wait for item to load
                        jQuery('<div/>',{
                            id:'music'+i+''+j,
                            class:'jp-jplayer'
                        }).appendTo('.music');
                        var music_obj = $('#music'+i+''+j);
                        music_obj[0]['filepath'] = filepath;
                        music_obj.jPlayer({
                            ready: function (event){
                               _object_ready();
                                $(this).jPlayer("setMedia",{
                                    mp3:event.delegateTarget['filepath']
                                });
                                _music_loaded($(this));
                            },
                            swfPath: 'static',
                            supplied: 'mp3',
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
}
function _object_ready(){
    loaded_objects++;
    setTimeout(_check_if_ready,10);
}
function _check_if_ready(){
    if(loaded_objects === total_objects){
        _load_callback();
    }
}
function _apply_post_enhancements(created_obj, enhancements){
    for(var i=0; i<enhancements.length; i++){
        var enh = enhancements[i];
        var path = enh['filepath'];
        if(path && path.indexOf('http') != 0){
            path = MOMEND_FILE_URL + path;
        }
        console.log(enh['type']);
        if(enh['type'] === 'apply_font'){
            jQuery('<link/>',{ //Include stylesheet to the html TODO:don't include twice maybe
                rel:'stylesheet',
                href:path,
                type:'text/css',
                charset:'utf-8'
            }).appendTo('head');

            created_obj.css('font',enh['parameters']); //Then apply it to div
        }else if(enh['type'] === 'apply_bg'){
            created_obj.css('background-image','url("'+path+'")');
            created_obj.css(_parse_string_to_dict(enh['parameters']));
        }
    }
}

/**
 * By default we keep animations in string format in db, however they can be parsed into json, this method gets those strings
 * and returns js dictionaries so that player can play them.
 * @param _str string like "left:200px,top:300px"
 * @param replaceKeywords replace keywords like {{SCREEN_WIDTH}} etc if true
 * @return {*} dictionary {"left":"200px","top":"300px"}
 * @private
 */
function _parse_string_to_dict(_str,replaceKeywords){
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
function fullscreenToggle(){
    var _button = $('#button-fullscreen');
    if(fullscreen){ //Was on fullscreen mode
        _button.removeClass('icon-resize-small')
        _button.addClass('icon-fullscreen');
    }else{
        _button.removeClass('icon-fullscreen')
        _button.addClass('icon-resize-small');
    }
    fullscreen = !fullscreen;
}

/**
 * Sets the listener of FullScreen trigger button. Sends both fullscreen and shrink events to the same function
 * so you should keep the current state and perform operations.
 * @param _func in signature; func()
 */
function setFullscreenFunction(_func){
    $('#button-fullscreen')[0].onclick=_func;
}

/**
 * Adds a listener to the animation finish listeners. This function will be called when the main animation finished.
 * @param _func in signature; func()
 */
function addFinishListenerFunction(_func){
    animation_finish_observer.push(_func);
}

/**
 * Sets the function which will handle the url change requests of the player,
 * i.e. view saved interaction
 * opening the url and opening it in the current or new tab is up to you.
 * @param _func in signature; func(url:String)
 */
function setRedirectFunction(_func){
    page_redirect_function = _func;
}