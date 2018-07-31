var casper = require('casper').create({
    viewportSize:{width: 1280, height: 3000}        
});
var p3_urls = [
                "https://p3.www.stg.ys-consulting.com.tw/news",
                "https://p3.www.stg.ys-consulting.com.tw/news/about.html",
                "https://p3.www.stg.ys-consulting.com.tw/service/",
                "https://p3.www.stg.ys-consulting.com.tw/service/",
                "https://p3.www.stg.ys-consulting.com.tw/service/",
                "https://p3.www.stg.ys-consulting.com.tw/",
                "https://p3.www.stg.ys-consulting.com.tw/news/l/25/"

];

var urls = [
                "https://www.ys-consulting.com.tw/news",
                "https://www.ys-consulting.com.tw/news/about.html",
                "https://www.ys-consulting.com.tw/service/",
                "https://www.ys-consulting.com.tw/service/",
                "https://www.ys-consulting.com.tw/service/",
                "https://www.ys-consulting.com.tw/",
                "https://www.ys-consulting.com.tw/news/l/25/"
];

var testCaseNo = [
            "1-7","8","9","10","11",
            "12","13"
];

casper.start();
var i = 0;

casper.each(p3_urls, function(self, link){
    this.thenOpen(link, function(){
        // dump screenshots
        this.capture('ScreenShot/News/1-13/' + testCaseNo[i] + '.png');
        this.wait(400);
        i++;
    });
});
//処理の実行
casper.run();


