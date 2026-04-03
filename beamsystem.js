const beamSessions = {};

function startBeam(message, opponent) {
  const channelId = message.channel.id;

  beamSessions[channelId] = {
    player1: { id: message.author.id, energy: 50, lastAction: 0 },
    player2: { id: opponent.id, energy: 50, lastAction: 0 },
    beamPosition: 0,
    momentum: 1,
    active: true,
  };

  message.channel.send("⚡ Lets use every last drop. ⚡");
}

module.exports = { beamSessions, startBeam };
