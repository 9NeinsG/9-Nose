const Discord = require("discord.js");
const bot = new Discord.Client();
const CONFIG = require('./../../config.js');

bot.on("guildMemberAdd", (member) => 
{
    console.log(`9New Added.`);
    messageToSend = "Welcome " + member.user + " to 9Neins! Please see Rules & Get Roles to Chat.";
    bot.channels.get(CONFIG.welcome).send(messageToSend);
});

bot.on("guildMemberRemove", (member) => 
{
    console.log(`9Left Removed`);
    messageToSend = member.user.username + " has been tossed in the oven.";
    bot.channels.get(CONFIG.byebye).send(messageToSend);
});  

bot.login(CONFIG.botToken);
