const { getMember } = require("../../../whoisf/functions/whois.js")
const { RichEmbed } = require("discord.js");

module.exports = {
    name: "serverinfo",
    aliases: ["server"],
    category: "info",
    description: "Displays server info",
    run: async (client, message, args) => {
        const member = getMember(message, args.join(" "));
        const roleColor = message.guild.me.displayHexColor === "#000000" ? "#ffffff" : message.guild.me.displayHexColor;
        
        function checkDays(date) {
            let now = new Date();
            let diff = now.getTime() - date.getTime();
            let days = Math.floor(diff / 86400000);
            return days + (days == 1 ? " day" : " days") + " ago";
        };

        let region = {
            "brazil": ":flag_br: Brazil",
            "eu-central": ":flag_eu: Central Europe",
            "singapore": ":flag_sg: Singapore",
            "us-central": ":flag_us: U.S. Central",
            "sydney": ":flag_au: Sydney",
            "us-east": ":flag_us: U.S. East",
            "us-south": ":flag_us: U.S. South",
            "us-west": ":flag_us: U.S. West",
            "eu-west": ":flag_eu: Western Europe",
            "vip-us-east": ":flag_us: VIP U.S. East",
            "london": ":flag_gb: London",
            "amsterdam": ":flag_nl: Amsterdam",
            "hongkong": ":flag_hk: Hong Kong",
            "russia": ":flag_ru: Russia",
            "southafrica": ":flag_za:  South Africa"
        };

        const embed = new RichEmbed()
            .setColor(roleColor)
            .addField("Owner", `${message.guild.owner.user.username}#${message.guild.owner.user.discriminator}`, true)
            .addField("Region", region[message.guild.region], true)
            .addField("Total | Humans | Bots", `${message.guild.members.size} | ${message.guild.members.filter(member => !member.user.bot).size} | ${message.guild.members.filter(member => member.user.bot).size}`, true)
            .addField("Channels", message.guild.channels.size, true)
            .addField("Creation Date", `${message.channel.guild.createdAt.toUTCString().substr(0, 16)} (${checkDays(message.channel.guild.createdAt)})`, true)
            .setThumbnail(message.guild.iconURL)
            .setColor(member.displayHexColor === "#000000" ? "#ffffff" : member.displayHexColor)
            .setDescription(args.slice(1).join(" "))
            .setTimestamp()
            .setAuthor(message.guild.name)
            .setFooter(client.user.username, client.user.displayAvatarURL)
            message.channel.send(embed);
    }
}
