var animationQueue;
var finishedAnimationQueue;
var queueOnAction;
var currentAnimation;
var _layerWaitQueue;
var _layerBreakPointWaitQueue;
MUSIC_ANIMATION_INTERVAL = 200;
function __generateQueues(_level){
    animationQueue=new Array();
    finishedAnimationQueue=new Array();
    queueOnAction=new Array();
    currentAnimation=new Array();
    _layerWaitQueue=new Array();
    _layerBreakPointWaitQueue=new Array();
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
}
function setAnimationQueue(_queue){
    __generateQueues(_queue.length);
    animationQueue = jQuery.extend(true,[],_queue);
    console.log('animation queue:');
    console.dir(animationQueue);
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
    _animation = _node['animation']
    currentAnimation[_level]=_node;
    finishedAnimationQueue[_level].push(_node); //TODO put it after finishing! it can be interrupted
    if(typeof _animation['name'] !=='undefined'){
        console.log('starting:'+_animation['name']);
    }else{
        console.log('starting:'+_animation['type']);
    }
    console.dir(_animation);
    if(_animation['type']==='sleep'){
        setTimeout(function(){nextAnimation(_level)},_animation['duration']);
        return;
    }
    var triggerNext=true;
    if(typeof _animation['triggerNext']!=='undefined'){
        triggerNext=_animation['triggerNext'];
    }

    var _type=_animation['type'];
    var _obj=_node['object'];
    var _duration=1;
    if('duration' in _animation){
        _duration=_animation['duration'];
    }

    console.dir(_obj)
    if(_type==='animation'){
        if('pre' in _animation){
            for(key in _animation['pre']){
                if(typeof _animation['pre'][key] === 'function'){
                    _animation['pre'][key]=_animation['pre'][key]();
                }
            }
            _obj.css(_animation['pre']);
        }
        for(key in _animation['anim']){
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
    }else if(_type === 'music-play'){
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
    while(_layerWaitQueue[_level].length!=0){
        var waiting=_layerWaitQueue[_level].shift();
        startQueue(waiting);
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

function handleClick(_obj,_layer,_order){
    console.log('kılik');
    console.dir(_obj);
}
