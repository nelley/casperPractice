//cmd:casperjs crawl_content.js --category='<board's name>'
//
//REMIND!!! if check console.log is necessary, please redirect logging to file by modifying crontab's config
//DO NOT USER echo or set verbose to "true", because it will streaming into stdout
//and update_content_Logs.py needs JSON stdin, its cause the exception!!
//
//
var url_list;
var json_num_index = 0;
var t0 = performance.now();
var json_summary = new Object();
var PATH = '/home/nelley/casperPractice/PTT/';
var SPLIT_STD = 8000;


var casper = require('casper').create({
    verbose: true,
    logLevel: 'debug',
    viewportSize: {width:1280, height:3000}
});

var category = casper.cli.get('category');
json_summary.category = category;

// logging timestamp formatting
Object.defineProperty(Date.prototype, 'YYYYMMDDHHMMSS', {
    value: function() {
        function pad2(n) {  // always returns a string
            return (n < 10 ? '0' : '') + n;
        }

        return this.getFullYear() + '/' +
               pad2(this.getMonth() + 1) + '/' +
               pad2(this.getDate()) + ' ' +
               pad2(this.getHours()) + ':' +
               pad2(this.getMinutes()) + ':' +
               pad2(this.getSeconds());
    }
});


// set logging timestamp
var _oldLog = casper.log;
casper.log = function(message, level, space) {
    var message_with_date = "[" + new Date().YYYYMMDDHHMMSS() + "] " + message;
    _oldLog.call(this, message_with_date, level, space);
};

function shuffle(arr){
    var i, j, temp;

    for(i=arr.length-1; i>0; i--){
        j=Math.floor(Math.random()*(i+1));
        temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
    return arr
}


// before crawl gopssiping, there is a check page
function ask18(){
    var ask18="body > div.bbs-screen.bbs-content.center.clear > form > div:nth-child(2) > button";
    if(casper.visible(ask18)){
        casper.thenClick(ask18);
        casper.wait(getRandomIntFromRange(2000,5000));
    }
}

/*process before finish crawl_content.js*/
function endProcess(cas){

        var t1 = performance.now();
        var elapsedT = t1-t0;
        cas.log('Processing Time Of ' + category + ':' + elapsedT + ' miliseconds', 'debug')
        json_summary.log = cas.result.log;
        json_summary.elapsed_time = elapsedT;

        // stdout for logging by update_content_Logs.py
        console.log(JSON.stringify(json_summary));
}

/*calculate the power of 2 from source recursively*/
function depth_cal(source, cnt){
    if(source <= 1){
        return cnt;
    }
    cnt++;
    var std = Math.ceil(source/2);
    if(std >= 2){
        return depth_cal(std, cnt);
    }
    return cnt;
}

/*split html content recursively*/
function splitter(dep, arr){
    if(dep == 0){
        return arr;
    }
    var result=[];
    for(var item in arr){
        var tl = item.length;
        var half = tl/2;

        var part1 = item.substring(0, half);
        var part2 = item.substring(half, tl);

        result.push(part1);
        result.push(part2);
    }
    if(dep > 1){
        return splitter(dep-1, result);
    }
    return result;

}

/**/
function contentSplitter(source){
    //this.log('Before split:'+ source, 'debug');
    var src = [];
    src.push(source);

    // get the length of whole html content
    var tl = source.length;
    //this.log('tl length:'+ tl);
    var depth = depth_cal(Math.ceil(tl/SPLIT_STD), 0);
    return splitter(depth, src);

}




function getRandomIntFromRange(min, max) {
  return Math.round(Math.random() * (max - min)) + min;
}

function getAllContext(){
    var cp = require('child_process');
    var current = 0;
    //var end = 5;
    var end = url_list.length;

    for(; current < end; current++){
        (function(cntr){
            casper.thenOpen('https://www.ptt.cc'+url_list[cntr].url, function(){
                this.echo('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'+ cntr + '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!');
                this.echo('casper.async url:' + url_list[cntr].url);
                var param = [];
                param.push(PATH + 'pttParser_mecab.py');
                this.log('length of html:'+casper.getHTML().length, 'debug');
                //split html into parts(execFile will crash is one argument is too large)
                var content = casper.getHTML();
                var tl = casper.getHTML().length;
                var depth = depth_cal(Math.ceil(tl/SPLIT_STD), 0);
                var divide = Math.pow(2, depth);

                this.log('depth of html:'+depth, 'debug');
                this.log('divide:'+divide, 'debug');

                for(var i=0; i<divide+1; i++){
                    var tmp = content.slice(0, Math.ceil(tl/divide));
                    content = content.replace(tmp,'');
                    param.push(tmp);
                }
                // streaming logs to mongodb 
                var json_log_obj = new Object();
                json_log_obj.logs = this.result.log;
                // empty the array which stores logs
                this.result.log = [];
                param.push(url_list[cntr].url);
                param.push(category);
                param.push(JSON.stringify(json_log_obj));
                var already_done;
                cp.execFile('/usr/bin/python', param, null,function(err,stdout,stderr){
                    parse_result =JSON.parse(stdout);
                    if(parse_result.result == 'done'){
                        already_done = true;
                    }else{
                        already_done = false;
                    }
                });

                this.waitFor(function check(){
                    //this.log('pttParser result value:' + already_done, 'debug');
                    return already_done;

                }, function then(){
                    this.log('pttParser result value:' + already_done, 'debug');
                    this.log('already_done is true')
                    
                }, function timeout(){
                    this.log('pttparser timeout')
                }, 1000*30);

                //var ranInt = getRandomIntFromRange(3000, 5000);
                //casper.wait(ranInt);
            });
        })(current);
    }

}

function getURL(){
    var sub_p = require('child_process');
    var finished = false;
    this.log('category:' + category, 'debug');
    // get URLs from DB
    sub_p.execFile('/usr/bin/python',[PATH + 'url_getter.py', category],null,function(err,stdout,stderr){
        //console.log("stdout=" + stdout);
        //console.log("stderr=" + stderr);

        //there is a attr in url_list:url
        url_list =JSON.parse(stdout);
        
        //for test
        //url_list = [{'url':'/bbs/Gossiping/M.1488980461.A.3CF.html', 'is_content_updated':false}]
 
        if(url_list == "db query error"){
            finished = false;
        }else{
            finished = true;
            shuffle(url_list);
        }
    });


    // monitoring the return value from py script
    this.waitFor(function check(){
        //this.log('url_getter finish value:' + finished, 'debug');
        return finished;
    }, function then(){//if finished is true
        this.log('got URL list. access each url to get content. url_list size=' + url_list.length, 'debug');
        if(url_list.length > 0){
            casper.emit('getAllContext');
        }else{
            this.log('Nothing new to update the content from URL','debug');
        }
    }, function timeout(){//if finished is false(db query error)
        this.log('something happened in crawl_content.js due to DB issue', 'debug');
        endProcess(this);
        this.exit();
    }, 1000*150);

}

casper.start('https://www.ptt.cc/ask/over18');
casper.then(ask18);
casper.then(getURL);
casper.then(getAllContext);
casper.run();

