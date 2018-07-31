var casper = require('casper').create({
    viewportSize:{width: 1280, height: 3000}        
});
var p3_urls = [
                "https://p3.www.stg.ys-consulting.com.tw/column",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/9/?page=1",
                "https://p3.www.stg.ys-consulting.com.tw/column/13605.html",
                "https://p3.www.stg.ys-consulting.com.tw/column/6031.html",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/45/?page=4",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/11/",
                "https://p3.www.stg.ys-consulting.com.tw/column/21151.html",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/66/",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/9/",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/9/94/",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/9/94/?page=4",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/9/94/?page=4",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/9/94/?page=2",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/9/94/?page=1",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/9/?page=3",
                "https://p3.www.stg.ys-consulting.com.tw/column/l/9/?page=4"
];

var urls = [
                "https://www.ys-consulting.com.tw/column",
                "https://www.ys-consulting.com.tw/column/l/9/?page=1",
                "https://www.ys-consulting.com.tw/column/13605.html",
                "https://www.ys-consulting.com.tw/column/6031.html",
                "https://www.ys-consulting.com.tw/column/l/45/?page=4",
                "https://www.ys-consulting.com.tw/column/l/11/",
                "https://www.ys-consulting.com.tw/column/21151.html",
                "https://www.ys-consulting.com.tw/column/l/66/",
                "https://www.ys-consulting.com.tw/column/l/9/",
                "https://www.ys-consulting.com.tw/column/l/9/94/",
                "https://www.ys-consulting.com.tw/column/l/9/94/?page=4",
                "https://www.ys-consulting.com.tw/column/l/9/94/?page=4",
                "https://www.ys-consulting.com.tw/column/l/9/94/?page=2",
                "https://www.ys-consulting.com.tw/column/l/9/94/?page=1",
                "https://www.ys-consulting.com.tw/column/l/9/?page=3",
                "https://www.ys-consulting.com.tw/column/l/9/?page=4"
           ];

var testCaseNo = [
            "1-2","3","4","5","6",
            "7","8","9","12","13",
            "14","15","16","17","18",
            "19"
];

casper.start();
var i = 0;

casper.each(p3_urls, function(self, link){
    this.thenOpen(link, function(){
        // dump screenshots
        this.capture('ScreenShot/Column/' + testCaseNo[i] + '.png');
        i++;
    });
});
//処理の実行
casper.run();


