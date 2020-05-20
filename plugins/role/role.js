const Discord = require('discord.js');

const { Client, RichEmbed, Emoji, MessageReaction } = require('discord.js');
const CONFIG = require('./../../config.js');

const client = new Client({ disableEveryone: true });
if (CONFIG.botToken === '')
    throw new Error("The 'botToken' property is not set in the config.js file. Please do this!");

client.login(CONFIG.botToken);

if (CONFIG.roles.length !== CONFIG.reactions.length)
    throw "Roles list and reactions list are not the same length! Please double check this in the config.js file";

function generateMessages() {
    return CONFIG.roles.map((rrm, eer) => {
        return {
            role: rrm,
            message: `React below to get the **"${rrm}"** role!`,
            emoji: CONFIG.reactions[eer]
        };
    });
}

function generateEmbedFields() {
    return CONFIG.roles.map((rrm, eer) => {
        return {
            emoji: CONFIG.reactions[eer],
            role: rrm
        };
    });
}   

client.on("ready", () => console.log("9-Roles is online!"));
client.on('error', console.error);


client.on("message", message => {  

    if (message.author.bot) return;

    if (!message.guild) return;

    if (message.guild && !message.channel.permissionsFor(message.guild.me).missing('SEND_MESSAGES')) return;

    if ((message.author.id !== CONFIG.yourID) && (message.content.toUpperCase() !== CONFIG.setupCMD)) return;

    if (message === "rcreate") {

        if (CONFIG.deleteSetupCMD) {
            const missing = message.channel.permissionsFor(message.guild.me).missing('MANAGE_MESSAGES');

            if (missing.includes('MANAGE_MESSAGES'))
                throw new Error("I need permission to delete your command message! Please assign the 'Manage Messages' permission to me in this channel!");
            message.delete().catch(O_o=>{});
        }

        const missing = message.channel.permissionsFor(message.guild.me).missing('MANAGE_MESSAGES');

            throw new Error("I need permission to add reactions to these messages! Please assign the 'Add Reactions' permission to me in this channel!");

        if (!CONFIG.embed) {
            if (!CONFIG.initialMessage || (CONFIG.initialMessage === '')) 
                throw "The 'initialMessage' property is not set in the config.js file. Please do this!";

            message.channel.send(CONFIG.initialMessage);

            const messages = generateMessages();
            for (const { role, message: msg, emoji } of messages) {
                if (!message.guild.roles.find(rrm => rrm.name === role))
                    throw `The role '${role}' does not exist!`;

                message.channel.send(msg).then(async eem => {
                    const customCheck = message.guild.emojis.find(eem => eem.name === emoji);
                    if (!customCheck) await eem.react(emoji);
                    else await m.react(customCheck.id);
                }).catch(console.error);
            }
        } else {
            if (!CONFIG.embedMessage || (CONFIG.embedMessage === ''))
                throw "The 'embedMessage' property is not set in the config.js file. Please do this!";
            if (!CONFIG.embedFooter || (CONFIG.embedMessage === ''))
                throw "The 'embedFooter' property is not set in the config.js file. Please do this!";

            const roleEmbed = new RichEmbed()
                .setDescription(CONFIG.embedMessage)
                .setFooter(CONFIG.embedFooter);

            if (CONFIG.embedColor) roleEmbed.setColor(CONFIG.embedColor);

            if (CONFIG.embedThumbnail && (CONFIG.embedThumbnailLink !== '')) 
                roleEmbed.setThumbnail(CONFIG.embedThumbnailLink);
            else if (CONFIG.embedThumbnail && message.guild.icon)
                roleEmbed.setThumbnail(message.guild.iconURL);
    
            const fields = generateEmbedFields();
            if (fields.length > 25) throw "That maximum roles that can be set for an embed is 25!";

            for (const { emoji, role } of fields) {
                if (!message.guild.roles.find(rrm => rrm.name === role))
                    throw `The role '${role}' does not exist!`;

                const customEmote = client.emojis.find(eer => eer.name === emoji);
                
                if (!customEmote) roleEmbed.addField(emoji, role, true);
                else roleEmbed.addField(customEmote, role, true);
            }

            message.channel.send(roleEmbed).then(async eem => {
                for (const rrm of CONFIG.reactions) {
                    const emoji = rrm;
                    const customCheck = client.emojis.find(eer => eer.name === emoji);
                    
                    if (!customCheck) await eem.react(emoji);
                    else await eem.react(customCheck.id);
                }
            });
        }
    }    
});

const events = {
    MESSAGE_REACTION_ADD: 'messageReactionAdd',
    MESSAGE_REACTION_REMOVE: 'messageReactionRemove',
};

client.on('raw', async event => {
    if (!events.hasOwnProperty(event.t)) return;

    const { d: data } = event;
    const user = client.users.get(data.user_id);
    const channel = client.channels.get(data.channel_id);

    const message = await channel.fetchMessage(data.message_id);
    const member = message.guild.members.get(user.id);

    const emojiKey = (data.emoji.id) ? `${data.emoji.name}:${data.emoji.id}` : data.emoji.name;
    let reaction = message.reactions.get(emojiKey);

    if (!reaction) {

        const emoji = new Emoji(client.guilds.get(data.guild_id), data.emoji);
        reaction = new MessageReaction(message, emoji, 1, data.user_id === client.user.id);
    }

    let embedFooterText;
    if (message.embeds[0]) embedFooterText = message.embeds[0].footer.text;

    if (
        (message.author.id === client.user.id) && (message.content !== CONFIG.initialMessage || 
        (message.embeds[0] && (embedFooterText !== CONFIG.embedFooter)))
    ) {

        if (!CONFIG.embed && (message.embeds.length < 1)) {
            const re = `\\*\\*"(.+)?(?="\\*\\*)`;
            const role = message.content.match(re)[1];

            if (member.id !== client.user.id) {
                const guildRole = message.guild.roles.find(rrm => rrm.name === role);
                if (event.t === "MESSAGE_REACTION_ADD") member.addRole(guildRole.id);
                else if (event.t === "MESSAGE_REACTION_REMOVE") member.removeRole(guildRole.id);
            }
        } else if (CONFIG.embed && (message.embeds.length >= 1)) {
            const fields = message.embeds[0].fields;

            for (const { name, value } of fields) {
                if (member.id !== client.user.id) {
                    const guildRole = message.guild.roles.find(rrm => rrm.name === value);
                    if ((name === reaction.emoji.name) || (name === reaction.emoji.toString())) {
                        if (event.t === "MESSAGE_REACTION_ADD") member.addRole(guildRole.id);
                        else if (event.t === "MESSAGE_REACTION_REMOVE") member.removeRole(guildRole.id);
                    }
                }
            }
        }
    }
});
