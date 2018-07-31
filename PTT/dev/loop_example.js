var AnchorArrays = [];
var page_num_index = 0;

var casper = require('casper').create({
    verbose: true,
    logLevel: 'info',
    viewportSize: {width:1280, height:3000}
});

casper.on('page_access', function(){
    //アクセスするページのURLを取得済みのリンク一覧配列から取り出す
    var access_page_url = AnchorArrays[page_num_index];
    var cp = require('child_process');
     
    //ニュースのN番目に遷移
    this.open('https://www.ptt.cc'+access_page_url).then(function() {
        page_num_index++;
        //画面のキャプチャを撮る
        this.capture('news_'+page_num_index+'.png');
        //ニュースのリンク一覧数分繰り返す
        if(page_num_index<AnchorArrays.length){
        //カスタムイベントpage_accessを発行する
            casper.emit('page_access');                                                                                  
        }
    });
});

//指定のURLへ遷移する
casper.start('https://www.ptt.cc/bbs/Tech_Job/index.html', function() {
    this.log('[FRONTEO]Logic Start', 'debug');
    //画面のキャプチャを取得
    //this.capture('ptt_tech_job.png');
    AnchorArrays = this.getElementsAttribute('#main-container > div.r-list-container.bbs-screen > div > div.title > a', 'href');
   //取得した内容を表示する
    this.log('[FRONTEO]casper start finished', 'debug');
    //var nextPage = this.getElementsAttribute('#action-bar-container > div > div.btn-group.btn-group-paging > a:nth-child(2)', 'href');
 
});
casper.then(function(){
    require('utils').dump(AnchorArrays);
    if(AnchorArrays.length > 0){
        casper.emit('page_access');
    }
    
    this.log('[FRONTEO]casper then end');
});


         
//処理の実行
casper.run();
