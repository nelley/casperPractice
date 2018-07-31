var casper = require('casper').create({
    viewportSize:{width: 1280, height: 3000}        
});

var testCaseNo = [
            "22","23","24","25","26"
];

casper.start();
var i = 0;

//------ testCase 1------//
casper.start('https://p3.www.stg.ys-consulting.com.tw/news/', function() {
    // category:
    this.click('label.radio-inline:nth-child(6)');
});

casper.then(function(){
    // click search button
    this.click('button.btn:nth-child(7)');
});

casper.then(function(){
    this.capture('ScreenShot/News/22-26/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});

//------ testCase 2------//
casper.thenOpen('https://p3.www.stg.ys-consulting.com.tw/news/', function(){
    // category:forest
    this.click('label.radio-inline:nth-child(14)'); 
});

casper.then(function(){    
    this.sendKeys('#id_from_date', "2014-02-10");
    this.sendKeys('#id_to_date', "2015-02-10");
});

casper.then(function(){
    // click search button
    this.click('button.btn:nth-child(7)');
});

casper.then(function(){
    this.capture('ScreenShot/News/22-26/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});


//------ testCase 3------//
casper.thenOpen('https://p3.www.stg.ys-consulting.com.tw/news/', function(){
    // category:forest
    this.click('label.radio-inline:nth-child(14)'); 
});

casper.then(function(){    
    this.sendKeys('#id_from_date', "2015-02-11");
    this.sendKeys('#id_to_date', "2015-02-10");
});

casper.then(function(){
    // click search button
    this.click('button.btn:nth-child(7)');
});

casper.then(function(){
    this.capture('ScreenShot/News/22-26/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});

//------ testCase 4------//
casper.thenOpen('https://p3.www.stg.ys-consulting.com.tw/news/', function(){
    // category:forest
    this.click('label.radio-inline:nth-child(14)'); 
});

casper.then(function(){    
    this.sendKeys('#id_from_date', "2014-02-10");
    this.sendKeys('#id_to_date', "2015-02-10");
});

casper.then(function(){
    // click search button
    this.click('button.btn:nth-child(7)');
});

casper.then(function(){
    // click paging button
    this.click('.glyphicon-step-forward');
});

casper.then(function(){
    this.capture('ScreenShot/News/22-26/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});

//------ testCase 5------//
casper.thenOpen('https://p3.www.stg.ys-consulting.com.tw/news/', function(){
    // category:forest
    this.click('label.radio-inline:nth-child(14)'); 
});

casper.then(function(){    
    this.sendKeys('#id_from_date', "2014-02-10");
    this.sendKeys('#id_to_date', "2015-02-10");
});

casper.then(function(){
    // click search button
    this.click('button.btn:nth-child(7)');
});

casper.then(function(){
    // click paging button
    this.click('.pagination > li:nth-child(3) > a:nth-child(1)');
});

casper.then(function(){
    this.capture('ScreenShot/News/22-26/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});



//処理の実行
casper.run();


