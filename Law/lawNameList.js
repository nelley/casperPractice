(function(global) {
    var NL = {
        Lawyer:function(props){
            this.name = props.name || 'noName';
            this.years = props.years || 0;
            this.caseCount = props.caseCount || 0;
            this.EC = props.EC || 0;
            this.IP = props.IP || 0;
            this.MD = props.MD || 0;
            this.IW = props.IW || 0;
            this.EP = props.EP || 0;
            this.PC = props.PC || 0;
            this.GP = props.GP || 0;
            this.PE = props.PE || 0;
            this.FC = props.FC || 0;
            this.HI = props.HI || 0;
            this.CI = props.CI || 0;
            this.CD = props.CD || 0;
            this.ID = props.ID || 0;
            this.RD = props.RD || 0;
            this.BC = props.BC || 0;
            this.SA = props.SA || 0;
            this.LA = props.LA || 0;
            this.LP = props.LP || 0;
            this.BD = props.BD || 0;
            this.NC = props.NC || 0;
            this.TP = props.TP || 0;
            this.EA = props.EA || 0;
            this.FM = props.FM || 0;
            this.FT = props.FT || 0;
            this.PN = props.PN || 0;
            
            NL.Lawyer.prototype.hello = function () {
                return alert('Hello, ' + this.name + '!');
            };

            NL.Lawyer.prototype.allRecord = function() {
                var recordList;
                for (var key in this) {
                    if (this.hasOwnProperty(key)) {
                        recordList = recordList + this[key];
                    }
                }
                return console.log(recordList);
            };
        },

        createLawyer:function(props){
            return new NL.Lawyer(props || {});
        },
    };
    global.NL = NL;
})(this);

var URL = 'http://service.moj.gov.tw/lawer/associList.aspx?associName=%E5%8F%B0%E5%8C%97%E5%BE%8B%E5%B8%AB%E5%85%AC%E6%9C%83';

var CATEGORY = ['感情事件','智慧財產','醫療糾紛','網路世界','毒品問題',
                '支付命令','政府採購','環境保護','詐騙案件','遺產繼承',
                '公司經營','車禍糾紛','保險爭議','營造工程','兒少事件',
                '性侵案件','訴訟程序','勞資糾紛','銀行債務','國家賠償',
                '消費爭議','選舉訴訟','金融市場','公平交易','房地糾紛'
                ];

var CATE_EN = ['EC','IP','MD','IW','EP',
               'PC','GP','PE','FC','HI',
               'CI','CD','ID','RD','BC',
               'SA','LA','LP','BD','NC',
               'TP','EA','FM','FT','PN'
               ];

var nameArray = [];
var spliceArrays = [];
var nameJSON = [];
var cnt = [];
var fs = require('fs');

var testArray = ["蘇盈貴"/*,"謝永誌","賴文萍"*/];
// get laywer list in JSON
function getJSON(){
    //console.log('getTexts');
    var nameArray = document.querySelectorAll('#lawyerList > div.floatDiv > a');
    var jsonData = [];
    Array.prototype.map.call(nameArray, function(e){
        var item = {};
        item['name'] = e.innerHTML;
        jsonData.push(item);
    });
    return jsonData;
}
// get laywer list in array
function getTexts(){
    //console.log('getTexts');
    var tmp = document.querySelectorAll('#lawyerList > div.floatDiv > a');
    return Array.prototype.map.call(tmp, function(e){
        return e.innerHTML;
    });
}

function sliceEng(arr){
    var cnt = 0;
    for(var i = 0; i < arr.length; i++){
        if(arr[i].match(/[a-zA-Z]/g) !== null){
            cnt = i;
        }
    }
    arr.splice(0, cnt + 1);
    console.log('evaluate' + cnt);
    return cnt + 1;
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
    fs.write('laywer_nameArray.csv', nameArray, "a");
    // remove the laywer name in English
    nameArray = this.evaluate(function(arr){
        var cnt = 0;
        for(var i = 0; i < arr.length; i++){
            if(arr[i].match(/[a-zA-Z]/g) !== null){
                cnt = i;
            }
        }
        arr.splice(0, cnt + 1);
        return arr;
    }, nameArray);
    //nameJSON = this.evaluate(getJSON);
    //var tmp = NL.createLawyer({name:"test", BD:"20"});
    //console.log(tmp.name + "_" + tmp.BD);
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
/*
// splice the array if too large
casper.then(function(){

    spliceArrays = this.evaluate(function(arr){
        //console.log('[spliceArray]' + arr.length);
        var splitArrays = [];
        var num = 100;
        while(arr.length > num){
            var tmpArr = arr.splice(0, num);
            splitArrays.push(tmpArr);
        }
        splitArrays.push(arr);
        return splitArrays;
    }, nameArray);
});
*/
casper.run();
