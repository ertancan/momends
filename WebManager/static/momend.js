
var momend_data;
function momend_arrived(){
    create_objects_from_data();
    setAnimationQueue(momend_data['animation_layers']);
    startAllQueues();
}
function create_objects_from_data(){
    var created_objects = {};
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
            switch(node['animation']['used_object_type']){
                case '{{NEXT_THEME_BG}}':
                    jQuery('<div/>',{
                        id: 'bg'+i+''+j,
                        class: 'scene-background'
                    }).appendTo('.scene');
                    jQuery('<img/>',{
                        class: 'background-image',
                        src: node['final_data_path']
                    }).appendTo('#bg'+i+''+j);
                    created_objects[node['final_data_path']] = $('#bg'+i+''+j);
                case '{{THEME_BG}}':
                    node['object'] = created_objects[node['final_data_path']];
                    break;
                case '{{NEXT_USER_PHOTO}}':
                    jQuery('<div/>',{
                        id: 'photo'+i+''+j,
                        class: 'photo'
                    }).appendTo('.scene');
                    jQuery('<img/>',{
                        class: 'photo_image',
                        src: node['final_data_path']
                    }).appendTo('#photo'+i+''+j);
                    created_objects[node['final_data_path']] = $('#photo'+i+''+j);
                case '{{USER_PHOTO}}':
                    node['object'] = created_objects[node['final_data_path']];
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