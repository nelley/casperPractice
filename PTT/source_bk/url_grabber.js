// cmd: casperjs url_grabber.js --category=<PTT board's name>
// looping and retrive html content to url_updater.py

//processing start time
var t0 = performance.now()

var CommentArrays = [];
var fs = require('fs');
var URL_ARRAY = {'gossip':'https://www.ptt.cc/bbs/Gossiping/index.html',
                'tech_job':'https://www.ptt.cc/bbs/Tech_Job/index.html',
                'salary':'https://www.ptt.cc/bbs/Salary/index.html'}

var insert_cnt = 0;
var update_cnt = 0;
var FINISH_IN_ERR = 1;
var FINISH_IN_NORMAL = 0;

var json_summary = new Object();

var casper = require('casper').create({
    pageSettings: {
        loadImages:  false,        // load images disable
        loadPlugins: false         // load plugin disable
    },
    verbose: false,
    logLevel: 'debug',
    viewportSize: {width:1280, height:3000}
});

var category = casper.cli.get('category')
json_summary.category = category;


function getRandomIntFromRange(min, max) {
  return Math.round(Math.random() * (max - min)) + min;
}



function cron_reconfiger(cas, flag){
    cas.log('cron_reconfiger start', 'debug');
    var cp2 = require('child_process');
    var sec_finished = false;
    cp2.execFile('/usr/bin/python',['/home/nelley/casperPractice/PTT/cron_url.py', category, category, flag],null,function(err,stdout,stderr){
        //console.log('cron_url.py started');
    });
    cas.waitFor(function check(){
        return sec_finished;
    }, function then(){
        cas.log('cron_reconfiger return true', 'debug');
        cas.exit();
    }, function timeout(){
        cas.log('cron_reconfiger return false', 'debug');
        cas.exit();
    });

}


// before crawl gopssiping, there is a check page
function ask18(){
    //var ask18="div.over18-button-container:nth-child(2) > button:nth-child(1)";
    var ask18="body > div.bbs-screen.bbs-content.center.clear > form > div:nth-child(2) > button";
    if(casper.visible(ask18)){
        casper.thenClick(ask18);
        casper.wait(getRandomIntFromRange(2000,5000));
    }
}

function getAllPage(){
    casper.log('START', 'debug')
    
    var cp = require('child_process');

    // retrive all html text under tag r-list-container.bbs-screen
    r_ent_object = this.evaluate(function(){
        var ent_ele = document.querySelectorAll('#main-container > div.r-list-container.bbs-screen');
        return Array.prototype.map.call(ent_ele, function(e){
            return e.innerHTML;
        });
    });

    //require('utils').dump(r_ent_object);
    // call python
    var finished = false;
    var json_stdout ='';
    cp.execFile('/usr/bin/python',['/home/nelley/casperPractice/PTT/url_updater.py', r_ent_object, category],null,function(err,stdout,stderr){
        //console.log("stdout=" + stdout);  //will output to the screen
        //console.log("stderr=" + stderr);  //will output to the screen
        json_stdout = JSON.parse(stdout);
        if(json_stdout.result != "done"){
            finished = false;
        }else{
            insert_cnt+=json_stdout.total_insert;
            update_cnt+=json_stdout.total_update;
            finished = true;
        }
    });
    // wait for python subprocess end    
    this.waitFor(function check(){
        return finished;
    }, function then(){//if finished is true
        this.log('update go on', 'debug'); 
    }, function timeout(){//if finished is false
        // expected finish pattern
        if(json_stdout.result == 'encountered over-ranged article'){
            var t1 = performance.now();
            var elapsedT = t1-t0;
            this.log('Processing Time Of '+ category + ' : ' + elapsedT + ' miliseconds', 'debug');

            this.log('url_grabber finished, reconfig cron job', 'debug');

            json_summary.insert_cnt = insert_cnt;
            json_summary.update_cnt = update_cnt;
            json_summary.log = this.result.log;
            json_summary.elapsed_time = elapsedT;
            
            cron_reconfiger(this, FINISH_IN_NORMAL);
            console.log(JSON.stringify(json_summary));

        }else{
            this.log('Exception happened, reconfig cron job', 'debug');
            cron_reconfiger(this, FINISH_IN_ERR);
        }

    });

    //fs.write("tech_job_list.csv", AnchorArrays + ',', 'a'); 

    //require('utils').dump(AnchorArrays);
    var ranInt = getRandomIntFromRange(1000, 5000);
    casper.log("wait for " + ranInt + " milliseconds", 'debug');
    casper.wait(ranInt);
    
    var nextLink = "#action-bar-container > div > div.btn-group.btn-group-paging > a:nth-child(2)";

    if (casper.visible(nextLink)) {
        casper.thenClick(nextLink);
        casper.then(getAllPage);
    } else {
        // if became last page
        casper.log("END", 'debug');
    }
}


casper.start(URL_ARRAY[category]);
casper.then(ask18);
casper.then(getAllPage);

casper.run();

