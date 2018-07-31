var URL = 'http://service.moj.gov.tw/lawer/associList.aspx?associName=%E5%8F%B0%E5%8C%97%E5%BE%8B%E5%B8%AB%E5%85%AC%E6%9C%83';
var nameArray = [];
var testArray = ['蘇盈貴','謝永誌','賴文萍'];

// get laywer list
function getTexts(){
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
    console.log("[NL]Open web site");
    //nameArray = this.getElementsAttribute('#lawyerList > div.floatDiv > a', 'text');
    //nameArray = this.fetchText('#lawyerList > div.floatDiv > a');
    //nameArray = this.getElementInfo('#lawyerList > div.floatDiv > a').text;

    //nameArray = this.evaluate(getTexts);
});

casper.then(function(){
    require('utils').dump(nameArray); 
    //this.capture('lawTest.png');
});

// connect to pinglu web service
casper.thenOpen('http://www.pingluweb.com/',function(){
    for(var i = 0; i < testArray.length; i++){
        console.log('test data:' + testArray[i]);
    // input laywer's name
    // click search btn
    

    // scrape laywer's info
    // save to file
    // click hp btn
    }
});

casper.run();
