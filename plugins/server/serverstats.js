const Discord = require("discord.js");
const client = new Discord.Client();
const CONFIG = require('./../../config.js');

const Console = console;

client.on("9stats", () => {

    if (client.guilds.size < 1) {
        Console.log("The bot is not in any guild.");
        process.exit(0);
        return;
    }
    const text = `
______________________________
Ready since: ${moment(Date.now()).format("dddd, MMMM do YYYY, HH:mm:ss")}
Server: ${client.guilds.first().name}
Total server members: ${client.guilds.first().memberCount}
Credits: https://www.Nineneins.com/
______________________________
`; 
    Console.log("9-Stats is online!");
});

client.on("guildMemberAdd", (member) => {

        try {
            member.guild.channels.get(CONFIG.total).setName(`Total Members: ${member.guild.memberCount}`);
            member.guild.channels.get(CONFIG.users).setName(`Users: ${member.guild.members.filter((m) => !m.user.bot).size}`); 
            member.guild.channels.get(CONFIG.bots).setName(`Bots: ${member.guild.members.filter((m) => m.user.bot).size}`);
        
        }
        catch (e) {
        console.log('9-Welcome NewMember');
        Console.log(e);
        }
  });
client.on("guildMemberRemove", (member) => {
 
        try {
            member.guild.channels.get(CONFIG.total).setName(`Total Members: ${member.guild.memberCount}`); 
            member.guild.channels.get(CONFIG.users).setName(`Users: ${member.guild.members.filter((m) => !m.user.bot).size}`); 
            member.guild.channels.get(CONFIG.bots).setName(`Bots: ${member.guild.members.filter((m) => m.user.bot).size}`);
        
        }
        catch (e) {
        console.log('9-Oven Blazing');
        Console.log(e);
        }
});

client.login(CONFIG.botToken);
