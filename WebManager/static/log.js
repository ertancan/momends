var MomendsLogger = (function(){
    var user;
    var mainURL = 'http://log.momends.com/momendslog/log.php?';
    var initialized = false;
    var last_event_time;
    var events;
    function _init(currentUser, details){
        if(!details){
            details = {};
        }
        if (typeof details === 'string'){
            details = {'msg': details};
        }
        if (currentUser){
            user = currentUser;
        }else{
            user = $.cookie('log_user');
            if(typeof user === 'undefined'){
                user = 'anonymous' + Math.floor(Math.random()*100000);
            }
        }
        $.cookie('log_user', user, {path: '/' });
        events = {};
        var cookie_last_event_time = $.cookie('last_event_time');
        details['init_cookie_last_event_time'] = cookie_last_event_time;
        var date = new Date();
        var time = date.getTime();
        details['init_time'] = date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();

        // Create new session if cookie does not exists or too old. Keep the "event order" otherwise
        if(typeof cookie_last_event_time === 'undefined' || (time - cookie_last_event_time) > 1000 * 60 * 60){  // older than 60 mins
            last_event_time = 0;
            $.cookie('log_session_id', 1, {path: '/' });  // Set order to 1 to indicate this is the first log of this session

            //Clearing some data to encode to JSON and send to server
            var nav = navigator;
            delete nav['mimeTypes'];
            delete nav['plugins'];
            delete nav['geolocation'];
            details['browser'] = nav;
        }else{
            last_event_time = cookie_last_event_time;
            order = $.cookie('log_session_id');

            // Adding some information to indicate we are restoring from cookie backup
            details['init_last_session_id'] = order;
            details['init_status'] = 'Found an active session, continuing it';
            if(typeof order === 'undefined'){  // Just in case
                $.cookie('log_session_id', 1, {path: '/' });  // Set order to 1
            }
        }
        initialized = true;
        _logEvent(details);  // Send an initialized logger event
    }

    /**
    *   Sends an event to log server, collects every possible error not to stop workflow
    *   @param event: a string or dictionary object to be encoded to JSON
    */
    function _logEvent(event){
        try{
            if (typeof event === 'string'){
                event = {'msg': event};
            }
            else if(typeof event !== 'object'){
                console.error('Event should be object or string');
                return;
            }
            if(!initialized){
                _init(null, {'msg': 'Initializing before event'});
            }

            //Generate full url since we are sending data via HTTP GET and url parameters.
            var url = mainURL + 'user=' + user;
            var date = new Date();
            var time = date.getTime();
            var order = $.cookie('log_session_id');
            order ++;  // Increase the latest id to keep the order,
                       // if two events happens simultaneously on different loggers,
                       // they will have the same order_id for 1 time then fix automatically

            // Human readable time, we also keep the arrival time and session start timestamp and differences between events
            event['event_time'] = date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();
            url += '&time_since_last_event=' + (time - last_event_time);
            last_event_time = time;
            url += '&event=' + encodeURIComponent(JSON.stringify(event));
            url += '&order=' + order;
            url += '&callback=?';  // To use JSONP
            events[url] = false;  // To keep track of which events have been sent, which are waiting etc. but not actively using

            $.getJSON(url,null,function(data){
                if (data.resp){
                    events[url] = true;
                }
            });
            $.cookie('log_session_id', order, {path: '/' });
            $.cookie('last_event_time', time, {path: '/' });
        }catch(e){
            console.log(e);
        }
    }
    return {
        init : _init,
        logEvent : _logEvent
    };
}());