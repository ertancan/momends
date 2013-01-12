var momend_data;
var created_objects;
String.prototype.hashCode = function(){
    var hash = 0;
    if (this.length == 0) return hash;
    for (i = 0; i < this.length; i++) {
        var _char = this.charCodeAt(i);
        hash = ((hash<<5)-hash)+_char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
};

function momend_arrived(){
    _calculate_dimensions(); //Since they may be needed while creating objects
    if(!momend_data || momend_data.length == 0){
        load_failed();
        return;
    }
    create_objects_from_data();
    setAnimationQueue(momend_data['animation_layers']);
    startAllQueues();
    $(window).resize(function(){
        _calculate_dimensions();
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
            switch(node['animation']['used_object_type']){
                case '{{NEXT_THEME_BG}}':
                case '{{RANDOM_THEME_BG}}':
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
                case '{{RANDOM_USER_PHOTO}}':
                    jQuery('<div/>',{
                        id: 'photo'+i+''+j,
                        class: 'photo'
                    }).appendTo('.scene');
                    var created_div = $('#photo'+i+''+j);
                    jQuery('<img/>',{
                        class: 'photo_image',
                        src: filepath
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
                    created_objects[node['final_data_path']] = created_div;
                case '{{USER_PHOTO}}':
                    node['animation']['object'] = created_objects[node['final_data_path']];
                    break;

                case '{{NEXT_USER_STATUS}}':
                case '{{RANDOM_USER_STATUS}}':
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
                    created_objects[node['data'].hashCode()] = created_div;

                case '{{USER_STATUS}}':
                    node['animation']['object'] = created_objects[node['data'].hashCode()];
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