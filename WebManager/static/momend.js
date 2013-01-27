var momend_data;
var created_objects;
var volume_slider;
var finished_modal;
var fullscreen = false;
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
    create_objects_from_data();
    setAnimationQueue(momend_data['animation_layers']);
    startAllQueues();
}
/**
 * Send the queue generated while user interacts with the animation to the given url
 * Needs the CSRF token to be on the player's codes
 * fills id and queue parameters of the request
 * @param url that listens post requests and saves interaction
 * @private
 */
function _sendUserInteractionToServer(url){
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
            console.log('Sent: '+msg);
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
function create_objects_from_data(){
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
                filepath = STATIC_URL + filepath;
            }
            if(node['animation']['used_theme_data'] != null){
                if(created_objects[node['final_data_path']]){
                    node['animation']['object'] = created_objects[node['final_data_path']];
                }else{
                    jQuery('<div/>',{
                        id: 'stub'+i+''+j,
                        class: 'photo'
                    }).appendTo('.scene');
                    var created_div = $('#stub'+i+''+j);
                    var created_obj = jQuery('<img/>',{
                        class: 'photo_image',
                        id: 'stub-image'+i+''+j,
                        src: filepath
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
                        jQuery('<div/>',{
                            id: 'bg'+i+''+j,
                            class: 'scene-background'
                        }).appendTo('.scene');
                        jQuery('<img/>',{
                            class: 'background-image',
                            src: filepath
                        }).appendTo('#bg'+i+''+j);
                        created_objects[node['final_data_path']] = $('#bg'+i+''+j);
                    case '{{THEME_BG}}':
                        node['animation']['object'] = created_objects[node['final_data_path']];
                        break;
                    case '{{NEXT_USER_PHOTO}}':
                    case '{{RAND_USER_PHOTO}}':
                        jQuery('<div/>',{
                            id: 'photo'+i+''+j,
                            class: 'photo'
                        }).appendTo('.scene');
                        var created_div = $('#photo'+i+''+j);
                        var created_obj = jQuery('<img/>',{
                            class: 'photo_image',
                            id: 'photo_image'+i+''+j,
                            src: filepath
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
                        jQuery('<div/>',{
                            id:'music'+i+''+j,
                            class:'jp-jplayer'
                        }).appendTo('.music');
                        var music_obj = $('#music'+i+''+j);
                        music_obj[0]['filepath'] = filepath;
                        music_obj.jPlayer({
                            ready: function (event){
                                console.dir(event.delegateTarget);
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
function _apply_post_enhancements(created_obj, enhancements){
    for(var i=0; i<enhancements.length; i++){
        var enh = enhancements[i];
        var path = enh['filepath'];
        if(path && path.indexOf('http') != 0){
            path = STATIC_URL + path;
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

function create_finish_view(){
    finished_modal = jQuery('<div/>',{
        class : 'finished-modal-bg',
        id : 'finished-bg'
    }).appendTo('body');
    var _modal = jQuery('<div/>',{
        class : 'finished-modal',
        id : 'finished-modal'
    }).appendTo(finished_modal);
    var sendInteractionButton = jQuery('<div/>',{
        id : 'send-interaction-button',
        onclick : 'send_interaction_data()',
        class : 'finished-modal-button'
    }).appendTo(_modal);

    jQuery('<i/>',{
        class : 'icon-magic modal-icon'
    }).appendTo(sendInteractionButton);
    jQuery('<span/>',{
        text : 'Save Interaction'
    }).appendTo(sendInteractionButton);

    var shareButton = jQuery('<div/>',{
        id : 'share-button',
        onclick : 'share()',
        class : 'finished-modal-button'
    }).appendTo(_modal);

    jQuery('<i/>',{
        class : 'icon-share modal-icon'
    }).appendTo(shareButton);
    jQuery('<span/>',{
        text : 'Share'
    }).appendTo(shareButton);
    finished_modal.hide();
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

function setFullscreenFunction(_func){
    $('#button-fullscreen')[0].onclick=_func;
}
function addFinishListenerFunction(_func){
    animation_finish_observer.push(_func);
}