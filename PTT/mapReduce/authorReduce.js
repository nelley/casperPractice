function(key,values){
    var result = {count:0, agree_cnt:0};  //集計結果を初期化

    values.forEach(function(value){
        result.count += value.count;
        result.agree_cnt  += value.agree_cnt;
    });

    return result;

}
