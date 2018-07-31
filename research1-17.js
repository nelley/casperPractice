var casper = require('casper').create({
    viewportSize:{width: 1280, height: 6000}
});

var URL = 'https://p3.www.stg.ys-consulting.com.tw/research/';

var testCaseNo = [
    "1-8","9-10","13","14","15",
    "16-17"
];

casper.start();
var i = 0;
//---------test case 1------------
casper.start(URL, function() {
    this.capture('ScreenShot/Research/1-8/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});

//---------test case 2------------
casper.thenOpen(URL, function(){
    // category gyoukai jyannaru
    this.click('div.row:nth-child(7) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(1)'); 
});

casper.then(function(){
    // click search button
    this.capture('ScreenShot/Research/1-8/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});

//---------test case 3------------
casper.thenOpen(URL, function(){
    this.click('div.row:nth-child(7) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(1)');
    this.wait(500);
});

casper.then(function(){
    this.click('#article-panels > div:nth-child(4) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2) > a:nth-child(1)');

});

casper.then(function(){
    this.capture('ScreenShot/Research/1-8/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});

//---------test case 4------------
casper.thenOpen(URL, function(){
    this.sendKeys('#id_q', '%');
});

casper.then(function(){
    this.click('div.hidden-xs:nth-child(2) > div:nth-child(2) > form:nth-child(1) > div:nth-child(3) > button:nth-child(1)');
});

casper.then(function(){
    this.capture('ScreenShot/Research/1-8/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});


//---------test case 5------------
casper.thenOpen(URL, function(){
    this.sendKeys('#id_q', '@');
});

casper.then(function(){
    this.click('div.hidden-xs:nth-child(2) > div:nth-child(2) > form:nth-child(1) > div:nth-child(3) > button:nth-child(1)');
});

casper.then(function(){
    this.capture('ScreenShot/Research/1-8/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});

//---------test case 6------------
casper.thenOpen(URL, function(){
    this.click('label.radio-inline:nth-child(1)');
});

casper.then(function(){
    this.click('div.hidden-xs:nth-child(2) > div:nth-child(2) > form:nth-child(1) > div:nth-child(3) > button:nth-child(1)');
});

casper.then(function(){
    this.capture('ScreenShot/Research/1-8/' + testCaseNo[i] + '.png');
    this.wait(500);
    i++;
});

//処理の実行
casper.run();


