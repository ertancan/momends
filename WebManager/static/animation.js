var JSAnimate = (function(){
    var screen = $('.scene');

    var animationQueue; // Keeps layers of animation data
    var _originalAnimationQueue; //Keeps the initial state of animationQueue since animationQueue changes during animations
    var shadowData; //Keeps shadow information of the objects
    var queueOnAction; // Boolean array indicates the given layer is active or not (e.g. queueOnAction[0] will be true if layer 0 started and working now)
    var currentAnimation; //Keeps the animations which are being processed right now
    var finishedAnimationQueue; //Keeps finished animation nodes in finishing order
    var _layerWaitQueue; //Each array in this queue keeps the ids of other layers waiting for the current animation on the queue
    //If _layerWaitQueue[0] has 1 and 2 in it, layers 1 and 2 will be started when the current animation in layer 0 finishes
    var _layerBreakPointWaitQueue; //Same principle as _layerWaitQueue but this waits for an animation which has type 'breakpoint' to trigger otherlayers
    var _userInteractionQueue; //Keeps the action performed by user during play.
    var lastUserInteraction = 0; //last time the user clicks on an item or mouse enters into the object boundaries.

    var MUSIC_ANIMATION_INTERVAL = 100; //Defines number of milliseconds between music fade animations. (e.g. if you perform fade animation with duration=1000ms
    // the animation will be performed in 5 steps. (Can be changed according to smoothness of the animation
    var readyMusicCount = 0; //How many of the remaining music are ready for playing.
    var nodeWaitingToPlay; //If the handle_node tried to play a music but it wasn't ready
    var currentMusicLayer; //Which layer belongs to music player
    var soundAnimationInProcess = false;
    var currentMusicObj;

    var pauseTime = 0; // Time that the user presses pause button, to calculate time between user interactions
    var pauseQueue; //Keeps the remaining animations that will be performed when un-paused
    var _isPlaying = false;

    var keywordLookupTable; //Keeps the latest values of keyword related values like {{SCREEN_WIDTH}}

    var animationFinishObserver = [];

    var volume;

    var isiPad = navigator.userAgent.match(/iPad/i);

    function _initAnimation(){
        $.cssEase._default = 'linear';
        $(window).resize(function(){
            _reCalculateDimensions();
        });
        volume = 100; //Default value if there is no cookie and so the callback won't be called
    }
    /**
     * Instantiates global variables according to number of levels needed.
     * @param _level number of animations layers
     */
    function __generateQueues(_level){
        animationQueue = [];
        _originalAnimationQueue = [];
        queueOnAction = [];
        currentAnimation = [];
        finishedAnimationQueue = [];
        _layerWaitQueue = [];
        _layerBreakPointWaitQueue = [];
        _userInteractionQueue = [];
        for(var i=0;i<_level;i++){
            animationQueue.push([]);
            _originalAnimationQueue.push([]);
            queueOnAction.push(false);
            currentAnimation.push([]);
            finishedAnimationQueue.push([]);
            _layerWaitQueue.push([]);
            _layerBreakPointWaitQueue.push([]);
        }
    }
    /**
     * Starts the given queue; flags it as on action and triggers the next animation on the queue
     * @param _level which level is going to start
     */
    function _startQueue(_level){
        if(queueOnAction[_level]){ //Already running
            return;
        }
        queueOnAction[_level]=true;
        _nextAnimation(_level, 'start queue');
    }
    /**
     * Starts all animation queues
     * !!Clears the user interaction timers, do not use unless you are starting a new animation!!
     */
    function _startAllQueues(){
        for (var i=0;i<animationQueue.length;i++){
            _startQueue(i);
        }
        lastUserInteraction = new Date().getTime();
        _isPlaying = true;
    }

    /**
     * Sets the running status of all queues to false, but not actually stops the current animations,
     * however, next animations will not be performed.
     */
    function _stopAllQueues(){
        for(var i = 0; i<queueOnAction.length; i++){
            queueOnAction[i] = false;
        }
    }
    /**
     * Clears the current animation queue and replaces it with the given one
     * @param _queue Layer of animations to be performed
     */
    function _setAnimationQueue(_queue){
        __generateQueues(_queue.length);
        animationQueue = jQuery.extend(true,[],_queue);
        for(var i = 0; i<animationQueue.length; i++){
            for(var j = 0; j<animationQueue[i].length;j++){
                animationQueue[i][j]['id'] = i+'-'+j;
            }
        }
        _originalAnimationQueue = jQuery.extend(true,[],animationQueue);
    }

    /**
     * Adds a dynamic shadow animation for given object
     * @param _obj jQuery dom object
     * @param _shadow animation dictionary containing keys: max_x, max_y, blur, spread, color(str), inset(bool)
     * @private
     */
    function _setShadowForObject(_obj, _shadow){
        if(!shadowData){
            shadowData = {};
        }
        shadowData[_obj.id] = _shadow;
    }

    /**
     * Sets the dynamic shadow animations of objects
     * @param _shadow_data dynamic shadow animation array
     */
    function _setShadowData(_shadow_data){
        shadowData = _shadow_data;
    }
    /**
     * Creates an additional animation queue level for user interaction animations like click or hover and hiding animations
     * @param animations Click or hover animations of an object
     */
    function __addInteractionAnimationLayerForObject(animations){
        animationQueue.push(animations);
        queueOnAction.push(false);
        currentAnimation.push([]);
        finishedAnimationQueue.push([]);
        _startQueue(animationQueue.length-1);
    }
    /**
     * Insert given node to the given layer of the queue.
     * !!If the level is on action and it is waiting empty, the animation will be performed immediately, so if you are adding
     * items to the queue one by one, it is most likely that it will be called like waitPrev option is false, so add elements
     * together in an array.
     * @param _level which the animations will be added
     * @param _node an animation object or an array containing animation objects.
     */
    function _addToQueue(_level,_node){
        var wasEmpty=false;
        if(animationQueue[_level].length===0){
            wasEmpty=true;
        }
        if(_node.constructor === Array){ //If adding an array of items
            for(var i=0;i<_node.length;i++){
                _node[i]['id'] = _level+'-'+animationQueue[_level].length;
                animationQueue[_level].push(_node[i]);
                _originalAnimationQueue[_level].push($.extend(_node, {}, true));
            }
        }else{ //Adding just one item
            _node['id'] = _level+'-'+animationQueue[_level].length;
            animationQueue[_level].push(_node);
            _originalAnimationQueue[_level].push($.extend(_node, {}, true));
        }
        if(wasEmpty && queueOnAction[_level]){
            _nextAnimation(_level, 'Add to running empty queue');
        }
    }
    /**
     * Handles a single node's animations
     * @param _node Whether the node itself or an object containing the node in 'animation' key
     * @param _level which level does the node belong to. (In order to trigger next animation)
     * @param _caller is whether the node or the describing string for debugging purposes
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
     *      trigger: Triggers any layer whether or not it was waiting a trigger; performs the next animation on the given layer
     *          target:(int) targeted layer
     *      click/hover: Performs click and hover animations on the object
     *      hide: Hides the given objects.
     *          it will perform 1 animation which is also given in the same node if the duration specified
     *          **Currently only action that supports 'delay' parameter which performs the action after given time
     *          **!!For now, 'duration' parameter is also required for delay, however this necessity will be removed after
     *              making delay globally supported option
     */
    function __handleNode(_node,_level, _caller){
        var _animation = _node;
        if('animation' in _node){
            _animation = _node['animation'];
        }
        _node['startTime'] = new Date().getTime();
        //if(_level == 4){
        if(typeof _animation['name'] !=='undefined'){
            //console.log('starting:'+_animation['name']+' on layer:'+_level+ ' called by:');
            if(typeof _caller === 'string'){
                //console.log(_caller)
            }else{
                //console.dir(_caller);
            }
        }else{
            //console.log('starting:'+_animation['type']+' on layer:'+_level+  ' called by:');
            if(typeof _caller === 'string'){
                //console.log(_caller)
            }else{
                //console.dir(_caller);
            }
        }
        //console.dir(_animation);
        //}
        if(_animation['type']==='sleep'){
            currentAnimation[_level].push(_node);
            //console.log('Layer '+_level+' now sleeping for '+_animation['duration']);
            _animation['sleepTimer'] = setTimeout(function(){
                //console.log('Layer '+_level+ ' sleep finished');
                __removeNodeFromCurrentQueue(_level,_node);
                _nextAnimation(_level,_node);
            },_animation['duration']);
            return;
        }
        var triggerNext=true;
        if(typeof _animation['triggerNext']!=='undefined'){
            triggerNext=_animation['triggerNext'];
        }

        var _type = _animation['type'];
        var _obj = null;
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
        var _delay=0;
        if('delay' in _animation){
            _delay = _animation['delay'];
        }
        var _target = null;
        if('target' in _animation){
            _target=_animation['target'];
        }
        if(_type==='animation'){
            var _shadow = shadowData[_obj[0].id];
            currentAnimation[_level].push(_node);
            if('pre' in _animation){
                for(var key in _animation['pre']){
                    if(typeof _animation['pre'][key] === 'function'){
                        _animation['pre'][key]=_animation['pre'][key]();
                    }
                    if(_animation['pre'][key] in keywordLookupTable){
                        _animation['pre'][key]=keywordLookupTable[_animation['pre'][key]];
                    }
                    _animation['pre'][key] = __replaceObjectKeywords(_animation['pre'][key],_obj);
                }
                _obj.css(_animation['pre']);
                if(_shadow){
                    var _shadowStr = __generateShadowStr(_obj, _shadow, null, null);
                    $(_obj[0].firstChild).css('box-shadow', _shadowStr); //Apply to image directly not to the div
                }
            }
            //if(_level ==1 && _animation['used_object_type'].indexOf('STATUS') == -1){ //Only first layer objects but statuses
            //    $(_obj[0].firstChild).box2d({'density':0.2,'x-velocity':-1,'debug':true});
            //}
            for(var key in _animation['anim']){
                if(typeof _animation['anim'][key] === 'function'){
                    _animation['anim'][key]=_animation['anim'][key]();
                }
                if(_animation['anim'][key] in keywordLookupTable){
                    _animation['anim'][key]=keywordLookupTable[_animation['anim'][key]];
                }
                _animation['anim'][key] = __replaceObjectKeywords(_animation['anim'][key],_obj);
            }
            var _easing =  $.cssEase._default;
            if('easing' in _animation){
                _easing = _animation['easing'];
            }
            if(_shadow){ //Handling animated shadow
                var _x = null, _y = null;
                if(_animation['anim']['left']){ //If animating on x axis
                    _x = _animation['anim']['left'];
                }else if(_animation['anim']['right']){ //Convert it to pixels if it is not left
                    var _right = _animation['anim']['right'];
                    if(_right.indexOf('px')>0){
                        _x = screen.outerWidth() - parseInt(_right.replace('px',''), 10);
                    }else if(_right.indexOf('%') > 0){
                        _x = screen.outerWidth() * (100 - parseFloat(_right.replace('%','')))/100;
                    }
                }

                if(_animation['anim']['top']){
                    _y = _animation['anim']['top'];
                }else if(_animation['anim']['bottom']){
                    var _bottom = _animation['anim']['bottom'];
                    if(_bottom.indexOf('px')>0){
                        _y = screen.outerHeight() - parseInt(_bottom.replace('px',''), 10);
                    }else if(_bottom.indexOf('%') > 0){
                        _y = screen.outerHeight() * (100 - parseFloat(_bottom.replace('%','')))/100;
                    }
                }
                if(_x || _y){ //If one of them animating
                    var _shadowStr = __generateShadowStr(_obj, _shadow, _x, _y);
                    //console.log('shadow animation for moving obj:'+_shadowStr);
                    if(_animation['extended_animation']){ //To support custom cubic-bezier easing on shadows
                        $(_obj[0].firstChild).transition({'box-shadow': _shadowStr}, _duration, _easing);
                    }else{
                        $(_obj[0].firstChild).animate({'box-shadow': _shadowStr},{duration:_duration, queue:false, easing:_easing}); //Apply to image directly not to the div
                    }
                }
            }
            if(_animation['extended_animation']){
                _obj.transition(_animation['anim'], _duration, _easing, function(){
                    __removeNodeFromCurrentQueue(_level,_node);
                    if(triggerNext){
                        _nextAnimation(_level, _node);
                    }
                });
            }else{
                _obj.animate(_animation['anim'],{duration:_duration, queue:false, easing:_easing, complete:function(){
                    __removeNodeFromCurrentQueue(_level,_node);
                    if(triggerNext){
                        _nextAnimation(_level, _node);
                    }
                }});
            }

        }
        else if(_type==='show'){ //Displays given object, it is like style display=block but handled by jquery
            _obj.show();
        }else if(_type==='hide'){ //Hide given object but perform the given animation if exists
            if(_duration > 0){
                var _hideAnimation = [];
                if(_delay > 0){ //Sleep first if hide animation has delay, to come back here after given delay, we add another animation object to the queue
                    _hideAnimation.push({'animation':{'type':'sleep', 'duration':_delay, 'name':'hide delay'}});
                }
                _hideAnimation.push({'animation':{'type':'animation', 'duration':_duration, 'object':_obj, 'waitPrev':true, 'name': 'hide animation'}}); //Create an empty animation
                var _animationIndex = _hideAnimation.length-1;
                if('pre' in _animation){ //Assign hide animation's pre and anim if they exists
                    _hideAnimation[_animationIndex]['animation']['pre'] = _animation['pre'];
                }
                if('anim' in _animation){
                    _hideAnimation[_animationIndex]['animation']['anim'] = _animation['anim'];
                }
                if(_animation['extended_animation']){
                    _hideAnimation[_animationIndex]['animation']['extended_animation'] = true;
                }
                _hideAnimation.push({'animation':{'type':'hide', 'duration':0, 'object':_obj, 'waitPrev':true, 'name':'Hide after delay'}}); //Insert an empty hide animation to hide the object after animation
                if(triggerNext){ //If hide animation should trigger the main queue(the queue which it was on)
                    _hideAnimation.push({'animation':{'type':'trigger', 'target':_level, 'waitPrev':true, 'name':'trigger main queue'}});
                }
                __addInteractionAnimationLayerForObject(_hideAnimation);
                //console.log('added hide animation:');
                //console.dir(_hideAnimation)
                return;
            }else{
                //console.log('Hiding now!!!');
                //console.dir(_obj);
                //console.log('layer:'+_level);
                _obj.hide();
                //console.log('Trigger next:'+triggerNext);
            }
        }else if(_type==='block'){
            if(typeof _target != 'number'){
                _target=_level;
            }
            queueOnAction[_target]=false;
            if(_animation['force']===true){ //force stop
                currentAnimation[_target]['object'].stop();
            }
        }else if(_type==='unblock'){
            if(typeof _target != 'number'){
                _target=_level;
            }
            _startQueue(_target);
        }else if(_type==='wait'){
            triggerNext=false;
            if(_target!==_level){
                queueOnAction[_level]=false;
                if(_animation['breakpoint']===true){ //Waiting for a break point on the target queue
                    _layerBreakPointWaitQueue[_target].push(_level);
                }else{
                    _layerWaitQueue[_target].push(_level); //Waiting the next action on the target queue
                }
            }
        }else if(_type==='breakpoint'){
            while(_layerBreakPointWaitQueue[_level].length!==0){
                _target=_layerBreakPointWaitQueue[_level].shift();
                _startQueue(_target);
            }
        }else if(_type==='trigger'){
            _nextAnimation(_target, _node);
        }
        else if(_type==='click'){
            _obj.click();
        }else if(_type==='hover'){
            _obj.mouseenter();
        }

        //Music animations below
        else if(_type === 'music-play'){
            if(isiPad){
                if(currentMusicObj){
                    currentMusicObj.jPlayer('stop'); //iOS won't let more than 1 tracks to be played
                }
            }
            currentMusicLayer = _level;
            currentMusicObj = _obj;
            if(readyMusicCount>0){ //If the music player object loaded and ready TODO check first music instead of loaded count
                _obj.jPlayer('play');
                nodeWaitingToPlay=null;
                readyMusicCount--;
                if(volume === 0){
                    _obj.jPlayer('volume', 0);
                }
            }else{
                //console.log('Music not ready yet, waiting');
                nodeWaitingToPlay=_node;
                _pause();
                return;
            }
        }else if(_type === 'music-pause'){
            _obj.jPlayer('pause');
        }else if(_type ==='music-stop'){
            _obj.jPlayer('stop');
        }else if(_type === 'music-volume'){
            var vol = parseFloat(_target);
            if(!isNaN(vol)){
                //console.log('New volume: '+ (vol*(volume/100))/100);
                _obj.jPlayer('volume', (vol*(volume/100))/100); //proportional to the volume slider's current value
            }
        }
        else if(_type === 'music-fadein'){
            if(volume!== 0){
                var currentVol = _obj.jPlayer('option','volume');
                __musicFade(_obj, true, ((volume/100)-currentVol)/(_duration/MUSIC_ANIMATION_INTERVAL), triggerNext);
                triggerNext = false; //Do not trigger next before music fade animation finishes.
            }
        }else if(_type === 'music-fadeout'){
            __musicFade(_obj, false,1/(_duration/MUSIC_ANIMATION_INTERVAL), triggerNext);
            triggerNext = false;
        }

        //Trigger next animation if needed
        if(_type!='animation' && triggerNext){
            _nextAnimation(_level, _node);
        }
    }


    /**
     * Triggers the next animation in the queue
     * @param _level level of the queue
     * @param _prev previous animation (to be sent to handle node)
     */
    function _nextAnimation(_level, _prev){
        if(currentAnimation.length!==animationQueue.length){
            //console.log('INCONSISTENCY!!!');
        }
        if(animationQueue[_level].length===0){
            if(_level === 1){
                _finish();
            }
            return;
        }
        if(!queueOnAction[_level]){
            return;
        }
        if(typeof _layerWaitQueue[_level]!=='undefined'){
            while(_layerWaitQueue[_level].length!==0){
                var waiting=_layerWaitQueue[_level].shift();
                _startQueue(waiting);
            }
        }
        var _node=animationQueue[_level].shift();
        __handleNode(_node,_level, _prev);
        try{
            if(animationQueue[_level].length!==0 && animationQueue[_level][0]['animation']['waitPrev']===false){
                _nextAnimation(_level, 'Wait Prev False');
            }
        }catch(error){
            //console.log('Animation error on level:'+_level+' : '+error);
            //console.dir(animationQueue[_level][0]);
        }
    }
    /**
     * Shows finish dialog and stops player functions and current animations
     * !Also informs finish observers!
     */
    function _finish(){
        $('#finished-bg').fadeIn();
        if(currentMusicObj){
            __musicFade(currentMusicObj, false,1/(2000/MUSIC_ANIMATION_INTERVAL), false); //Fadeout animation for 2 seconds
        }
        for(var i=0; i<animationFinishObserver.length; i++){
            animationFinishObserver[i]();
        }
        _stopAllQueues();

        //Change pause button to replay
        var button = $('#play-toggle');
        button.removeClass('icon-pause');
        button.addClass('icon-repeat');
        button.unbind('click');
        button.bind('click', function(){location.reload();});

        for(var i = 0; i< currentAnimation.length; i++){ //Stop active animations (i.e. background)
            for(var j = 0; j<currentAnimation[i].length; j++){
                var node = currentAnimation[i][j];
                if('animation' in node){
                    var _animation = node['animation'];
                    if('object' in _animation){
                        var _obj=_animation['object'];
                        if(_obj){
                            _obj.stop();
                        }
                    }
                }
            }
        }
    }

    /**
     * Pauses the current animation and saves the current states of animations to be able to resume
     */
    function _pause(){
        if(!_isPlaying){
            return;
        }
        pauseTime = new Date().getTime();
        _stopAllQueues();
        pauseQueue = [];
        for(var i = 0; i< currentAnimation.length; i++){
            pauseQueue.push([]);
            for(var j = 0; j<currentAnimation[i].length; j++){
                var node = currentAnimation[i][j];
                if('animation' in node){
                    node = node['animation'];
                }
                node = $.extend(node, {}, true);

                var passed = pauseTime - currentAnimation[i][j]['startTime']; //Time passed since the animation start
                node['duration'] = node['duration'] - passed; //Assign remaining time
                var _obj;
                if('object' in node){
                    _obj=node['object'];
                    if(typeof _obj === 'string'){
                        _obj = $(_obj);
                    }
                }
                if(_obj && node['type']==='animation'){
                    if(node['extended_animation']){
                        _obj.transitStop(); //!! this function was not approved yet and may be changed in next jquery.transit update
                    }else{ //Regular animation (plain jQuery)
                        _obj.stop();
                    }
                    pauseQueue[i].push(node);
                    $(_obj[0].firstChild).stop();
                }
                if(node['type']==='sleep'){
                    clearTimeout(node['sleepTimer']);
                    pauseQueue[i].push(node);
                }
            }
        }
        currentAnimation = [];
        for(var i = 0; i < animationQueue.length; i++){
            currentAnimation.push([]);
        }
        if(currentMusicObj){
            currentMusicObj.jPlayer('pause');
        }
        _isPlaying = false;
        _togglePlayButton(true);

    }

    function _resume(){
        for (var k = 0; k < queueOnAction.length; k++){ //Not calling _startAllQueues not to trigger first animations before remainders of previous
            queueOnAction[k] = true;
        }
        for(var i = 0; i< pauseQueue.length; i++){
            for(var j = 0; j < pauseQueue[i].length; j++){
                var node = pauseQueue[i][j];
                if('animation' in node){
                    node = node['animation'];
                }
                if('pre' in node){
                    node['pre'] = {}; //Clear pre-conditions, since they have already applied
                }
                __handleNode(node,i, 'Resume');
            }
        }
        if(currentMusicObj){
            currentMusicObj.jPlayer('play');
        }
        _isPlaying = true;
        _togglePlayButton(false);
    }

    /**
     * Handles fade-in and fade-out animations of musics.
     * USES: MUSIC_ANIMATION_INTERVAL from global variables
     *      music_layer from global variables if trigger next flag is true
     * CAUTION: stops the music animation if animation is fade out
     * @param _obj jPlayer object
     * @param isFadeIn true if the animation is fade in, false otherwise
     * @param step step value to be added or removed on every step of animation
     * @param triggerNextAfterFinish trigger next animation on the music queue
     * @private
     */
    function __musicFade(_obj, isFadeIn, step, triggerNextAfterFinish){
        var currentVol = _obj.jPlayer('option','volume');
        var targetVol;
        if(isFadeIn){
            targetVol = currentVol + step;
        }else{
            targetVol = currentVol - step;
        }
        _obj.jPlayer('volume',targetVol);
        if((isFadeIn && targetVol + step  <= (volume/100) ) || //Fade-in animation and not completed yet 
            (!isFadeIn && targetVol - step >=0)){ //Fade-out animation and not completed yet
            setTimeout(function(){
                __musicFade(_obj, isFadeIn, step, triggerNextAfterFinish);
            },MUSIC_ANIMATION_INTERVAL);
        }else{
            if(triggerNextAfterFinish){ //Fade animation completed and should trigger next music animation
                _nextAnimation(currentMusicLayer, 'music fade');
            }
            if(!isFadeIn){ //Fade out animation finished, we are going to stop the music
                _obj.jPlayer('stop');
            }
        }
    }
    /**
     * Volume slider's listener function, sets the volume if music player in steady mode (not animating)
     * @param _val Current value of the slider
     */
    function _volumeSliderChanged(_val){
        if(!soundAnimationInProcess && currentMusicObj){
            currentMusicObj.jPlayer('volume',_val/100);
        }
        volume = _val;
    }
    /**
     * Gets the click animation of the clicked object, creates a new animation layer for it and plays
     * @param _obj clicked object
     */
    function _handleClick(_obj){
        if(!_isPlaying){ //Don't let interactions if paused
            return;
        }
        var click_time = new Date().getTime();
        var _node = __findObjectNode(_obj);
        //console.dir(_node);
        var click_animation = _node['animation']['click_animation'];
        for (var i = 0; i<click_animation['animations'].length;i++){
            click_animation['animations'][i]['anim'] = _parseStringToDict(click_animation['animations'][i]['anim']);
            click_animation['animations'][i]['pre'] = _parseStringToDict(click_animation['animations'][i]['pre']);
            click_animation['animations'][i]['object'] = _node['animation']['object'];
        }
        if(click_animation['stop_current_animation']){
            _obj.parent().stop(true);
        }
        if(click_animation['clear_further_animations']){
            __clearObjectAnimationsFromQueues(_obj.parent());
        }
        if(click_animation['disable_further_interaction']){
            _obj.unbind('click');
            _obj.unbind('mouseenter');
        }

        //Add performed operations to the user interaction queue to be able to imitate it later
        _userInteractionQueue.push({'animation':{'type':'sleep','duration':(click_time-lastUserInteraction)}});
        _userInteractionQueue.push({'animation':{'type':'click','object':_obj}});
        __addInteractionAnimationLayerForObject(jQuery.extend(true,[],click_animation['animations']));
        lastUserInteraction=click_time;
    }

    /**
     * Gets the hover animation of the clicked object, creates a new animation layer for it and plays
     * @param _obj clicked object
     */
    function _handleMouseEnter(_obj){
        if(!_isPlaying){ //Don't let interactions if paused
            return;
        }
        var enter_time = new Date().getTime();
        var _node = __findObjectNode(_obj);
        var enter_animation = _node['animation']['hover_animation'];
        for (var i = 0; i<enter_animation['animations'].length;i++){
            enter_animation['animations'][i]['anim'] = _parseStringToDict(enter_animation['animations'][i]['anim']);
            enter_animation['animations'][i]['pre'] = _parseStringToDict(enter_animation['animations'][i]['pre']);
            enter_animation['animations'][i]['object'] = _node['animation']['object'];
        }
        if(enter_animation['stop_current_animation']){
            _obj.parent().stop(true);
        }
        if(enter_animation['clear_further_animations']){
            __clearObjectAnimationsFromQueues(_obj.parent());
        }
        if(enter_animation['disable_further_interaction']){
            _obj.unbind('click');
            _obj.unbind('mouseenter');
        }

        //Add performed operations to the user interaction queue to be able to imitate it later
        _userInteractionQueue.push({'animation':{'type':'sleep','duration':(enter_time-lastUserInteraction)}});
        _userInteractionQueue.push({'animation':{'type':'hover','object':_obj}});
        __addInteractionAnimationLayerForObject(jQuery.extend(true,[],enter_animation['animations']));
        lastUserInteraction=enter_time;
    }

    /**
     * Clears all! upcoming animations of the given objects from every queue
     * Call before adding the interaction animations to the animation queue, since this will remove new animations from queue, too
     * @param _obj
     * @private
     */
    function __clearObjectAnimationsFromQueues(_obj){ //We may need to pass objects to sleep etc. functions to be able to remove them here
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
     * Finds the clicked object in the animationQueue
     * @param _obj dom object
     * @return {*} node from animationQueue
     * @private
     */
    function __findObjectNode(_obj){
        //console.log('Looking for:');
        //console.log(_obj[0].id);
        var time = new Date().getTime();
        for(var i=0;i<_originalAnimationQueue.length;i++){
            for(var j=0;j<_originalAnimationQueue[i].length;j++){
                if(!_originalAnimationQueue[i][j]['animation']['object']){
                    continue;
                }
                if(_originalAnimationQueue[i][j]['animation']['object'][0].children[0].id ===_obj[0].id){
                    var foundTime=new Date().getTime();
                    //console.log('Found in:'+(foundTime-time));
                    return _originalAnimationQueue[i][j];
                }
            }
        }
        var finishTime=new Date().getTime();
        //console.log('Node not found in:'+(finishTime-time));
    }

    /**
     * Converts any given layer into JSON format, currently its intended use is for user animations
     * @param _layer number of the layer
     * @return JSON string
     * @private
     */
    function __convertLayerToJSON(_layer){
        var layerCopy = jQuery.extend(true,[],_layer);
        for (var i=0; i<layerCopy.length;i++){
            if('object' in layerCopy[i]['animation']){
                layerCopy[i]['animation']['object'] = '#'+layerCopy[i]['animation']['object'][0].id;
            }
        }
        return JSON.stringify(layerCopy);
    }

    function _convertUserInteractionLayerToJSON(){
        return __convertLayerToJSON(_userInteractionQueue);
    }

    /**
     * Music load callback to keep if we can start playing music tracks when play-music animation arrives
     * @param _loaded_obj which track loaded
     * @private
     */
    function _musicLoaded(_loaded_obj){
        readyMusicCount++;
        if(nodeWaitingToPlay ){
            _resume();
        }
    }

    /**
     * Saves the screen dimensions to use them parameter replacing
     * --Currently this function is also the callback of body's resize--
     * @private
     */
    function _reCalculateDimensions(){
        keywordLookupTable = {
            '{{SCREEN_WIDTH}}' : screen.outerWidth(),
            '{{SCREEN_HEIGHT}}' : screen.outerHeight()
        };
    }

    function __replaceObjectKeywords(_str, _obj){
        if(typeof _str !='string'){
            return null;
        }
        var _child = _obj.children()[0];
        return _str.replace('{{OBJECT_WIDTH}}',100*(_child.width/keywordLookupTable['{{SCREEN_WIDTH}}'])+'%'). //Replace with percent value instead of px
            replace('{{OBJECT_HEIGHT}}',100*(_child.height/keywordLookupTable['{{SCREEN_HEIGHT}}'])+'%');
    }

    /**
     * Generates parameter for box-shadow property according to shadow object given
     * @param _obj div that contains element to which will have the shadow
     * @param _shadow shadow object from shadowData
     * @param _targetX targeting x position if animating, null otherwise
     * @param _targetY targeting y position if animation, null otherwise
     * @return {String} to be given to css function as box-shadow value
     * @private
     */
    function __generateShadowStr(_obj, _shadow, _targetX, _targetY){
        var _x;
        var _y;
        var _photoObj = _obj[0].firstChild;
        if(!_targetX){
            _x = _photoObj.x;
        }else{
            if(typeof _targetX == 'number'){
                _x = _targetX;
            }else if(_targetX.indexOf('px')>0){ //Value is in pixels
                _x = parseFloat(_targetX.replace('px',''));
            }else if(_targetX.indexOf('%')>0){ //Value is in pixels
                _x = parseFloat(_targetX.replace('%','')) * screen.outerWidth() / 100; //Change % into px
            }else{
                //console.log('Not supported metric, expecting:int, px or %');
                return '';
            }
        }
        if(!_targetY){
            _y = _photoObj.y;
        }else{
            if(typeof _targetY == 'number'){
                _y = _targetY;
            }else if(_targetY.indexOf('px')>0){ //Value is in pixels
                _y = parseFloat(_targetY.replace('px',''));
            }else if(_targetY.indexOf('%')>0){ //Value is in pixels
                _y = parseFloat(_targetY.replace('%','')) * screen.outerHeight() / 100; //Change % into px
            }else{
                //console.log('Not supported metric, expecting:int, px or %');
                return '';
            }
        }
        _x += _photoObj.width/2;
        _y += _photoObj.height/2;
        var _placeX = _x / screen.outerWidth();
        var _placeY = _y / screen.outerHeight();
        _placeX -= 0.5; //Light is at the center of the screen
        _placeY -= 0.5;
        var _shadowStr = Math.ceil(_shadow['max_x'] * _placeX) +'px '+Math.ceil(_shadow['max_y'] * _placeY) +'px';
        if(_shadow['blur'] > 0){
            _shadowStr += ' '+_shadow['blur']+'px';
        }
        if(_shadow['spread'] > 0){
            _shadowStr += ' '+_shadow['blur']+'px';
        }
        _shadowStr += ' '+_shadow['color'];
        if(_shadow['inset']){
            _shadowStr += ' inset';
        }
        return _shadowStr;
    }

    /**
     * Searches the given layer's current animation queue and removes the node if found and adds node to finished animation queue
     * @param _level animation queue layer
     * @param _node to search
     * @private
     */
    function __removeNodeFromCurrentQueue(_level,_node){
        currentAnimation[_level] = $.grep(currentAnimation[_level], function(obj){
            return obj['id'] !== _node['id'];
        });
        finishedAnimationQueue[_level].push(_node);
    }

    function _togglePlayButton(toPlay){
        var button = $('#play-toggle');

        if(toPlay){
            button.removeClass('icon-pause');
            button.addClass('icon-play');
            button.unbind('click');
            button.bind('click', _resume);

        }else{
            button.removeClass('icon-play');
            button.addClass('icon-pause');
            button.unbind('click');
            button.bind('click', _pause);
        }
    }
    function _addFinishListenerFunction(_func){
        animationFinishObserver.push(_func);
    }
    return {
        initAnimation : _initAnimation,
        startQueue : _startQueue,
        startAllQueues : _startAllQueues,
        stopAllQueues : _stopAllQueues,
        setAnimationQueue : _setAnimationQueue,
        addToQueue : _addToQueue,
        nextAnimation : _nextAnimation,
        finish : _finish,
        pause : _pause,
        resume : _resume,
        volumeSliderChanged : _volumeSliderChanged,
        handleClick : _handleClick,
        handleMouseEnter : _handleMouseEnter,
        convertUserInteractionLayerToJSON : _convertUserInteractionLayerToJSON,
        musicLoaded : _musicLoaded,
        reCalculateDimensions : _reCalculateDimensions,
        addFinishListenerFunction : _addFinishListenerFunction,
        setShadowForObject : _setShadowForObject,
        setShadowData : _setShadowData,
        isPlaying : _isPlaying
    };
}());