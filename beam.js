// commands/beam.js
const { startBeam } = require("../systems/beamSystem");

module.exports = {
  name: "beam",
  async execute(message, args) {
    const opponent = message.mentions.users.first();
    if (!opponent) return message.reply("Mention someone.");

    startBeam(message, opponent);
  },
};
