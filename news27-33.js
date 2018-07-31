// variables with testCase name
var casper = require('casper').create({
    viewportSize:{width: 1280, height: 3000}
});

    
var p3_urls_text = [
    "news",
    //"seminar",
    //"research"
];

var p3_urls = [
    "https://p3.www.stg.ys-consulting.com.tw/news/"
    //"https://p3.www.stg.ys-consulting.com.tw/seminar/",
    //"https://p3.www.stg.ys-consulting.com.tw/research/"
];

var test_texts = [
    "日本人",
    "台湾人",
    "韓国人",
    "@",
    "(",
    ")",
    "*"
];

casper.start().zoom(1);

var i = -1;
casper.eachThen(p3_urls, function(response){
    // response is the current data attached(p3_urls)    
    this.thenOpen(response.data, function(){
        this.wait(500);
    });

    this.each(test_texts, function(self, test_text){
        this.then(function(){
            this.click('#djHideToolBarButton');
            this.sendKeys('#search', test_text, {reset: true});
        });

        this.then(function(){
            this.click('#main > div.navbar.navbar-blue.navbar-static-top > nav:nth-child(3) > form > div > div > button > i');
        });

        this.then(function(){
            this.captureSelector('ScreenShot/News/29-35/' + p3_urls_text[i] + test_text + '_' + 'testCase.png', 'body');
        });
    });
    ++i;
});

//処理の実行
casper.run();
