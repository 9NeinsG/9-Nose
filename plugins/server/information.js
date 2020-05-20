
const { Client, Collection } = require("discord.js")
const { config } = require("dotenv");
const fs = require("fs")
const CONFIG = require('./../../config.js');

const client = new Client({
    disableEveryone: true
});

client.commands = new Collection();
client.aliases = new Collection();

client.categories = fs.readdirSync("./plugins/Server/info/commands/")

config({
    path: __dirname + "/.env"
});

["command"].forEach(handler => {
    require(`./info/handler/${handler}`)(client);
});

client.on("message", async (message) => {

    if(message.author.bot) return;

    if(!message.guild) return;

    if(!message.content.startsWith(CONFIG.iprefix)) return;

    if(!message.member) message.member = await message.guild.fetchMember(message);
        if (!message.member) message.member.endsWith("-T", "-G", "-E");
            message.delete();


    const args = message.content.slice(CONFIG.iprefix.length).trim().split(/ +/g);
    const cmd = args.shift().toLowerCase();

    if (cmd.length === 0) return;

    let command = client.commands.get(cmd)
    if (!command) command = client.commands.get(client.aliases.get(cmd));

    if (command)
        command.run(client, message, args);

});

client.login(CONFIG.botToken);
console.log('9-Info is online');
