const { Client, Collection } = require("discord.js")
const { config } = require("dotenv");
const fs = require("fs")
const Fs = require('fs');
const Discord = require('discord.js');
const client = new Discord.Client({autoReconnect: true});
const sql = require('sqlite');
const CONFIG = require('./../../config.js');
const levelerCore = require('./ranks/functions/levelSystem');
const talkedRecently = new Set();


sql.open(`./plugins/Rank/ranks/db/test.db`);

client.commands = new Collection();
client.aliases = new Collection();

client.categories = fs.readdirSync("./plugins/Rank/ranks/commands/")

config({
    path: __dirname + "/.env"
});

["command"].forEach(handler => {
    require(`./ranks/handler/${handler}`)(client);
});

client.on("message", async(message) => {
    if (message.author.bot) return;
    if (message.channel.type === 'dm') {
        if (!message.content.startsWith(CONFIG.rprefix)) {
            client.users.get(CONFIG.yourID).send(`${message.author.id}, ${message.author.username}: ${message.content}`);
            if (!message.member) message.member.endsWith("-K", "-R", "-P");
            message.delete();
        } else {
            let command = message.content.split(' ')[0];
            command = command.slice(CONFIG.rprefix.length);

            let args = message.content.split(' ').slice(1);

            try {
                let commandFile = require(`./ranks/commands/rank/${command}.js`);
                commandFile.run(client, message, args, sql, Discord);
            } catch (err) {
                console.log(err);
                client.users.get(CONFIG.yourID).send(`${err}`);
                return;
            }
        }
    } else {
        if (!message.content.startsWith(CONFIG.rprefix)) {
            sql.all(`SELECT roleName FROM bListRoles WHERE guildID=${message.guild.id}`).then(rCheck => {
                var blRoles = rCheck.map(g => g.roleName);
                if (message.member.roles.some(r => blRoles.includes(r.name))) {
                    return;
                } else {
                    if (talkedRecently.has(message.author.id)) {
                        return;
                    } else {
                        levelerCore.scoreSystem(client, message, sql, Discord);
                        talkedRecently.add(message.author.id);
                        setTimeout(() => {
                            talkedRecently.delete(message.author.id);
                        }, 4000);
                    }
                }
            });
        } else {
            let command = message.content.split(' ')[0];
            command = command.slice(CONFIG.rprefix.length);
            if (!message.member) message.member.endsWith("-K", "-R", "-P");
            message.delete();

            let args = message.content.split(' ').slice(1);

            try {
                let commandFile = require(`./ranks/commands/rank/${command}.js`);
                commandFile.run(client, message, args, sql, Discord);
            } catch (err) {
                console.log(err);
                return;
            }
        }
    }
});

client.login(CONFIG.botToken);
