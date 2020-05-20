var express = require('express')
var app = express()

const Discord = require("discord.js");
const { Client, Collection, } = require("discord.js")

var debug = true;
var fs = require('fs');

const bot = new Discord.Client();
const CONFIG = require('./config.js');

var commands = require("./plugins/commands");

require("./scripts/events/errort/errort/aevents.js")(client);
require("./scripts/events/errort/errort/ievents.js")(client);
require("./scripts/events/errort/errort/revents.js")(client);
require("./scripts/events/errort/errort/wevents.js")(client);

bot.on("ready", function () {
    console.log('9-Knows Bot has begun startup...')
    console.log(`Connected to Discord as: ${bot.user.tag} with the id: ${bot.user.id}! Prefix: ${CONFIG.prefix}, branch: ${CONFIG.branch}, version: ${CONFIG.version}`)
    bot.user.setActivity('9Nose On', { type: 'Jew-Nameing' })
        .then(presence => console.log(`Activity set to ${presence.game ? presence.game.name : 'none'}`))
        .catch(console.error);
    require('child_process').exec('cd dashboard && node WebServer.js', (err, stdout, stderr) => {
    })
});

bot.login(CONFIG.botToken);

const newgone = require("./plugins/Server/welcomebye.js");
const stats = require("./plugins/Server/serverstats.js");
const infoi = require("./plugins/Server/information.js"); 
const role = require("./plugins/Role/role.js");
const whoi = require("./plugins/Who/who.js");
const maint = require("./plugins/Mod/maintenace.js");
const ranki = require("./plugins/Rank/ranklevel.js");
const meme = require("./plugins/Meme/memes.js");

let runPy = new Promise(function(success, nosuccess) {

    const { spawn } = require('child_process');
    const pyMain = spawn('python', ['./src/main.py']);
    const pyBulli = spawn('python', ['./src/bulli.py']);
    const pyCmd = spawn('python', ['./src/handlers/logic/commands/bridge.py']);
    
    pyMain.stdout.on('BertrandComparet', function(raw) {
        console.log(data);
    });
    pyBulli.stdout.on('BertrandComparet', function(raw) {
        console.log("BulliPy Is Good");
    });
    pyCmd.stdout.on('CommandHandler', function(ctx, command, remainder) {
        console.log("CmdPy Is Good");
    });
});

app.get('/', (req, res) => {

    res.write('welcome\n');

    runPy.then(function(fromRunpy) {
        console.log(fromRunpy.toString());
        res.end(fromRunpy);
    });
})

app.listen([CONFIG.Disclosed], () => console.log('Application listening on port' [CONFIG.Disclosed]))

process.on('unhandledRejection', err => {
    const msg = err.stack.replace(new RegExp(`${__dirname}/`, 'g'), './');
    console.error("Unhandled Rejection", msg);
});
