const { RichEmbed } = require("discord.js");

module.exports = {
    name: "source",
    aliases: ["opensource", "code"],
    category: "info",
    description: "9-Nose Bot",
    run: async (client, message, args) => {
        const embed = new RichEmbed()
            .setTitle('Source code')    
            .setThumbnail('https://avatars0.githubusercontent.com/u/44002584?s=460&v=4')
            .setDescription(`The Bots Code:\nhttps://github.com/9NeinsG/9-Nose\n`, true)            
            .setTimestamp()

            message.channel.send(embed);
    }
}
