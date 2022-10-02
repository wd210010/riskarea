tt = new Date('2022-10-01')
console.log(tt)

function formatDate(date){
    var y = date.getFullYear();
    var m = date.getMonth() + 1;
    m = m < 10 ? '0' + m : m;
    var d = date.getDate();
    d = d < 10 ? ('0' + d) : d;
    return y + '-' + m + '-' + d;
}
predate = formatDate(new Date(tt.getTime() - 24*60*60*1000))
console.log(predate)
//predate = predate.toString()
// predate = predate.slice(0,9)
// Date.prototype.format = function(format)
// {
//     var o = {
//         "M+" : this.getMonth()+1, //month
//         "d+" : this.getDate(),    //day
//         "h+" : this.getHours(),   //hour
//         "m+" : this.getMinutes(), //minute
//         "s+" : this.getSeconds(), //second
//         "q+" : Math.floor((this.getMonth()+3)/3),  //quarter
//         "S" : this.getMilliseconds() //millisecond
//     }
//     if(/(y+)/.test(format)) format=format.replace(RegExp.$1,
//         (this.getFullYear()+"").substr(4 - RegExp.$1.length));
//     for(var k in o)if(new RegExp("("+ k +")").test(format))
//         format = format.replace(RegExp.$1,
//             RegExp.$1.length==1 ? o[k] :
//                 ("00"+ o[k]).substr((""+ o[k]).length));
//     return format;
// }

//console.log(predate)


// var date1 = new Date().format('yyyy-MM-dd');
