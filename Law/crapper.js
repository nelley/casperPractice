var URL = 'http://service.moj.gov.tw/lawer/associList.aspx?associName=%E5%8F%B0%E5%8C%97%E5%BE%8B%E5%B8%AB%E5%85%AC%E6%9C%83';

var stop = '吳天富';
var nameArray = [];
var spliceArrays = [];
var nameJSON = [];
var cnt = [];
var fs = require('fs');

// get laywer list in array
function getTexts(){
    //console.log('getTexts');
    var tmp = document.querySelectorAll('#lawyerList > div.floatDiv > a');
    return Array.prototype.map.call(tmp, function(e){
        return e.innerHTML;
    });
}

casper = require('casper').create({
    logLevel: 'debug',
    viewportSize:{width: 1280, height: 3000}        
});

// output msg from phantomJS brower
casper.on('remote.message', function(msg) {
    console.log('remote message caught: ' + msg);
})

//-------------------
// Logic start!!
// ------------------
casper.start(URL, function() {
    console.log("[NL]Open web site for getting the name array");
    nameArray = this.evaluate(getTexts);
    // remove the laywer name in English
    nameArray = this.evaluate(function(arr){
        var cnt = 0;
        for(var i = 0; i < arr.length; i++){
            if(arr[i].indexOf('莊明翰') != -1){
                cnt = i;
            }
        }
        arr.splice(0, cnt + 1);
        return arr;
    }, nameArray);
});

// loop whole nameArray
casper.then(function(){
    console.log('[NL]name array loop start');
    //require('utils').dump(nameArray); 
    //require('utils').dump(nameJSON);
    for(var i = 0; i < nameArray.length; i++){
        (function(cntr) {
            casper.thenOpen('http://www.pingluweb.com/', function() {
                console.log(nameArray[cntr]);
                this.sendKeys('#queryBox',nameArray[cntr],{reset: true});
            });
            // click the query button
            casper.then(function(){
                this.click('#search');
                this.wait(1000);
            });
           
            //casper.waitForSelector('#main-pie', function(){
            casper.then(function(){
                var fieldArr = [];
                var caseCount;
                //if(){}
                fieldArr = this.evaluate(function(){
                    var names = [];
                    names = $('#tagWindow tspan').text();
                    return names;
                });
                require('utils').dump(fieldArr);

                caseCount = this.evaluate(function(){
                    return $('#caseCount').text();
                });        
                require('utils').dump(caseCount);

                var workYears = this.evaluate(function(){
                    return $('#practiceYear').text();
                });
                require('utils').dump(workYears);
                
                // csv output
                fs.write('laywer.csv', nameArray[cntr] + "\," + 
                                       caseCount + "\," + 
                                       workYears + "\," + 
                                       fieldArr +"\n",
                                       "a");
            });
        })(i);
    }
});
casper.run();
