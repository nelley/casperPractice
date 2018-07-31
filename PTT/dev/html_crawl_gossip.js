var AnchorArrays = [];
var fs = require('fs');


var casper = require('casper').create({
    verbose: true,
    logLevel: 'debug',
    viewportSize: {width:1280, height:3000}
});

function getRandomIntFromRange(min, max) {
  return Math.round(Math.random() * (max - min)) + min;
}

function getAllPage(){
    casper.echo("START")
    AnchorArrays = this.getElementsAttribute('#main-container > div.r-list-container.bbs-screen > div > div.title > a', 'href');
    fs.write("gossiping_list.csv", AnchorArrays + ',', 'a'); 

    //require('utils').dump(AnchorArrays);
    var ranInt = getRandomIntFromRange(1000, 5000);
    casper.echo(ranInt);
    casper.wait(ranInt);
    
    var nextLink = "#action-bar-container > div > div.btn-group.btn-group-paging > a:nth-child(2)";

    if (casper.visible(nextLink)) {
        casper.thenClick(nextLink);
        casper.then(getAllPage);
    } else {
        casper.echo("END");
    }
}

casper.start('https://www.ptt.cc/bbs/Gossiping/index.html', function(){
    var over18check = "div.over18-button-container:nth-child(2) > button:nth-child(1)"
    if(this.visible(over18check)){
        this.thenClick(over18check);
    }else{
        casper.echo('over 18 check failed!!');
    }
});

casper.then(getAllPage);

casper.run();



