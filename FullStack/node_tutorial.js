const { clear } = require("console");

var time = 10;
const time_original = time;

const interval = setInterval(() => {
    console.log(time);
    time = time-1;
}, 1000);

setTimeout(()=>{
    clearInterval(interval);
    console.log("Reminder");
}, 6000)