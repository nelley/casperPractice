var URLArrays = [];
var CommentArrays = [];
var fs = require('fs');


var casper = require('casper').create({
    verbose: true,
    logLevel: 'debug',
    viewportSize: {width:1280, height:3000}
});

function getRandomIntFromRange(min, max) {
  return Math.round(Math.random() * (max - min)) + min;
}

function getAllPage(){
    casper.echo("START")
    var cp = require('child_process');

    r_ent_object = this.evaluate(function(){
        var ent_ele = document.querySelectorAll('#main-container > div.r-list-container.bbs-screen');
        return Array.prototype.map.call(ent_ele, function(e){
            return e.innerHTML;
        });
    });

    // call python
    var finished = false;
    cp.execFile('/usr/bin/python',['url_updater.py', r_ent_object],null,function(err,stdout,stderr){
        console.log("stdout=" + stdout);
        console.log("stderr=" + stderr);
        if(stdout != "done"){
            console.log("something happened!!");
            finished = false;
        }else{
            finished = true;
        }
    });
    // wait for python subprocess end    
    this.waitFor(function check(){
        return finished;
    }, function then(){//if finished is true
        this.echo('update go on'); 
    }, function timeout(){//if finished is false
        this.echo('BYE').exit();
    });

    //fs.write("tech_job_list.csv", AnchorArrays + ',', 'a'); 

    //require('utils').dump(AnchorArrays);
    var ranInt = getRandomIntFromRange(1000, 5000);
    casper.echo("wait for " + ranInt + " milliseconds");
    casper.wait(ranInt);
    
    var nextLink = "#action-bar-container > div > div.btn-group.btn-group-paging > a:nth-child(2)";

    if (casper.visible(nextLink)) {
        casper.thenClick(nextLink);
        casper.then(getAllPage);
    } else {
        casper.echo("END")
    }
}

casper.start('https://www.ptt.cc/bbs/Tech_Job/index.html');

casper.then(getAllPage);

casper.run();



