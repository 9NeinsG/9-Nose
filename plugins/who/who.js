
const { Client, Collection } = require("discord.js")
const { config } = require("dotenv");
const fs = require("fs")
const CONFIG = require('./../../config.js');
const Discord = require('discord.js');
const sql = require('sqlite');

const client = new Client({
    disableEveryone: true
});

client.commands = new Collection();
client.aliases = new Collection();

client.categories = fs.readdirSync("./plugins/Who/whoisf/commands/")

config({
    path: __dirname + "/.env"
});

["command"].forEach(handler => {
    require(`./whoisf/handler/${handler}`)(client);
});

client.on("message", async (message) => {

    if(message.author.bot) return;

    if(!message.guild) return;

    if(!message.content.startsWith(CONFIG.wprefix)) return;

    if(!message.member) message.member = await message.guild.fetchMember(message);
        if (!message.member) message.member.endsWith("-O", "-R", "-S", "-V");
            message.delete();

    const args = message.content.slice(CONFIG.wprefix.length).trim().split(/ +/g);
    const cmd = args.shift().toLowerCase();

    if (cmd.length === 0) return;

    let command = client.commands.get(cmd)
    if (!command) command = client.commands.get(client.aliases.get(cmd));

    if (command)
        command.run(client, message, args);
});

client.login(CONFIG.botToken);
console.log('9-Who is online');
