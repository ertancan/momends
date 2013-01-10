var animationQueue; // Keeps layers of animation data
var finishedAnimationQueue; //Keeps finished animations
var queueOnAction; // Boolean array indicates the given layer is active or not (e.g. queueOnAction[0] will be true if layer 0 started and working now)
var currentAnimation; //Keeps the animations which are being processed right now
var _layerWaitQueue; //Each array in this queue keeps the ids of other layers waiting for the current animation on the queue
//If _layerWaitQueue[0] has 1 and 2 in it, layers 1 and 2 will be started when the current animation in layer 0 finishes
var _layerBreakPointWaitQueue; //Same principle as _layerWaitQueue but this waits for an animation which has type 'breakpoint' to trigger otherlayers
var _userInteractionQueue; //Keeps the action performed by user during play.
MUSIC_ANIMATION_INTERVAL = 100; //Defines number of milliseconds between music fade animations. (e.g. if you perform fade animation with duration=1000ms
// the animation will be performed in 5 steps. (Can be changed according to smoothness of the animation
var last_user_interaction = 0; //last time the user clicks on an item or mouse enters into the object boundaries.
var ready_music_count = 0; //How many of the remaining music are ready for playing.
var node_waiting_to_play; //If the handle_node tried to play a music but it wasn't ready
var music_layer; //Which layer belongs to music player
var keywordLookupTable; //Keeps the latest values of keyword related values like {{SCREEN_WIDTH}}

/**
 * Instantiates global variables according to number of levels needed.
 * @param _level number of animations layers
 */
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
/**
 * Starts the given queue; flags it as on action and triggers the next animation on the queue
 * @param _level which level is going to start
 */
function startQueue(_level){
    queueOnAction[_level]=true;
    nextAnimation(_level);
}
/**
 * Starts all animation queues
 * !!Clears the user interaction timers, do not use unless you are starting a new animation!!
 */
function startAllQueues(){
    for (var i=0;i<animationQueue.length;i++){
        startQueue(i);
    }
    last_user_interaction = new Date().getTime();
}
/**
 * Clears the current animation queue and replaces it with the given one
 * @param _queue Layer of animations to be performed
 */
function setAnimationQueue(_queue){
    __generateQueues(_queue.length);
    animationQueue = jQuery.extend(true,[],_queue);
}
/**
 * Creates an additional animation queue level for user interaction animations like click or hover.
 * @param animations Click or hover animations of an object
 */
function _addInteractionAnimationLayerForObject(animations){
    animationQueue.push(animations);
    finishedAnimationQueue.push(new Array());
    queueOnAction.push(false);
    currentAnimation.push(undefined);
    console.dir(animations);
    startQueue(animationQueue.length-1);
}
/**
 * Insert given node to the given layer of the queue.
 * !!If the level is on action and it is waiting empty, the animation will be performed immediately, so if you are adding
 * items to the queue one by one, it is most likely that it will be called like waitPrev option is false, so add elements
 * together in an array.
 * @param _level which the animations will be added
 * @param _node an animation object or an array containing animation objects.
 */
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
/**
 * Handles a single node's animations
 * @param _node Whether the node itself or an object containing the node in 'animation' key
 * @param _level which level does the node belong to. (In order to trigger next animation)
 *
 * main keys in the animation dictionary;
 *  object:(jQuery object) to perform operations on
 *  [duration]:(int) duration of the animations (in ms)
 *  [triggerNext]:(bool) whether the next operation should be called after
 *  [name]:(string) name to print on the console if needed
 *  type:(string) type of the animation
 *      animation; Animates the given object
 *          uses duration parameter
 *          [pre]:(dictionary) css parameters which should be applied before animation
 *          [anim]:(dictionary) css parameters which are going to be animated during animation
 *      sleep: Blocks the queue for some amount of time
 *          uses duration parameter
 *      show/hide: Shows and hides the given object
 *      block/unblock: blocks and unblocks the given queue (unblock cannot work on its own queue)
 *          target:(int) targeted layer
 *      wait: Force the current queue to wait until the current operation on the watched queue ends or breakpoint occurs
 *          [breakpoint]:(bool) if given true, current layer will wait until a breakpoint occurs in the target layer
 *          target:(int) targeted layer
 *      breakpoint: Triggers the other layers which were waiting for current layer for a breakpoint
 *      click/hover: Performs click and hover animations on the object
 */
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
        if(typeof _obj === 'string'){
            _obj = $(_obj);
        }
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
                if(_animation['pre'][key] in keywordLookupTable){
                    _animation['pre'][key]=keywordLookupTable[_animation['pre'][key]];
                }
            }
            _obj.css(_animation['pre']);
        }
        for(var key in _animation['anim']){
            if(typeof _animation['anim'][key] === 'function'){
                _animation['anim'][key]=_animation['anim'][key]();
            }
            if(_animation['anim'][key] in keywordLookupTable){
                _animation['anim'][key]=keywordLookupTable[_animation['anim'][key]];
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
        music_layer = _level;
        if(ready_music_count>0){
            _obj.jPlayer("play");
            node_waiting_to_play=null;
            ready_music_count--;
        }else{
            console.log('Music not ready yet, waiting');
            node_waiting_to_play=_node;
            return;
        }
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
        _musicFade(_obj,false,1/(_duration/MUSIC_ANIMATION_INTERVAL));
    }

    //Trigger next animation if needed
    if(_type!='animation' && triggerNext){
        nextAnimation(_level);
    }
}

/**
 * Triggers the next animation in the queue
 * @param _level level of the queue
 */
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
    try{
        if(animationQueue[_level].length!==0 && animationQueue[_level][0]['animation']['waitPrev']===false){
            nextAnimation(_level);
        }
    }catch(error){
        console.dir(animationQueue[_level][0]);
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
    if((isFadeIn && targetVol + step  <=1 ) || (!isFadeIn && targetVol - step >=0)){
        setTimeout(function(){
            _musicFade(_obj,isFadeIn,step);
        },MUSIC_ANIMATION_INTERVAL);
    }
}
/**
 * Gets the click animation of the clicked object, creates a new animation layer for it and plays
 * @param _obj clicked object
 */
function handleClick(_obj){
    var click_time = new Date().getTime();
    var _node = _findObjectNode(_obj);
    var click_animation = _node['animation']['click_animation'];
    for (var i = 0; i<click_animation['animations'].length;i++){
        click_animation['animations'][i]['anim'] = _parse_string_to_dict(click_animation['animations'][i]['anim']);
        click_animation['animations'][i]['pre'] = _parse_string_to_dict(click_animation['animations'][i]['pre']);
        click_animation['animations'][i]['object'] = _obj;
    }
    if(click_animation['stop_current_animation']){
        _obj.stop(true);
    }
    if(click_animation['clear_further_animations']){
        _clearObjectAnimationsFromQueues(_obj);
    }
    if(click_animation['disable_further_interaction']){
        _obj.unbind('click');
        _obj.unbind('mouseenter');
    }

    //Add performed operations to the user interaction queue to be able to imitate it later
    _userInteractionQueue.push({'animation':{'type':'sleep','duration':(click_time-last_user_interaction)}});
    _userInteractionQueue.push({'animation':{'type':'click','object':_obj}});
    _addInteractionAnimationLayerForObject(jQuery.extend(true,[],click_animation['animations']))
    last_user_interaction=click_time;
}

/**
 * Gets the hover animation of the clicked object, creates a new animation layer for it and plays
 * @param _obj clicked object
 */
function handleMouseEnter(_obj){
    var enter_time = new Date().getTime();
    var _node = _findObjectNode(_obj);
    var enter_animation = _node['animation']['hover_animation'];
    for (var i = 0; i<enter_animation['animations'].length;i++){
        enter_animation['animations'][i]['anim'] = _parse_string_to_dict(enter_animation['animations'][i]['anim']);
        enter_animation['animations'][i]['pre'] = _parse_string_to_dict(enter_animation['animations'][i]['pre']);
        enter_animation['animations'][i]['object'] = _obj;
    }
    if(enter_animation['stop_current_animation']){
        _obj.stop(true);
    }
    if(enter_animation['clear_further_animations']){
        _clearObjectAnimationsFromQueues(_obj);
    }
    if(enter_animation['disable_further_interaction']){
        _obj.unbind('click');
        _obj.unbind('mouseenter');
    }

    //Add performed operations to the user interaction queue to be able to imitate it later
    _userInteractionQueue.push({'animation':{'type':'sleep','duration':(enter_time-last_user_interaction)}});
    _userInteractionQueue.push({'animation':{'type':'hover','object':_obj}});
    _addInteractionAnimationLayerForObject(jQuery.extend(true,[],enter_animation['animations']))
    last_user_interaction=enter_time;
}

/**
 * Clears all! upcoming animations of the given objects from ever queue
 * Call before adding the interaction animations to the animation queue, since this will remove new animations from queue, too
 * @param _obj
 * @private
 */
function _clearObjectAnimationsFromQueues(_obj){ //We may need to pass objects to sleep etc. functions to be able to remove them here
    for(var i=0;i<animationQueue.length;i++){
        for(var j=0;j<animationQueue[i].length;j++){
            if(!animationQueue[i][j]['animation']['object']){
                continue;
            }
            if(animationQueue[i][j]['animation']['object'].selector ==='#'+_obj[0].id){ //TODO something better than concatenating with # ??
                animationQueue[i].splice(j,1);
            }
        }
    }
}

/**
 * Finds the clicked object in the momend_data
 * @param _obj dom object
 * @return {*} node from momend_data
 * @private
 */
function _findObjectNode(_obj){
    for(var i=0;i<momend_data['animation_layers'].length;i++){
        for(var j=0;j<momend_data['animation_layers'][i].length;j++){
            if(!momend_data['animation_layers'][i][j]['animation']['object']){
                continue;
            }
            if(momend_data['animation_layers'][i][j]['animation']['object'].selector ==='#'+_obj[0].id){
                return momend_data['animation_layers'][i][j];
            }
        }
    }
}

function _convertLayerToJSON(_layer){
    var layerCopy = jQuery.extend(true,[],_layer);
    for (var i=0; i<layerCopy.length;i++){
        if('object' in layerCopy[i]['animation']){
            layerCopy[i]['animation']['object'] = '#'+layerCopy[i]['animation']['object'][0].id;
        }
    }
    return JSON.stringify(layerCopy);
}

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

/**
 * Music load callback to keep if we can start playing music tracks when play-music animation arrives
 * @param _loaded_obj which track loaded
 * @private
 */
function _music_loaded(_loaded_obj){
    console.log('music loaded.');
    ready_music_count++;
    if(node_waiting_to_play){
        _handleNode(node_waiting_to_play,music_layer);
    }
}

function _calculate_dimensions(){
    var screen = $('.scene');
    keywordLookupTable = {
        '{{SCREEN_WIDTH}}' : screen.outerWidth(),
        '{{SCREEN_HEIGHT}}' : screen.outerHeight()
    }
}