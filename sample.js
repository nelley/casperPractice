casper = require('casper').create({
    verbose: true, 
    logLevel: 'debug',
    pageSettings: {
         loadImages:  false,         // The WebPage instance used by Casper will
         loadPlugins: false,         // use these settings
         userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4'
    },
    viewportSize:{width: 1280, height: 3000}        
});

var URL = "https://p3.www.stg.ys-consulting.com.tw/login/";

casper.start().thenOpen(URL, function() {
    console.log("[NL]YS website opened");
});

casper.then(function(){
    console.log("[NL]Login using username and password");
    this.evaluate(function(){
        document.getElementById("InputEmail1").value="doublenunchakus@gmail.com";
        document.getElementById("InputPassword1").value="notsniw0405";
    });
});

/*
casper.start(URL, function() {
    this.fill('form#loginForm', {
              'email1':'doublenunchakus@gmail.com',
              'password':'notsniw0405'
               }, true);
});*/

casper.then(function(){
    this.click('.btn-sm');
    this.wait(500);
});

casper.then(function(){
    this.capture('test.png');
});

casper.run();

