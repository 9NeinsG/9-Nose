const { getMember, formatTime, formatDate } = require("./../../../../Zscripts/functions.js")
const { RichEmbed } = require("discord.js");
const { stripIndents } = require("common-tags")

module.exports = {
    name: "uptime",
    aliases: ["status", "runtime"],
    category: "info",
    description: "Displays bot uptime information",
    run: async (client, message, args) => {
        const member = getMember(message, args.join(" "));    

        let totalSeconds = (client.uptime / 1000);
        let days = Math.floor(totalSeconds / 86400);
        let hours = Math.floor(totalSeconds / 3600) % 24;
        totalSeconds %= 3600;
        let minutes = Math.floor(totalSeconds / 60);

        const date = formatDate(client.readyTimestamp);
        const time = formatTime(client.readyTimestamp)

        const embed = new RichEmbed()
            .setThumbnail(message.guild.iconURL)
            .setColor(member.displayHexColor === "#000000" ? "#ffffff" : member.displayHexColor)
            .addField('Bot uptime', stripIndents`${days} day(s)
                ${hours} hour(s)
                ${minutes} minute(s) `, true)
            .addField('Bot started', stripIndents`${time} CST
                ${date}`, true)
            .setTimestamp()
            message.channel.send(embed);
    }
}
