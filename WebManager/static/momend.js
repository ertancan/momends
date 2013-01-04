var momend_data;
var created_objects;
function momend_arrived(){
    create_objects_from_data();
    setAnimationQueue(momend_data['animation_layers']);
    startAllQueues();
}
function create_objects_from_data(){
    created_objects = {};
    for(var i = 0;i<momend_data['animation_layers'].length;i++){
        for(var j = 0;j < momend_data['animation_layers'][i].length;j++){
            var node = momend_data['animation_layers'][i][j];
            var _anim = node['animation']['anim'];
            if(_anim.length > 0){
                node['animation']['anim'] = _parse_string_to_dict(_anim);
            }
            var _pre = node['animation']['pre'];
            if(_pre.length > 0){
                node['animation']['pre'] = _parse_string_to_dict(_pre);
            }
            var filepath = node['final_data_path'];
            if(filepath != null && filepath.indexOf('http') != 0){
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
                    if(node['click_animation'] !== null){
                        created_div.click(function(){
                            handleClick($(this));
                        });
                    }
                    if(node['hover_animation'] !== null){
                        created_div.mouseenter(function(){
                            handleMouseEnter($(this));
                        });
                    }
                    created_objects[node['final_data_path']] = created_div;
                case '{{USER_PHOTO}}':
                    node['animation']['object'] = created_objects[node['final_data_path']];
                    break;
                case '{{NEXT_THEME_MUSIC}}':
                case '{{RAND_THEME_MUSIC}}':
                case '{{NEXT_USER_MUSIC}}':
                    jQuery('<div/>',{
                        id:'music'+i+''+j,
                        class:'jp-jplayer'
                    }).appendTo('.music');
                    $('#music'+i+''+j).jPlayer({
                        ready: function (event){
                            $(this).jPlayer("setMedia",{
                                mp3:filepath
                            });
                        },
                        swfPath: 'static',
                        supplied: 'mp3',
                        wmode: 'window',
                        volume: 0.01,
                        loop: true
                    });
                    created_objects[node['final_data_path']] = $('#music'+i+''+j);
                case '{{THEME_MUSIC}}':
                case '{{USER_MUSIC}}':
                    node['animation']['object'] = created_objects[node['final_data_path']];
                    break;
            }
        }
    }
}

function _parse_string_to_dict(_str){
    var resp = {};
    var parts = _str.split(',');
    for(var i= 0; i<parts.length;i++){
        var css_parts = parts[i].split(':');
        resp[css_parts[0]] = css_parts[1];
    }
    return resp;
}