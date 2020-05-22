const Discord = require("discord.js");
const config = require('./../../../../../config.js');

module.exports = {
    name: "about",
    aliases: ["about"],
    category: "info",
    description: "Returns About Section",
    run: async (client, message, args) => {
        const embed = new Discord.RichEmbed()
            .setAuthor(client.user.username, client.user.avatarURL) 
            .setDescription(`:smirk: **${client.user.username}** by GreyingError#2410, serving ${client.users.size} beautiful White Christians.
                    Need help? :confused: Try **${config.rprefix}help** for commands. \n`, true)            
            .addField("If Owner", `**${config.aprefix}help** \n`, true)  
            .setFooter(`${client.user.username} v${config.version}`)
            .setColor(0xf1d302)

        message.channel.send(embed);
    }
}
