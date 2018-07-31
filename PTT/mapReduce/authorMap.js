function authorMap(){
    emit(this.author, {count:1, agree_cnt: this.agree_cnt});
};
