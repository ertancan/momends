var animationQueue;
var finishedAnimationQueue;
var queueOnAction;
var currentAnimation;
var _layerWaitQueue;
var _layerBreakPointWaitQueue;
var _userInteractionQueue;
MUSIC_ANIMATION_INTERVAL = 200;
var last_user_click = 0;
var last_mouse_enter = 0;
function __generateQueues(_level){
    animationQueue = new Array();
    finishedAnimationQueue = new Array();
    queueOnAction = new Array();
    currentAnimation = new Array();
    _layerWaitQueue = new Array();
    _layerBreakPointWaitQueue = new Array();
    _userInteractionQueue = new Array();
    for(var i=0;i<_level;i++){
        animationQueue.push(new Array());
        finishedAnimationQueue.push(new Array());
        queueOnAction.push(false);
        currentAnimation.push(undefined);
        _layerWaitQueue.push(new Array());
        _layerBreakPointWaitQueue.push(new Array());
    }
}
function startQueue(_level){
    queueOnAction[_level]=true;
    nextAnimation(_level);
}
function startAllQueues(){
    for (var i=0;i<animationQueue.length;i++){
        startQueue(i);
    }
    last_user_click = new Date().getTime();
    last_mouse_enter = new Date().getTime();
}
function setAnimationQueue(_queue){
    __generateQueues(_queue.length);
    animationQueue = jQuery.extend(true,[],_queue);
}
function _addInteractionAnimationLayerForObject(animations){
    animationQueue.push(animations);
    finishedAnimationQueue.push(new Array());
    queueOnAction.push(false);
    currentAnimation.push(undefined);
    console.dir(animations);
    startQueue(animationQueue.length-1);
}
function addToQueue(_level,_node){
    var wasEmpty=false;
    if(animationQueue[_level].length===0){
        wasEmpty=true;
    }
    if(_node.constructor === Array){ //If adding an array of items
        for(var i=0;i<_node.length;i++){
            animationQueue[_level].push(_node[i]);
        }
    }else{ //Adding just one item
        animationQueue[_level].push(_node);
    }
    if(wasEmpty && queueOnAction[_level]){
        nextAnimation(_level);
    }
}
function _handleNode(_node,_level){ //TODO should handle dynamic values also, e.g., screenWidth, screenHeight
    var _animation = _node;
    if('animation' in _node){
        _animation = _node['animation']
    }

    currentAnimation[_level]=_node;
    finishedAnimationQueue[_level].push(_node); //TODO put it after finishing! it can be interrupted
    if(typeof _animation['name'] !=='undefined'){
        console.log('starting:'+_animation['name']);
    }else{
        console.log('starting:'+_animation['type']);
    }
    if(_animation['type']==='sleep'){
        setTimeout(function(){nextAnimation(_level)},_animation['duration']);
        return;
    }
    var triggerNext=true;
    if(typeof _animation['triggerNext']!=='undefined'){
        triggerNext=_animation['triggerNext'];
    }

    var _type=_animation['type'];
    if('object' in _animation){
        var _obj=_animation['object'];
    }
    var _duration=1;
    if('duration' in _animation){
        _duration=_animation['duration'];
    }

    if(_type==='animation'){
        if('pre' in _animation){
            for(var key in _animation['pre']){
                if(typeof _animation['pre'][key] === 'function'){
                    _animation['pre'][key]=_animation['pre'][key]();
                }
            }
            _obj.css(_animation['pre']);
        }
        for(var key in _animation['anim']){
            if(typeof _animation['anim'][key] === 'function'){
                _animation['anim'][key]=_animation['anim'][key]();
            }
        }
        _obj.animate(_animation['anim'],{duration:_duration,queue:false,complete:function(){
            if(triggerNext){
                nextAnimation(_level);
            }
        }});
    }
    else if(_type==='show'){
        _obj.show();
    }else if(_type==='hide'){
        _obj.hide();
    }else if(_type==='block'){
        var _target=_animation['target'];
        if(typeof _target != 'number'){
            _target=_level;
        }
        queueOnAction[_target]=false;
        if(_animation['force']===true){ //force stop
            currentAnimation[_target]['object'].stop();
        }
    }else if(_type==='unblock'){
        var _target=_animation['target'];
        if(typeof _target != 'number'){
            _target=_level;
        }
        startQueue(_target);
    }else if(_type==='wait'){
        triggerNext=false;
        var _target=_animation['target'];
        if(_target!==_level){
            queueOnAction[_level]=false;
            if(_animation['breakpoint']===true){ //Waiting for a break point on the target queue
                _layerBreakPointWaitQueue[_target].push(_level);
            }else{
                _layerWaitQueue[_target].push(_level); //Waiting the next action on the target queue
            }
        }
    }else if(_type==='breakpoint'){
        while(_layerBreakPointWaitQueue[_level].length!=0){
            _target=_layerBreakPointWaitQueue[_level].shift();
            startQueue(_target);
        }
    }else if(_type==='click'){
        _obj.click();
    }else if(_type==='hover'){
        _obj.mouseenter();
    }

    //Music animations below
    else if(_type === 'music-play'){
        _obj.jPlayer("play");
    }else if(_type === 'music-pause'){
        _obj.jPlayer("pause");
    }else if(_type ==='music-stop'){
        _obj.jPlayer("stop");
    }else if(_type === 'music-volume'){
        var _target = _animation['target'];
        var vol = parseFloat(_target);
        if(!isNaN(vol)){
            _obj.jPlayer("volume",vol);
        }
    }
    else if(_type === 'music-fadein'){
        var currentVol = _obj.jPlayer("option","volume");
        _musicFade(_obj,true,(1-currentVol)/(_duration/MUSIC_ANIMATION_INTERVAL));
    }else if(_type === 'music-fadeout'){
        var currentVol = _obj.jPlayer("option","volume");
        _musicFade(_obj,false,(1-currentVol)/(_duration/MUSIC_ANIMATION_INTERVAL));
    }

    //Trigger next animation if needed
    if(_type!='animation' && triggerNext){
        nextAnimation(_level);
    }
}
function nextAnimation(_level){
    if(currentAnimation.length!==animationQueue.length){
        console.log('INCONSISTENCY!!!');
    }
    if(animationQueue[_level].length===0){
        return;
    }
    if(!queueOnAction[_level]){
        return;
    }
    if(typeof _layerWaitQueue[_level]!=='undefined'){
        while(_layerWaitQueue[_level].length!=0){
            var waiting=_layerWaitQueue[_level].shift();
            startQueue(waiting);
        }
    }
    _node=animationQueue[_level].shift();
    _handleNode(_node,_level);
    if(animationQueue[_level].length!==0 && animationQueue[_level][0]['animation']['waitPrev']===false){
        nextAnimation(_level);
    }
}

function _musicFade(_obj,isFadeIn,step){
    var currentVol = _obj.jPlayer("option","volume");
    if(isFadeIn){
        var targetVol = currentVol + step;
    }else{
        var targetVol = currentVol - step;
    }
    _obj.jPlayer("volume",targetVol);
    if(targetVol - step > 0 || targetVol + step <1){
        setTimeout(function(){
            _musicFade(_obj,isFadeIn,step);
        },MUSIC_ANIMATION_INTERVAL);
    }
}

function handleClick(_obj){
    var click_time = new Date().getTime();
    var _node = _findObjectNode(_obj);
    var click_animation = _node['animation']['click_animation'];
    for (var i = 0; i<click_animation['animations'].length;i++){
        click_animation['animations'][i]['anim'] = _parse_string_to_dict(click_animation['animations'][i]['anim']);
        click_animation['animations'][i]['object'] = _obj;
    }
    if(click_animation['stop_current_animation']){
        _obj.stop(true);
    }
    _userInteractionQueue.push({'animation':{'type':'sleep','duration':(click_time-last_user_click)}});
    _userInteractionQueue.push({'object':_obj,'animation':{'type':'click'}});
    _addInteractionAnimationLayerForObject(click_animation['animations'])
    last_user_click=click_time;
}

function handleMouseEnter(_obj){
    var enter_time = new Date().getTime();
    var _node = _findObjectNode(_obj);
    var enter_animation = _node['animation']['hover_animation'];
    for (var i = 0; i<enter_animation['animations'].length;i++){
        enter_animation['animations'][i]['anim'] = _parse_string_to_dict(enter_animation['animations'][i]['anim']);
        enter_animation['animations'][i]['object'] = _obj;
    }
    if(enter_animation['stop_current_animation']){
        _obj.stop(true);
    }
    _userInteractionQueue.push({'animation':{'type':'sleep','duration':(enter_time-last_mouse_enter)}});
    _userInteractionQueue.push({'object':_obj,'animation':{'type':'hover'}});
    _addInteractionAnimationLayerForObject(enter_animation['animations'])
    last_mouse_enter=enter_time;
}


function _findObjectNode(_obj){
    console.dir(_obj);
    for(var i=0;i<momend_data['animation_layers'].length;i++){
        for(var j=0;j<momend_data['animation_layers'][i].length;j++){
            if(!momend_data['animation_layers'][i][j]['animation']['object']){
                continue;
            }
            console.log('search:'+_obj[0].id+' got:'+momend_data['animation_layers'][i][j]['animation']['object'].selector);
            if(momend_data['animation_layers'][i][j]['animation']['object'].selector ==='#'+_obj[0].id){
                return momend_data['animation_layers'][i][j];
            }
        }
    }
}
