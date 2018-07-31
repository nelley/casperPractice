var casper = require('casper').create();
var urls = ["https://www.ys-consulting.com.tw/seminar",
            "https://www.ys-consulting.com.tw/seminar/list/1.html",
            "https://www.ys-consulting.com.tw/seminar/list/2.html?page=4",
            "https://www.ys-consulting.com.tw/seminar/list/2.html?page=2",
            "https://www.ys-consulting.com.tw/seminar/list/2.html?page=4",
            "https://www.ys-consulting.com.tw/seminar/yearlist/2006.html",
            "https://www.ys-consulting.com.tw/seminar/yearlist/2007.html",
            "https://www.ys-consulting.com.tw/seminar/yearlist/2008.html",
            "https://www.ys-consulting.com.tw/seminar/yearlist/2008.html?page=2",
            "https://www.ys-consulting.com.tw/seminar/yearlist/2008.html?page=1"
           ];

var testCaseNo = [
            "1-5","10-12","13","14","15",
            "23","24","25","26","27"
];

casper.start();
var i = 0;

casper.each(urls, function(self, link){
    this.thenOpen(link, function(){
        // dump screenshots
        this.capture('ScreenShot/Seminar/' + testCaseNo[i] + '.png');
        i++;
    });
});
//処理の実行
casper.run();

